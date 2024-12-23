# import cv2
# import numpy as np
# from ultralytics import YOLO
# import supervision as sv
# import torch
# import os
# import csv
# from datetime import datetime
# import logging
# from typing import List, Optional
# from utils.general import find_in_list
# from utils.timer import FPSBasedTimer
# from datetime import datetime, timedelta

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# class CanteenAnalyzer:
#     def __init__(
#         self,
#         source_video_path: str,
#         zones_config: List[List[np.ndarray]],
#         weights: str = "yolov8n.pt",
#         confidence: float = 0.4,
#         sample_interval: int = 120,
#         output_folder: str = "output"
#     ):
#         # Basic initialization remains the same
#         self.source_video_path = source_video_path
#         self.model = YOLO(weights)
#         self.confidence = confidence
#         self.sample_interval = sample_interval
#         self.output_folder = output_folder
#         self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
#         # Create timestamp for this run
#         self.run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
#         # Create output directories
#         self.count_dir = os.path.join(output_folder, "counts")
#         self.dwell_dir = os.path.join(output_folder, "dwell_times")
#         os.makedirs(self.count_dir, exist_ok=True)
#         os.makedirs(self.dwell_dir, exist_ok=True)
        
#         # Initialize base components
#         self.video_info = sv.VideoInfo.from_video_path(source_video_path)
#         self.frames_generator = sv.get_video_frames_generator(source_video_path)
#         self.tracker = sv.ByteTrack()
        
#         # Setup zones and visualization
#         self._setup_zones(zones_config)
#         self._setup_visualization()
        
#         # Initialize tracking components
#         self.timers = [FPSBasedTimer(self.video_info.fps) if i < 3 else None for i in range(len(self.zones))]
#         self.active_trackers = {idx: {} for idx in range(3)}  # Track active people in queues
#         self.zone_counts = {idx: [] for idx in range(3, 6)}  # Track counts in aisles
        
#         # Create CSV files with headers
#         self._initialize_csv_files()

#     def _setup_zones(self, zones_config: List[List[np.ndarray]]):
#         """Setup detection zones"""
#         self.zones = [
#             sv.PolygonZone(
#                 polygon=np.array(polygon, np.int32),
#                 triggering_anchors=(sv.Position.CENTER,)
#             )
#             for polygon in zones_config
#         ]

#     def _setup_visualization(self):
#         """Setup visualization components"""
#         self.colors = sv.ColorPalette.from_hex([
#             "#E6194B",  # Red for Queue 1
#             "#3CB44B",  # Green for Queue 2
#             "#FFE119",  # Yellow for Queue 3
#             "#F58231",  # Orange for Aisle 1
#             "#911EB4",  # Purple for Aisle 2
#             "#42D4F4",  # Cyan for Aisle 3
#         ])
        
#         self.zone_labels = {
#             0: "Queue - Chicken Rice",
#             1: "Queue - Indian",
#             2: "Queue - Taiwanese",
#             3: "Seating - Aisle 1",
#             4: "Seating - Aisle 2",
#             5: "Seating - Aisle 3"
#         }

#         self.box_annotator = sv.BoundingBoxAnnotator(color=self.colors)
#         self.label_annotator = sv.LabelAnnotator(color=self.colors)
#         self.zone_annotators = [
#             sv.PolygonZoneAnnotator(
#                 zone=zone,
#                 color=self.colors.by_idx(idx),
#                 thickness=1,
#                 text_thickness=1,
#                 text_scale=1
#             )
#             for idx, zone in enumerate(self.zones)
#         ]

#     def get_zone_capacity(self, zone_id: int) -> int:
#         """Return seating capacity for each zone"""
#         seating_capacity = {
#             3: 6,   # Aisle 1
#             4: 18,  # Aisle 2
#             5: 18   # Aisle 3
#         }
#         return seating_capacity.get(zone_id, 0)

#     def _initialize_csv_files(self):
#         """Initialize CSV files with headers"""
#         # Initialize dwell time CSVs for queue zones
#         for zone_id in range(3):
#             dwell_path = self._get_dwell_path(zone_id)
#             with open(dwell_path, 'w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(['Tracker ID', 'Entry Time', 'Exit Time', 'Dwell Time (mm:ss)', 'Total Seconds'])
        
#         # Initialize count CSVs for aisle zones
#         for zone_id in range(3, 6):
#             count_path = self._get_count_path(zone_id)
#             with open(count_path, 'w', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(['Timestamp', 'Count'])

#     def _get_dwell_path(self, zone_id: int) -> str:
#         """Get path for dwell time CSV file"""
#         return os.path.join(
#             self.dwell_dir,
#             f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{self.run_timestamp}.csv"
#         )

#     def _get_count_path(self, zone_id: int) -> str:
#         """Get path for count CSV file"""
#         return os.path.join(
#             self.count_dir,
#             f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{self.run_timestamp}.csv"
#         )

#     def _save_exit_record(self, zone_id: int, tracker_id: int, dwell_time: float):
#         """Save record when someone exits a queue zone"""
#         dwell_path = self._get_dwell_path(zone_id)
#         exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         entry_time = (datetime.now() - timedelta(seconds=dwell_time)).strftime('%Y-%m-%d %H:%M:%S')
        
#         with open(dwell_path, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([
#                 tracker_id,
#                 entry_time,
#                 exit_time,
#                 f"{int(dwell_time // 60):02d}:{int(dwell_time % 60):02d}",
#                 round(dwell_time, 2)
#             ])
#         logger.info(f"Person {tracker_id} exited {self.zone_labels[zone_id]} after {round(dwell_time, 2)} seconds")

#     def _save_count_record(self, zone_id: int, count: int, timestamp: str):
#         """Save count record for aisle zone"""
#         count_path = self._get_count_path(zone_id)
#         with open(count_path, 'a', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerow([timestamp, count])

#     def process_frame(self, frame: np.ndarray, frame_time: float) -> tuple:
#         results = self.model(frame, verbose=False, device=self.device, conf=self.confidence)[0]
#         detections = sv.Detections.from_ultralytics(results)
#         detections = detections[detections.class_id == 0]  # Filter for persons only
#         detections = self.tracker.update_with_detections(detections)
        
#         stats = {}
#         annotated_frame = frame.copy()
        
#         for idx, zone in enumerate(self.zones):
#             detections_in_zone = detections[zone.trigger(detections)]
            
#             if idx < 3:  # Queue zones
#                 # Get current trackers in zone
#                 current_trackers = set(detections_in_zone.tracker_id)
#                 existing_trackers = set(self.active_trackers[idx].keys())
                
#                 # Process exits
#                 exited_trackers = existing_trackers - current_trackers
#                 for tracker_id in exited_trackers:
#                     dwell_time = self.active_trackers[idx][tracker_id]
#                     self._save_exit_record(idx, tracker_id, dwell_time)
#                     del self.active_trackers[idx][tracker_id]
                
#                 # Update active trackers
#                 times_in_zone = self.timers[idx].tick(detections_in_zone)
#                 for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone):
#                     self.active_trackers[idx][tracker_id] = time
                
#                 # Create labels for visualization
#                 labels = [
#                     f"#{tracker_id} {int(time // 60):02d}:{int(time % 60):02d}"
#                     for tracker_id, time in zip(detections_in_zone.tracker_id, times_in_zone)
#                 ]
#                 zone_label = f"{self.zone_labels[idx]}: {len(detections_in_zone)}"
                
#             else:  # Aisle zones
#                 labels = [f"#{tracker_id}" for tracker_id in detections_in_zone.tracker_id]
#                 total_seats = self.get_zone_capacity(idx)
#                 count = len(detections_in_zone)
#                 zone_label = f"{self.zone_labels[idx]}: {count}/{total_seats} seats"
                
#                 stats[f"zone_{idx}"] = {
#                     "count": count,
#                     "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 }
            
#             # Annotate frame
#             annotated_frame = self.zone_annotators[idx].annotate(
#                 scene=annotated_frame,
#                 label=zone_label
#             )
#             annotated_frame = self.box_annotator.annotate(
#                 scene=annotated_frame,
#                 detections=detections_in_zone
#             )
#             annotated_frame = self.label_annotator.annotate(
#                 scene=annotated_frame,
#                 detections=detections_in_zone,
#                 labels=labels
#             )
        
#         return annotated_frame, stats

#     def analyze_video(self):
#         output_video_path = os.path.join(self.output_folder, "annotated_video.mp4")
#         video_writer = cv2.VideoWriter(
#             output_video_path,
#             cv2.VideoWriter_fourcc(*'mp4v'),
#             self.video_info.fps,
#             (self.video_info.width, self.video_info.height)
#         )
        
#         frame_count = 0
#         last_sample_time = None
        
#         for frame in self.frames_generator:
#             current_time = frame_count / self.video_info.fps
            
#             annotated_frame, stats = self.process_frame(frame, current_time)
            
#             # Save aisle counts at intervals
#             if last_sample_time is None or (current_time - last_sample_time) >= self.sample_interval:
#                 last_sample_time = current_time
                
#                 for zone_id, zone_stats in stats.items():
#                     zone_num = int(zone_id.split('_')[1])
#                     if zone_num >= 3:  # Only for Aisle zones
#                         self._save_count_record(
#                             zone_num,
#                             zone_stats['count'],
#                             zone_stats['timestamp']
#                         )
#                         logger.info(
#                             f"{zone_stats['timestamp']} - {self.zone_labels[zone_num]}: "
#                             f"Count={zone_stats['count']}"
#                         )
            
#             video_writer.write(annotated_frame)
#             frame_count += 1
            
#             # Print progress
#             if frame_count % 100 == 0:
#                 logger.info(f"Processed frame {frame_count}")
        
#         video_writer.release()


# def main():
#     zones_config = [
#         # Queue Areas
#         [[213, 412], [222, 567], [519, 550], [508, 401]],  # Chicken Rice Queue
#         [[522, 409], [531, 589], [730, 572], [727, 401]],  # Indian Food Queue
#         [[735, 404], [735, 538], [749, 561], [884, 550], [884, 407]],  # Taiwanese Queue
        
#         # Seating Areas
#         [[14, 696], [281, 665], [676, 1066], [8, 1069]],  # Aisle 1
#         [[424, 684], [688, 634], [1583, 864], [1311, 1063]],  # Aisle 2
#         [[775, 620], [938, 583], [1681, 696], [1558, 822]], # Aisle 3
#     ]
    
#     analyzer = CanteenAnalyzer(
#         source_video_path="test.mov",
#         zones_config=zones_config,
#         sample_interval=40
#     )
    
#     analyzer.analyze_video()

# if __name__ == "__main__":
#     main()

import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import torch
import os
import csv
from datetime import datetime, timedelta
import logging
from typing import List, Optional
from utils.general import find_in_list
from utils.timer import FPSBasedTimer
import requests

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
        sample_interval: int = 30,
        output_folder: str = "output",
        position_threshold: float = 50.0,  # Max distance to consider same person
        time_threshold: int = 10,  # Frames to look back for matching
        min_dwell_time: float = 8.0,
        api_base_url: str = "http://10.32.4.205:5000"

    ):
        # Basic initialization
        self.source_video_path = source_video_path
        self.model = YOLO(weights)
        self.confidence = confidence
        self.sample_interval = sample_interval
        self.output_folder = output_folder
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.position_threshold = position_threshold
        self.time_threshold = time_threshold
        self.min_dwell_time = min_dwell_time
        self.api_base_url = api_base_url
        
        # Create timestamp for this run
        self.run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output directories
        self.count_dir = os.path.join(output_folder, "counts")
        self.dwell_dir = os.path.join(output_folder, "dwell_times")
        os.makedirs(self.count_dir, exist_ok=True)
        os.makedirs(self.dwell_dir, exist_ok=True)
        
        # Initialize video components
        self.video_info = sv.VideoInfo.from_video_path(source_video_path)
        self.frames_generator = sv.get_video_frames_generator(source_video_path)
        self.tracker = sv.ByteTrack()
        
        # Setup zones and visualization
        self._setup_zones(zones_config)
        self._setup_visualization()
        
        # Initialize tracking components
        self.timers = [FPSBasedTimer(self.video_info.fps) if i < 3 else None for i in range(len(self.zones))]
        self.active_trackers = {idx: {} for idx in range(3)}  # Track active people in queues
        self.zone_counts = {idx: [] for idx in range(3, 6)}  # Track counts in aisles
        self.tracker_history = {idx: {} for idx in range(3)}  # Position history
        self.frame_count = 0
        
        # Create CSV files with headers
        # self._initialize_csv_files()

    def _setup_zones(self, zones_config: List[List[np.ndarray]]):
        """Setup detection zones"""
        self.zones = [
            sv.PolygonZone(
                polygon=np.array(polygon, np.int32),
                triggering_anchors=(sv.Position.CENTER,)
            )
            for polygon in zones_config
        ]

    def _setup_visualization(self):
        """Setup visualization components"""
        self.colors = sv.ColorPalette.from_hex([
            "#E6194B",  # Red for Queue 1
            "#3CB44B",  # Green for Queue 2
            "#FFE119",  # Yellow for Queue 3
            "#F58231",  # Orange for Aisle 1
            "#911EB4",  # Purple for Aisle 2
            "#42D4F4",  # Cyan for Aisle 3
        ])
        
        self.zone_labels = {
            0: "Chicken Rice",
            1: "Indian",
            2: "Taiwanese",
            3: "Zone 1",
            4: "Zone 2",
            5: "Zone 3"
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

    # def _initialize_csv_files(self):
    #     """Initialize CSV files with headers"""
    #     # Initialize dwell time CSVs for queue zones
    #     for zone_id in range(3):
    #         dwell_path = self._get_dwell_path(zone_id)
    #         with open(dwell_path, 'w', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerow(['Tracker ID', 'Entry Time', 'Exit Time', 'Dwell Time (mm:ss)', 'Total Seconds'])
        
    #     # Initialize count CSVs for aisle zones
    #     for zone_id in range(3, 6):
    #         count_path = self._get_count_path(zone_id)
    #         with open(count_path, 'w', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerow(['Timestamp', 'Count'])

    # def _get_dwell_path(self, zone_id: int) -> str:
    #     """Get path for dwell time CSV file"""
    #     return os.path.join(
    #         self.dwell_dir,
    #         f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{self.run_timestamp}.csv"
    #     )

    # def _get_count_path(self, zone_id: int) -> str:
    #     """Get path for count CSV file"""
    #     return os.path.join(
    #         self.count_dir,
    #         f"{self.zone_labels[zone_id].replace(' - ', '_').lower()}_{self.run_timestamp}.csv"
    #     )

    def _calculate_distance(self, pos1, pos2):
        """Calculate Euclidean distance between two positions"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def _find_matching_tracker(self, zone_idx: int, current_pos, current_time):
        """Find the most likely previous tracker ID for a position"""
        best_match = None
        min_distance = float('inf')
        
        # Look through recent history of all trackers in this zone
        for tracker_id, history in self.tracker_history[zone_idx].items():
            if not history:
                continue
            
            # Only consider trackers that were active recently
            recent_history = [h for h in history if h['frame'] >= current_time - self.time_threshold]
            if not recent_history:
                continue
            
            # Get last known position
            last_pos = recent_history[-1]['position']
            distance = self._calculate_distance(current_pos, last_pos)
            
            # Update best match if this is closer
            if distance < min_distance and distance < self.position_threshold:
                min_distance = distance
                best_match = tracker_id
        
        return best_match
    
    def _send_dwell_time_data(self, zone_id: int, dwell_time: float, exit_time: str):
        dt = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
        formatted_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        """Send dwell time data to API endpoint"""
        payload = {
            "name": self.zone_labels[zone_id],
            # "dwell_time_seconds": round(dwell_time, 2),
            "dwell_time": f"{round(dwell_time/60,2)}",
            "timestamp": formatted_timestamp
        }
        
        try:
            response = requests.post(f"{self.api_base_url}/dwelltimes", json=payload)
            response.raise_for_status()
            # logger.info(f"Successfully sent dwell time data for tracker {tracker_id} in {self.zone_labels[zone_id]}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send dwell time data: {e}")

    def _send_count_data(self, zone_id: int, count: int, timestamp: str):
        """Send count data to API endpoint"""
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        formatted_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        payload = {
            "zone": self.zone_labels[zone_id], ##name of zone
            "count": count,
            "timestamp": formatted_timestamp,
            "capacity": self.get_zone_capacity(zone_id),
            "status": round((count/self.get_zone_capacity(zone_id))*100,2)

        }
        
        try:
            response = requests.post(f"{self.api_base_url}/counts", json=payload)
            response.raise_for_status()
            logger.info(f"Successfully sent count data for {self.zone_labels[zone_id]}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send count data: {e}")

    def _update_tracker_history(self, zone_idx: int, detections_in_zone: sv.Detections):
        """Update position history for all trackers"""
        current_positions = {}
        
        # Get current positions
        for tracker_id, bbox in zip(detections_in_zone.tracker_id, detections_in_zone.xyxy):
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            current_positions[tracker_id] = (center_x, center_y)
            
            # Initialize history if needed
            if tracker_id not in self.tracker_history[zone_idx]:
                self.tracker_history[zone_idx][tracker_id] = []
            
            # Add current position to history
            self.tracker_history[zone_idx][tracker_id].append({
                'position': (center_x, center_y),
                'frame': self.frame_count
            })
            
            # Keep only recent history
            self.tracker_history[zone_idx][tracker_id] = [
                h for h in self.tracker_history[zone_idx][tracker_id] 
                if h['frame'] >= self.frame_count - self.time_threshold
            ]

    def _save_exit_record(self, zone_id: int, tracker_id: int, dwell_time: float):
        """Save record when someone exits a queue zone"""
        if dwell_time < self.min_dwell_time:
            logger.debug(f"Skipping record for tracker {tracker_id} in {self.zone_labels[zone_id]} - dwell time {round(dwell_time, 2)}s < minimum {self.min_dwell_time}s")
            return
        
        # dwell_path = self._get_dwell_path(zone_id)
        exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry_time = (datetime.now() - timedelta(seconds=dwell_time)).strftime('%Y-%m-%d %H:%M:%S')
        
        # with open(dwell_path, 'a', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow([
        #         tracker_id,
        #         entry_time,
        #         exit_time,
        #         f"{int(dwell_time // 60):02d}:{int(dwell_time % 60):02d}",
        #         round(dwell_time, 2)
        #     ])
        self._send_dwell_time_data(
            zone_id=zone_id, ##store name
            # tracker_id=tracker_id,
            # entry_time=entry_time,
            exit_time=exit_time,
            dwell_time=dwell_time
        )
        logger.info(f"Person {tracker_id} exited {self.zone_labels[zone_id]} after {round(dwell_time, 2)} seconds")

    def _save_count_record(self, zone_id: int, count: int, timestamp: str):
        """Save count record for aisle zone"""
        # count_path = self._get_count_path(zone_id)
        # with open(count_path, 'a', newline='') as f:
        #     writer = csv.writer(f)
        #     writer.writerow([timestamp, count])
        self._send_count_data(zone_id, count, timestamp)


    def get_zone_capacity(self, zone_id: int) -> int:
        """Return seating capacity for each zone"""
        seating_capacity = {
            3: 6,   # Aisle 1
            4: 18,  # Aisle 2
            5: 18   # Aisle 3
        }
        return seating_capacity.get(zone_id, 0)

    def process_frame(self, frame: np.ndarray, frame_time: float) -> tuple:
        self.frame_count += 1
        results = self.model(frame, verbose=False, device=self.device, conf=self.confidence)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = detections[detections.class_id == 0]
        detections = self.tracker.update_with_detections(detections)
        
        stats = {}
        annotated_frame = frame.copy()
        
        for idx, zone in enumerate(self.zones):
            detections_in_zone = detections[zone.trigger(detections)]
            
            if idx < 3:  # Queue zones
                # Update position history
                self._update_tracker_history(idx, detections_in_zone)
                
                # Process each detection
                processed_detections = []
                processed_times = []
                
                for tracker_id, bbox in zip(detections_in_zone.tracker_id, detections_in_zone.xyxy):
                    current_pos = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                    
                    # Try to find matching previous tracker
                    matched_tracker = self._find_matching_tracker(idx, current_pos, self.frame_count)
                    
                    if matched_tracker and matched_tracker in self.active_trackers[idx]:
                        # Use the time from the matched tracker
                        dwell_time = self.active_trackers[idx][matched_tracker]
                        # Update the active tracker with new ID
                        if matched_tracker != tracker_id:
                            self.active_trackers[idx][tracker_id] = dwell_time
                            del self.active_trackers[idx][matched_tracker]
                            logger.debug(f"Maintained identity: {matched_tracker} -> {tracker_id}")
                    else:
                        # New tracker
                        dwell_time = 0
                    
                    processed_detections.append(tracker_id)
                    processed_times.append(dwell_time)
                
                # Update times using timer
                updated_times = self.timers[idx].tick(detections_in_zone)
                
                # Update active trackers
                for tracker_id, time in zip(processed_detections, updated_times):
                    self.active_trackers[idx][tracker_id] = time
                
                # Create labels for visualization
                labels = [
                    f"#{tracker_id} {int(time // 60):02d}:{int(time % 60):02d}"
                    for tracker_id, time in zip(processed_detections, updated_times)
                ]
                zone_label = f"{self.zone_labels[idx]}: {len(detections_in_zone)}"
                
                # Check for exits
                current_tracker_set = set(processed_detections)
                for tracker_id in list(self.active_trackers[idx].keys()):
                    if tracker_id not in current_tracker_set:
                        # Check if there's no nearby match before declaring exit
                        last_pos = self.tracker_history[idx].get(tracker_id, [{}])[-1].get('position')
                        if last_pos and not self._find_matching_tracker(idx, last_pos, self.frame_count):
                            dwell_time = self.active_trackers[idx][tracker_id]
                            self._save_exit_record(idx, tracker_id, dwell_time)
                            del self.active_trackers[idx][tracker_id]
            
            else:  # Aisle zones
                labels = [f"#{tracker_id}" for tracker_id in detections_in_zone.tracker_id]
                total_seats = self.get_zone_capacity(idx)
                count = len(detections_in_zone)
                zone_label = f"{self.zone_labels[idx]}: {count}/{total_seats} seats"
                
                stats[f"zone_{idx}"] = {
                    "count": count,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Annotate frame
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
            
            annotated_frame, stats = self.process_frame(frame, current_time)
            
            # Save aisle counts at intervals
            if last_sample_time is None or (current_time - last_sample_time) >= self.sample_interval:
                last_sample_time = current_time
                
                for zone_id, zone_stats in stats.items():
                    zone_num = int(zone_id.split('_')[1])
                    if zone_num >= 3:  # Only for Aisle zones
                        self._save_count_record(
                            zone_num,
                            zone_stats['count'],
                            zone_stats['timestamp']
                        )
                        logger.info(
                            f"{zone_stats['timestamp']} - {self.zone_labels[zone_num]}: "
                            f"Count={zone_stats['count']}"
                        )
            
            video_writer.write(annotated_frame)
            frame_count += 1
            
            # Print progress
            if frame_count % 100 == 0:
                logger.info(f"Processed frame {frame_count}")
        
        video_writer.release()


def main():
    zones_config = [
        # Queue Areas
        [[213, 412], [222, 567], [519, 550], [508, 401]],  # Chicken Rice Queue
        [[523, 413], [529, 526], [728, 512], [725, 416]],  # Indian Food Queue
        [[737, 419], [742, 523], [883, 520], [877, 422]],  # Taiwanese Queue
        
        # Seating Areas
        [[-1, 601], [291, 589], [876, 1076], [26, 1070]],  # Aisle 1
        [[377, 607], [641, 568], [1691, 899], [1444, 1073], [989, 1062]],  # Aisle 2
        [[758, 601], [891, 561], [1725, 688], [1565, 814]], # Aisle 3
    ]
    
    analyzer = CanteenAnalyzer(
        source_video_path="prototype_video.mp4",
        zones_config=zones_config,

    )
    
    analyzer.analyze_video()

if __name__ == "__main__":
    main()