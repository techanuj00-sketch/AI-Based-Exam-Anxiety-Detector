import cv2
from deepface import DeepFace
import csv
from datetime import datetime
import pyttsx3
import sys
import threading

student_name = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
voice_engine = pyttsx3.init()
is_speaking = False

def speak(text):
    global is_speaking
    is_speaking = True
    voice_engine.say(text)
    voice_engine.runAndWait()
    is_speaking = False

filename = f"{student_name}_anxiety_report.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Emotion", "Fear Score", "Status", "Student Name"])

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    try:
        results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        main_emotion = results[0]['dominant_emotion']
        fear_score = int(results[0]['emotion']['fear'])

        status = "Calm"
        color = (0, 255, 0)
        
        if fear_score > 30:
            status = "Anxiety Detected"
            color = (0, 0, 255)
            if fear_score > 70 and not is_speaking:
                threading.Thread(target=speak, args=(f"{student_name}, please relax",)).start()

        current_time = datetime.now().strftime("%H:%M:%S")
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([current_time, main_emotion, fear_score, status, student_name])

        # ਕਾਲਾ ਡੱਬਾ ਹਟਾ ਦਿੱਤਾ ਗਿਆ ਹੈ (cv2.rectangle ਲਾਈਨ ਡਿਲੀਟ ਕਰ ਦਿੱਤੀ)
        cv2.putText(frame, f"Student: {student_name}", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Status: {status}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Fear: {fear_score}%", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    except Exception:
        cv2.putText(frame, "AI Processing...", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow('AI Exam Anxiety Detector', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()