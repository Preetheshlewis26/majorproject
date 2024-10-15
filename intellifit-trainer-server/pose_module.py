import mediapipe as mp
import math
import cv2

# Class to handle image processing
class PoseDetector:
    def __init__(self, static_image_mode=False, model_complexity=1,
                 smooth_landmarks=True, enable_segmentation=False,
                 smooth_segmentation=True, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):

        # List to store the actual coordinates of each landmark
        self.lmList = None
        # Will process pose operations on the image
        self.results = None
        # Variables for the Pose class from the mediapipe library
        self.mode = static_image_mode
        self.complexity = model_complexity
        self.smooth = smooth_landmarks
        self.e_segmentation = enable_segmentation
        self.s_segmentation = smooth_segmentation
        self.d_confidence = min_detection_confidence
        self.t_confidence = min_tracking_confidence
        # Will draw the detected points, lines, and other shapes on the images
        self.mpDraw = mp.solutions.drawing_utils
        # Access the pose module of mediapipe
        self.mpPose = mp.solutions.pose
        # The pose object from mediapipe
        self.pose = self.mpPose.Pose(self.mode, self.complexity, self.smooth,
                                     self.e_segmentation, self.s_segmentation,
                                     self.d_confidence, self.t_confidence)

    # Detects the pose on the image and draws connections, then returns the image
    def findPose(self, img, draw=True):
        # Converts the image color format from BGR to RGB
        # Note: OpenCV reads images in BGR format, but some libraries like MediaPipe work in RGB format
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Performs pose detection on the converted image
        self.results = self.pose.process(imgRGB)

        # Checks if any landmarks are detected on the image
        if self.results.pose_landmarks:
            if draw:
                # Specifies the drawing style for each detected body point
                drawing_spec = self.mpDraw.DrawingSpec(thickness=5, circle_radius=2, color=(0, 0, 255))
                # Specifies the drawing style for lines connecting the detected points
                connection_drawing_spec = self.mpDraw.DrawingSpec(thickness=2, color=(0, 255, 0))
                # Draws the detected landmarks and the lines connecting them on the image
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
                                           drawing_spec, connection_drawing_spec)
        # Returns the modified image
        return img

    # Finds the pixel coordinates of each pose landmark on the image and returns them as a list
    def findPosition(self, img, draw=True):
        # Creates a list to store the landmarks
        self.lmList = []

        # Checks if any landmarks are detected on the image
        if self.results.pose_landmarks:
            # Iterates over the landmarks (lm) and their ids
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                # Retrieves the dimensions of the image (h - height, w - width, c - color channels)
                h, w, c = img.shape
                # Normalized x and y coordinates of the landmark...(1)
                # Scales them to pixel coordinates based on the actual image size...(2)
                cx, cy = int(lm.x * w), int(lm.y * h)
                # Adds the actual pixel coordinates to the lmList
                self.lmList.append([id, cx, cy])
                # Marks the coordinates on the image
                if draw:
                    cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        # Returns the updated list
        return self.lmList

    # Calculates the angle between three landmark points
    def findAngle(self, img, p1, p2, p3, draw=True):
        # Assigns the x, y values of the three points to variables
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Calculates the angle between the three points...(1)
        # Computes the angle between the vectors p2->p3 and p2->p1, with p2 being the pivot point
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        # Ensures the angle remains positive by taking the absolute value
        if angle < 0:
            angle = abs(angle)
        # If the angle exceeds 180 degrees, it takes the complementary value
        if angle > 180:
            angle -= 360
            angle = abs(angle)

        if draw:
            # Draws two lines connecting the points
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 5)
            cv2.line(img, (x2, y2), (x3, y3), (0, 255, 0), 5)
            # Marks each point twice, with a small and a larger circle
            cv2.circle(img, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), 3)

            cv2.circle(img, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), 3)

            cv2.circle(img, (x3, y3), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x3, y3), 10, (255, 0, 0), 3)

            # Displays the angle between the points on the image
            cv2.putText(img, str(int(angle)), (x2, y2), cv2.FONT_HERSHEY_PLAIN,
                                          2, (0, 0, 255), 2)
        # Returns the calculated angle
        return angle
