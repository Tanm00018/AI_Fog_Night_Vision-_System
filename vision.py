import cv2
import numpy as np
import threading

class VisionProcessor:
    def __init__(self):
        self.cap = None
        self.video_path = None
        self.lock = threading.Lock()
        
        # Default settings
        self.mode = "normal" # "normal", "fog", "night"
        self.fog_strength = 50 # 0-100
        self.brightness = 50 # 0-100
        self.contrast = 50 # 0-100
        self.split_screen = False
        self.edge_highlight = False
        
        # Pre-initialize CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # CLAHE is very fast and effective for both fog and night vision approximation
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def set_video_source(self, path):
        with self.lock:
            if self.cap is not None:
                self.cap.release()
            self.video_path = path
            self.cap = cv2.VideoCapture(path)
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def update_settings(self, mode=None, fog_strength=None, brightness=None, contrast=None, split_screen=None, edge_highlight=None):
        with self.lock:
            if mode is not None:
                self.mode = mode
            if fog_strength is not None:
                self.fog_strength = int(fog_strength)
            if brightness is not None:
                self.brightness = int(brightness)
            if contrast is not None:
                self.contrast = int(contrast)
            if split_screen is not None:
                self.split_screen = split_screen
            if edge_highlight is not None:
                self.edge_highlight = edge_highlight

    def apply_fog_vision(self, frame):
        # Fast Dehazing using CLAHE on lightness channel
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clip_limit = 1.0 + (self.fog_strength / 100.0) * 3.0
        self.clahe.setClipLimit(clip_limit)

        cl = self.clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return final

    def apply_night_vision(self, frame):
        # Convert to grayscale to simulate night vision sensors and speed up processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        alpha = 1.0 + (self.contrast / 100.0) * 2.0
        beta = (self.brightness - 50) * 2
        
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        self.clahe.setClipLimit(2.0)
        enhanced = self.clahe.apply(enhanced)
        
        night_frame = np.zeros_like(frame)
        night_frame[:,:,1] = enhanced
        
        return night_frame

    def get_frame(self):
        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Waiting for Video Upload...", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                return buffer.tobytes()

            success, frame = self.cap.read()
            
            if not success:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self.cap.read()
                if not success:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "Error reading video", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    return buffer.tobytes()
            
            if success:
                # Resize frame to a lower resolution to reduce heavy processing on old device
                frame = cv2.resize(frame, (640, 480))
                original_frame = frame.copy()
                
                # Apply processing based on mode
                if self.mode == "fog":
                    frame = self.apply_fog_vision(frame)
                elif self.mode == "night":
                    frame = self.apply_night_vision(frame)
                else: # normal
                    if self.brightness != 50 or self.contrast != 50:
                        alpha = 1.0 + ((self.contrast - 50) / 50.0)
                        beta = (self.brightness - 50) * 2
                        frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

                # Edge Highlighting (ADAS simulation)
                if self.edge_highlight:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(gray, 50, 150)
                    edge_colored = np.zeros_like(frame)
                    edge_colored[edges > 0] = [0, 255, 0] # Bright Green
                    frame = cv2.addWeighted(frame, 0.8, edge_colored, 0.6, 0)

                # Split Screen
                if self.split_screen:
                    orig_resized = cv2.resize(original_frame, (320, 480))
                    proc_resized = cv2.resize(frame, (320, 480))
                    cv2.putText(orig_resized, "RAW", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(proc_resized, "AI ENHANCED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    frame = np.hstack((orig_resized, proc_resized))

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            return buffer.tobytes()
            
    def __del__(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
