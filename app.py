import streamlit as st

st.title("AI Exam Anxiety Detector Test")
student_name = st.text_input("Enter Name:")

if student_name:
    st.write(f"Hello {student_name}, the system is loading...")
    st.camera_input("Take a test photo") # ਇਹ Streamlit ਦਾ ਆਪਣਾ ਕੈਮਰਾ ਬਟਨ ਹੈ