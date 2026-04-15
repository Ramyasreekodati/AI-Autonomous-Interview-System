import streamlit as st
import os
import sys

st.set_page_config(page_title="Debug Mode")
st.title("🛠 Debug Mode")

st.write("### Environment Info")
st.write(f"**Python Version:** {sys.version}")
st.write(f"**Current Directory:** `{os.getcwd()}`")
st.write(f"**Files in Root:** `{os.listdir('.')}`")

st.write("---")
if st.button("Check Database"):
    try:
        from database import engine
        st.success("✅ Database module found")
    except Exception as e:
        st.error(f"❌ Database error: {e}")
if st.button("Resume Full App"):
    st.info("I will restore the full app logic in the next update. Please tell the assistant you see the Debug page.")
