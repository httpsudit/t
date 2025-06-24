import cv2
import face_recognition
import numpy as np
import os
from dotenv import dotenv_values
import threading
import time

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")

class FaceAuthenticator:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.authenticated = False
        self.camera = None
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load known faces from the Data/Faces directory"""
        faces_dir = "Data/Faces"
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
            print(f"Created {faces_dir} directory")
            return
            
        for filename in os.listdir(faces_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(faces_dir, filename)
                try:
                    # Load image and get face encoding
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        # Use the username from env or filename without extension
                        name = Username if Username else os.path.splitext(filename)[0]
                        self.known_face_names.append(name)
                        print(f"Loaded face for: {name}")
                    else:
                        print(f"No face found in {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def start_authentication(self):
        """Start the face authentication process"""
        try:
            # Try different camera indices
            for camera_index in [0, 1, 2]:
                self.camera = cv2.VideoCapture(camera_index)
                if self.camera.isOpened():
                    print(f"Camera {camera_index} opened successfully")
                    break
            else:
                print("No camera found")
                return False
                
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def authenticate_face(self, timeout=30):
        """Authenticate face with timeout"""
        if not self.known_face_encodings:
            print("No known faces loaded. Please add face images to Data/Faces directory.")
            return False
            
        if not self.start_authentication():
            return False
            
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            
            if self.process_this_frame:
                # Find faces in current frame
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                
                self.face_names = []
                for face_encoding in self.face_encodings:
                    # Compare with known faces
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    name = "Unknown"
                    
                    # Use the known face with smallest distance
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                        name = self.known_face_names[best_match_index]
                        self.authenticated = True
                        self.cleanup()
                        return True
                    
                    self.face_names.append(name)
            
            self.process_this_frame = not self.process_this_frame
            
            # Display results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Draw rectangle around face
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
            # Add instructions
            cv2.putText(frame, "Look at camera for authentication", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Time remaining: {int(timeout - (time.time() - start_time))}s", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('JARVIS Face Authentication', frame)
            
            # Break on 'q' key or ESC
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
        
        self.cleanup()
        return False
    
    def cleanup(self):
        """Clean up camera and windows"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
    
    def quick_authenticate(self):
        """Quick authentication for testing"""
        return self.authenticate_face(timeout=10)

# Global authenticator instance
face_auth = FaceAuthenticator()

def authenticate_user():
    """Main authentication function"""
    print("Starting face authentication...")
    return face_auth.authenticate_face()

if __name__ == "__main__":
    # Test authentication
    if authenticate_user():
        print("Authentication successful!")
    else:
        print("Authentication failed!")