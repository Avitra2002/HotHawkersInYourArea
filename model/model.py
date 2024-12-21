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
        confidence: float = 0.3,
        sample_interval: int = 60,  # 5 minutes in seconds
        output_folder: str = "output"
    ):
        self.source_video_path = source_video_path
        self.model = YOLO(weights)
        self.confidence = confidence
        self.sample_interval = sample_interval
        self.output_folder = output_folder
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Initialize video info and frame generator
        self.video_info = sv.VideoInfo.from_video_path(source_video_path)
        self.frames_generator = sv.get_video_frames_generator(source_video_path)
        
        # Initialize zones
        self.zones = [
            sv.PolygonZone(
                polygon=np.array(polygon, np.int32),
                triggering_anchors=(sv.Position.CENTER,)
            )
            for polygon in zones_config
        ]
        
        # Initialize tracker
        self.tracker = sv.ByteTrack()
        
        # Initialize annotators
        # Colors for different zones (10 zones total: 4 queues + 6 seating)
        self.colors = sv.ColorPalette.from_hex([
            "#E6194B",  # Red for Queue 1
            "#3CB44B",  # Green for Queue 2
            "#FFE119",  # Yellow for Queue 3
            # "#4363D8",  # Blue for Queue 4
            "#F58231",  # Orange for Seating 1
            "#911EB4",  # Purple for Seating 2
            # "#42D4F4",  # Cyan for Seating 3
            # "#F032E6",  # Magenta for Seating 4
            # "#BFEF45",  # Lime for Seating 5
            # "#FABEBE",  # Pink for Seating 6
        ])
        
        # Zone labels
        # self.zone_labels = {
        #     0: "Queue - Western",
        #     1: "Queue - Asian",
        #     2: "Queue - Indian",
        #     3: "Queue - Drinks",
        #     4: "Seating - Main Hall",
        #     5: "Seating - Window Area",
        #     6: "Seating - Corner",
        #     7: "Seating - Outdoor",
        #     8: "Seating - Private",
        #     9: "Seating - Extension"
        # }

        self.zone_labels = {
            0: "Queue - Chicken Rice",
            1: "Queue - Indian",
            2: "Queue - Taiwanese",
            3: "Seating - Alse 1",
            4: "Seating - Alse 2",
            5: "Seating - Alse 3"
        }

        self.box_annotator = sv.BoundingBoxAnnotator(color=self.colors)
        self.label_annotator = sv.LabelAnnotator(color=self.colors)
        self.zone_annotators = [
            sv.PolygonZoneAnnotator(
                zone=zone,
                color=self.colors.by_idx(idx),
                thickness=2,
                text_thickness=2,
                text_scale=1
            )
            for idx, zone in enumerate(self.zones)
        ]
        
        # Initialize timers for dwell time tracking
        self.timers = [FPSBasedTimer(self.video_info.fps) for _ in self.zones]
        
        # Storage for statistics
        self.zone_counts = {idx: [] for idx in range(len(self.zones))}
        self.dwell_times = {idx: {} for idx in range(len(self.zones))}
        
    def process_frame(self, frame: np.ndarray, frame_number: int) -> tuple:
        """Process a single frame and return statistics"""
        # Detect objects
        results = self.model(
            frame,
            verbose=False,
            device=self.device,
            conf=self.confidence
        )[0]
        
        # Get detections
        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.class_id == 0]  # Filter for persons only
        detections = self.tracker.update_with_detections(detections)
        
        stats = {}
        annotated_frame = frame.copy()
        
        # Process each zone
        for idx, (zone, timer) in enumerate(zip(self.zones, self.timers)):
            # Get detections in zone
            detections_in_zone = detections[zone.trigger(detections)]
            
            # Update dwell times
            times_in_zone = timer.tick(detections_in_zone)
            
            # Store statistics
            stats[f"zone_{idx}"] = {
                "count": len(detections_in_zone),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Update dwell times dictionary
            for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone):
                if tracker_id not in self.dwell_times[idx]:
                    self.dwell_times[idx][tracker_id] = time
                else:
                    self.dwell_times[idx][tracker_id] = max(
                        self.dwell_times[idx][tracker_id],
                        time
                    )
            
            # Annotate frame
            labels = [
                f"#{tracker_id} {int(time // 60):02d}:{int(time % 60):02d}"
                for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone)
            ]
            
            # Draw zone and detections
            # Create label with zone name and count
            zone_label = f"{self.zone_labels[idx]}: {len(detections_in_zone)}"
            if idx < 4:  # Queue areas
                zone_label += f" (Avg wait: {self.get_average_dwell_time(idx)})"
            else:  # Seating areas
                total_seats = self.get_zone_capacity(idx)
                zone_label += f" ({len(detections_in_zone)}/{total_seats} seats)"
            
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
    
    def analyze_video(self):
        """Main analysis loop"""
        # Set up video writer
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
            
            # Always process frame for visualization
            annotated_frame, stats = self.process_frame(frame, frame_count)
            
            # Save statistics at sample interval
            if last_sample_time is None or (current_time - last_sample_time) >= self.sample_interval:
                last_sample_time = current_time
                
                # Log statistics
                for zone_id, zone_stats in stats.items():
                    logger.info(
                        f"{zone_stats['timestamp']} - {zone_id}: "
                        f"Count={zone_stats['count']}"
                    )
                    self.zone_counts[int(zone_id.split('_')[1])].append({
                        'timestamp': zone_stats['timestamp'],
                        'count': zone_stats['count']
                    })
            
            video_writer.write(annotated_frame)
            frame_count += 1
        
        video_writer.release()
        self.save_statistics()
    
    def get_zone_capacity(self, zone_id: int) -> int:
        """Return the seating capacity for each seating zone"""
        # Define seating capacity for each seating area
        seating_capacity = {
            4: 100,  # Main Hall
            5: 50,   # Window Area
            6: 30,   # Corner
            7: 40,   # Outdoor
            8: 20,   # Private
            9: 60    # Extension
        }
        return seating_capacity.get(zone_id, 0)
    
    def get_average_dwell_time(self, zone_id: int) -> str:
        """Calculate and return average dwell time for a zone"""
        if zone_id not in self.dwell_times or not self.dwell_times[zone_id]:
            return "00:00"
        
        times = list(self.dwell_times[zone_id].values())
        avg_time = sum(times) / len(times)
        return f"{int(avg_time // 60):02d}:{int(avg_time % 60):02d}"

    def save_statistics(self):
        """Save statistics to separate CSV files for each zone"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create directories for different types of data
        count_dir = os.path.join(self.output_folder, "counts")
        dwell_dir = os.path.join(self.output_folder, "dwell_times")
        os.makedirs(count_dir, exist_ok=True)
        os.makedirs(dwell_dir, exist_ok=True)
        
        # Save zone counts for each zone
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
        
        # Save dwell times for each zone
        for zone_id, times in self.dwell_times.items():
            if zone_id < 4:  # Only save dwell times for queue areas
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
            writer.writerow(['Zone', 'Average Count', 'Maximum Count', 'Average Dwell Time'])
            
            for zone_id in range(len(self.zones)):
                avg_count = np.mean([c['count'] for c in self.zone_counts[zone_id]]) if self.zone_counts[zone_id] else 0
                max_count = max([c['count'] for c in self.zone_counts[zone_id]]) if self.zone_counts[zone_id] else 0
                
                if zone_id < 4:  # Queue areas
                    avg_dwell = self.get_average_dwell_time(zone_id)
                else:
                    avg_dwell = "N/A"
                
                writer.writerow([
                    self.zone_labels[zone_id],
                    round(avg_count, 2),
                    max_count,
                    avg_dwell
                ])
        
        logger.info(f"Saved summary statistics to {summary_path}")


def main():
    # Example zone configuration for all areas (adjust coordinates for your canteen)
    zones_config = [
        # Queue Areas
        [[233, 535], [243, 668], [277, 702], [546, 666], [529, 596], [529, 501], [228, 508]],  # Chicken Rice Queue
        [[529, 499], [726, 491], [728, 591], [823, 622], [554, 664], [520, 627]],  # Indian Food Queue
        [[740, 486], [884, 479], [886, 569], [942, 576], [757, 608]],  # Taiwanese Queue
    
        
        # Seating Areas
        [[8, 741], [284, 702], [714, 1071], [17, 1069]],  # Alse 1
        [[447, 722], [767, 639], [1643, 889], [1383, 1074], [1177, 1064]],  # Alse 2
        [[743, 632], [930, 586], [1699, 698], [1565, 838]], # Alse 3

    ]
    
    analyzer = CanteenAnalyzer(
        source_video_path="prototype_video.MOV",
        zones_config=zones_config,
        sample_interval=60  # 5 minutes
    )
    
    analyzer.analyze_video()

if __name__ == "__main__":
    main()