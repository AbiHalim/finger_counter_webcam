import cv2
import mediapipe as mp
import pygame

pygame.mixer.init()
pygame.mixer.music.load("sadarkan_aku.wav")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
m = 0

# Load video capture
cap = cv2.VideoCapture(0)

# Initialize Mediapipe hands
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        # Read frame from camera
        ret, frame = cap.read()

        # Convert image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Flip image horizontally
        image = cv2.flip(image, 1)

        # Set flag to detect landmarks
        results = hands.process(image)

        # Draw landmarks on image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)     
        
        # Detect finger count
        finger_count = 0
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            tip_ids = [4, 8, 12, 16, 20]  # Landmark ids of finger tips
            finger_states = []
            for tip_id in tip_ids:
                finger_tip = hand_landmarks.landmark[tip_id]
                finger_mcp = hand_landmarks.landmark[tip_id - 1]
                # Check if finger is open or closed
                if tip_id==4:
                    finger_states.append(finger_tip.x < finger_mcp.x)
                else:
                    finger_states.append(finger_tip.y < finger_mcp.y)
            # Count number of open fingers
            finger_count = finger_states.count(True)

        # Display finger count on image (large, centered with outline for readability)
        text = str(finger_count) if finger_count != 5 else "JAM LIMA MENTIONED RAHHH"
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Scale and thickness tuned for large display; adjust if it's too big/small for your camera resolution
        scale = 1
        thickness = 12
        # Calculate text size so we can center it
        (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
        x = (image.shape[1] - text_width) // 2
        # y is baseline-based: put text vertically centered visually
        y = (image.shape[0] + text_height) // 2
        # Draw a thick black outline for contrast
        cv2.putText(image, text, (x, y), font, scale, (0, 0, 0), thickness + 6, cv2.LINE_AA)
        # Draw the colored text on top
        cv2.putText(image, text, (x, y), font, scale, (0, 0, 255), thickness, cv2.LINE_AA)

        # Display image
        cv2.imshow('Finger Counter', image)
        if finger_count == 5 and m == 0:
            pygame.mixer.music.play()
            m = 1

        # Check for 'q' key to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release video capture and close windows
cap.release()
cv2.destroyAllWindows()
