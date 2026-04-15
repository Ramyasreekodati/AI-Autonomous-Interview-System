import streamlit as st
import os
import sys

st.set_page_config(page_title="Debug Mode")
st.title("🛠 Debug Mode")

st.write("### Environment Info")
st.write(f"**Python Version:** {sys.version}")
st.write(f"**Current Directory:** `{os.getcwd()}`")
st.write(f"**Files in Root:** `{os.listdir('.')}`")

try:
    import sqlalchemy
    st.success("✅ SQLAlchemy is installed")
except ImportError:
    st.error("❌ SQLAlchemy is missing")

try:
    import cv2
    st.success(f"✅ OpenCV is installed (Version: {cv2.__version__})")
except ImportError:
    st.error("❌ OpenCV is missing")
except Exception as e:
    st.error(f"❌ OpenCV error: {e}")

st.write("---")
if st.button("Resume Full App"):
    st.info("I will restore the full app logic in the next update. Please tell the assistant you see the Debug page.")
