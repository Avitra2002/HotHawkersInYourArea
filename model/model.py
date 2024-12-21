import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import torch
import os
import csv
from datetime import datetime
import logging
from typing import List, Optional
from utils.general import find_in_list
from utils.timer import FPSBasedTimer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class CanteenAnalyzer:
    def __init__(
        self,
        source_video_path: str,
        zones_config: List[List[np.ndarray]],
        weights: str = "yolov8n.pt",
        confidence: float = 0.4,
        sample_interval: int = 120,
        output_folder: str = "output"
    ):
        self.source_video_path = source_video_path
        self.model = YOLO(weights)
        self.confidence = confidence
        self.sample_interval = sample_interval
        self.output_folder = output_folder
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        os.makedirs(output_folder, exist_ok=True)
        
        self.video_info = sv.VideoInfo.from_video_path(source_video_path)
        self.frames_generator = sv.get_video_frames_generator(source_video_path)
        
        self.zones = [
            sv.PolygonZone(
                polygon=np.array(polygon, np.int32),
                triggering_anchors=(sv.Position.CENTER,)
            )
            for polygon in zones_config
        ]
        
        self.tracker = sv.ByteTrack()
        
        self.colors = sv.ColorPalette.from_hex([
            "#E6194B",  # Red for Queue 1
            "#3CB44B",  # Green for Queue 2
            "#FFE119",  # Yellow for Queue 3
            "#F58231",  # Orange for Aisle 1
            "#911EB4",  # Purple for Aisle 2
            "#42D4F4",  # Cyan for Aisle 3
        ])
        
        self.zone_labels = {
            0: "Queue - Chicken Rice",
            1: "Queue - Indian",
            2: "Queue - Taiwanese",
            3: "Seating - Aisle 1",
            4: "Seating - Aisle 2",
            5: "Seating - Aisle 3"
        }

        self.box_annotator = sv.BoundingBoxAnnotator(color=self.colors)
        self.label_annotator = sv.LabelAnnotator(color=self.colors)
        self.zone_annotators = [
            sv.PolygonZoneAnnotator(
                zone=zone,
                color=self.colors.by_idx(idx),
                thickness=1,
                text_thickness=1,
                text_scale=1
            )
            for idx, zone in enumerate(self.zones)
        ]
        
        # Initialize timers only for queue zones (0, 1, 2)
        self.timers = [FPSBasedTimer(self.video_info.fps) if i < 3 else None for i in range(len(self.zones))]
        
        # Only store counts for Aisle zones (3, 4, 5)
        self.zone_counts = {idx: [] for idx in range(3, 6)}
        # Only store dwell times for queue zones (0, 1, 2)
        self.dwell_times = {idx: {} for idx in range(3)}
        
    def process_frame(self, frame: np.ndarray, frame_number: int) -> tuple:
        results = self.model(
            frame,
            verbose=False,
            device=self.device,
            conf=self.confidence
        )[0]
        
        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.class_id == 0]  # Filter for persons only
        detections = self.tracker.update_with_detections(detections)
        
        stats = {}
        annotated_frame = frame.copy()
        
        for idx, zone in enumerate(self.zones):
            detections_in_zone = detections[zone.trigger(detections)]
            
            if idx < 3:  # Queue zones - track dwell time
                times_in_zone = self.timers[idx].tick(detections_in_zone)
                # Update dwell times dictionary
                for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone):
                    if tracker_id not in self.dwell_times[idx]:
                        self.dwell_times[idx][tracker_id] = time
                    else:
                        self.dwell_times[idx][tracker_id] = max(
                            self.dwell_times[idx][tracker_id],
                            time
                        )
                labels = [
                    f"#{tracker_id} {int(time // 60):02d}:{int(time % 60):02d}"
                    for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone)
                ]
                zone_label = f"{self.zone_labels[idx]}: (Avg wait: {self.get_average_dwell_time(idx)})"
            else:  # Aisle zones - only track count
                labels = [f"#{tracker_id}" for tracker_id in detections_in_zone.tracker_id]
                total_seats = self.get_zone_capacity(idx)
                zone_label = f"{self.zone_labels[idx]}: {len(detections_in_zone)}/{total_seats} seats"
                stats[f"zone_{idx}"] = {
                    "count": len(detections_in_zone),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            annotated_frame = self.zone_annotators[idx].annotate(
                scene=annotated_frame,
                label=zone_label
            )
            annotated_frame = self.box_annotator.annotate(
                scene=annotated_frame,
                detections=detections_in_zone
            )
            annotated_frame = self.label_annotator.annotate(
                scene=annotated_frame,
                detections=detections_in_zone,
                labels=labels
            )
        
        return annotated_frame, stats
    
    def get_zone_capacity(self, zone_id: int) -> int:
        seating_capacity = {
            3: 6,   # Aisle 1
            4: 18,  # Aisle 2
            5: 18,  # Aisle 3
        }
        return seating_capacity.get(zone_id, 0)
    
    def get_average_dwell_time(self, zone_id: int) -> str:
        if zone_id >= 3 or zone_id not in self.dwell_times or not self.dwell_times[zone_id]:
            return "00:00"
        
        times = list(self.dwell_times[zone_id].values())
        avg_time = sum(times) / len(times)
        return f"{int(avg_time // 60):02d}:{int(avg_time % 60):02d}"

    def save_statistics(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        count_dir = os.path.join(self.output_folder, "counts")
        dwell_dir = os.path.join(self.output_folder, "dwell_times")
        os.makedirs(count_dir, exist_ok=True)
        os.makedirs(dwell_dir, exist_ok=True)
        
        # Save counts only for Aisle zones (3, 4, 5)
        for zone_id, counts in self.zone_counts.items():
            count_path = os.path.join(
                count_dir, 
                f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{timestamp}.csv"
            )
            with open(count_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Count'])
                for count_data in counts:
                    writer.writerow([
                        count_data['timestamp'],
                        count_data['count']
                    ])
            logger.info(f"Saved count data for {self.zone_labels[zone_id]} to {count_path}")
        
        # Save dwell times only for queue zones (0, 1, 2)
        for zone_id, times in self.dwell_times.items():
            dwell_path = os.path.join(
                dwell_dir,
                f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{timestamp}.csv"
            )
            with open(dwell_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Tracker ID', 'Dwell Time (mm:ss)', 'Total Seconds'])
                for tracker_id, time in times.items():
                    writer.writerow([
                        tracker_id,
                        f"{int(time // 60):02d}:{int(time % 60):02d}",
                        round(time, 2)
                    ])
            logger.info(f"Saved dwell time data for {self.zone_labels[zone_id]} to {dwell_path}")
        
        # Save summary statistics
        summary_path = os.path.join(self.output_folder, f"summary_{timestamp}.csv")
        with open(summary_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Zone', 'Count/Dwell Time'])
            
            # Write dwell times for queue zones
            for zone_id in range(3):
                writer.writerow([
                    self.zone_labels[zone_id],
                    self.get_average_dwell_time(zone_id)
                ])
            
            # Write counts for Aisle zones
            for zone_id in range(3, 6):
                avg_count = np.mean([c['count'] for c in self.zone_counts[zone_id]]) if self.zone_counts[zone_id] else 0
                writer.writerow([
                    self.zone_labels[zone_id],
                    f"Count: {round(avg_count, 2)}"
                ])
        
        logger.info(f"Saved summary statistics to {summary_path}")

    def analyze_video(self):
        output_video_path = os.path.join(self.output_folder, "annotated_video.mp4")
        video_writer = cv2.VideoWriter(
            output_video_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.video_info.fps,
            (self.video_info.width, self.video_info.height)
        )
        
        frame_count = 0
        last_sample_time = None
        
        for frame in self.frames_generator:
            current_time = frame_count / self.video_info.fps
            
            annotated_frame, stats = self.process_frame(frame, frame_count)
            
            if last_sample_time is None or (current_time - last_sample_time) >= self.sample_interval:
                last_sample_time = current_time
                
                # Only store counts for Aisle zones (3, 4, 5)
                for zone_id, zone_stats in stats.items():
                    zone_num = int(zone_id.split('_')[1])
                    if zone_num >= 3:  # Only for Aisle zones
                        logger.info(
                            f"{zone_stats['timestamp']} - {zone_id}: "
                            f"Count={zone_stats['count']}"
                        )
                        self.zone_counts[zone_num].append({
                            'timestamp': zone_stats['timestamp'],
                            'count': zone_stats['count']
                        })
            
            video_writer.write(annotated_frame)
            frame_count += 1
        
        video_writer.release()
        self.save_statistics()


def main():
    zones_config = [
        # Queue Areas
        [[208, 381], [227, 620], [519, 592], [511, 378]],  # Chicken Rice Queue
        [[522, 409], [531, 589], [730, 572], [727, 401]],  # Indian Food Queue
        [[735, 404], [735, 538], [749, 561], [884, 550], [884, 407]],  # Taiwanese Queue
        
        # Seating Areas
        [[14, 696], [281, 665], [676, 1066], [8, 1069]],  # Aisle 1
        [[424, 684], [688, 634], [1583, 864], [1311, 1063]],  # Aisle 2
        [[775, 620], [938, 583], [1681, 696], [1558, 822]], # Aisle 3
    ]
    
    analyzer = CanteenAnalyzer(
        source_video_path="prototype_video.mp4",
        zones_config=zones_config,
        sample_interval=120
    )
    
    analyzer.analyze_video()

if __name__ == "__main__":
    main()