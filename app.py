
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import cv2
from deepface import DeepFace
import numpy as np
import pandas as pd
from datetime import datetime
import os
import av

# Page Configuration
st.set_page_config(page_title="AI Anxiety Detector Pro", layout="wide")

# iPhone, Android, and PC Connection Fix (STUN Servers)
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun3.l.google.com:19302"]},
        {"urls": ["stun:stun4.l.google.com:19302"]}
    ]}
)

# Custom CSS for Professional Dashboard
st.markdown("""
    <style>
    [data-testid="stSidebar"] { border-right: 1px solid #e6e9ef; background-color: #f8f9fa; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 AI-Based Exam Proctoring & Anxiety Detector")

# Sidebar
st.sidebar.header("📋 Student Portal")
student_name = st.sidebar.text_input("Student Name:", placeholder="Enter Full Name")
device_type = st.sidebar.selectbox("Select Device:", ["PC / Laptop", "Mobile (Front Cam)"])

# Camera Orientation for Mobile
video_constraints = {"facingMode": "user"} if device_type == "Mobile (Front Cam)" else True

if student_name:
    filename = f"{student_name}_report.csv"
    col_v, col_e = st.columns([1.6, 1])

    with col_v:
        st.subheader("📸 Live AI Monitoring")
        
        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            
            # --- MIRROR EFFECT FIX (Sidha Camera) ---
            # Horizontal flip (1) taaki left/right movement natural lage
            img = cv2.flip(img, 1)
            
            if not hasattr(video_frame_callback, "count"):
                video_frame_callback.count = 0
                video_frame_callback.emotions = {"Anxiety": 0, "Sadness": 0, "Stress": 0, "Happy": 0}
            
            video_frame_callback.count += 1
            try:
                # --- TEXT POSITIONING ---
                # Left side te Student Name
                cv2.putText(img, f"PROCTOR: {student_name.upper()}", (20, 40), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)

                # Emotion Analysis (Har 25 frames baad)
                if video_frame_callback.count % 25 == 0:
                    results = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                    res = results[0]['emotion']
                    video_frame_callback.emotions = {
                        "Anxiety": int(res['fear']),
                        "Sadness": int(res['sad']),
                        "Stress": int(res['angry']),
                        "Happy": int(res['happy'])
                    }
                
                e = video_frame_callback.emotions
                status = "HIGH ALERT" if e['Anxiety'] > 35 or e['Stress'] > 45 else "NORMAL"
                color = (0, 0, 255) if status == "HIGH ALERT" else (0, 255, 0)
                
                # Right side te Status
                cv2.putText(img, f"STATUS: {status}", (img.shape[1]-250, 40), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, color, 2)

                # Save Data to CSV
                if video_frame_callback.count % 100 == 0:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    pd.DataFrame([[timestamp, e['Anxiety'], e['Sadness'], e['Stress'], e['Happy'], status]], 
                                 columns=["Time", "Fear %", "Sad %", "Stress %", "Happy %", "Status"]).to_csv(
                                 filename, mode='a', header=not os.path.exists(filename), index=False)
            except:
                pass
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        webrtc_streamer(
            key="proctoring-final-v9",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": video_constraints, "audio": False},
            async_processing=True
        )

    with col_e:
        st.subheader("📊 Session Analytics")
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                if not df.empty and "Happy %" in df.columns:
                    last_row = df.iloc[-1]
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"😊 Happy: {last_row['Happy %']}%")
                        st.progress(int(last_row['Happy %']) / 100)
                        st.write(f"😟 Anxiety: {last_row['Fear %']}%")
                        st.progress(int(last_row['Fear %']) / 100)
                    with c2:
                        st.write(f"😢 Sadness: {last_row['Sad %']}%")
                        st.progress(int(last_row['Sad %']) / 100)
                        st.write(f"😠 Stress: {last_row['Stress %']}%")
                        st.progress(int(last_row['Stress %']) / 100)
                    
                    st.divider()
                    st.area_chart(df[["Fear %", "Sad %", "Stress %", "Happy %"]], height=200)
                    
                    st.subheader("📋 Session Log")
                    st.dataframe(df[["Time", "Fear %", "Sad %", "Stress %", "Happy %", "Status"]].tail(10), use_container_width=True)
        except Exception:
            st.info("ਸੈਸ਼ਨ ਅਪਡੇਟ ਹੋ ਰਿਹਾ ਹੈ...")

    if os.path.exists(filename):
        st.sidebar.markdown("---")
        with open(filename, "rb") as f:
            st.sidebar.download_button("📥 Download Report", f, file_name=filename, use_container_width=True)
else:
    st.info("Enter student name and click on start")
