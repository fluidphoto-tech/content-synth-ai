import streamlit as st

st.title("🎨 Content Synth AI - Test Deployment")

st.write("Hello from Ruth's AI project!")

name = st.text_input("What's your name?")
if name:
    st.write(f"Welcome, {name}! 👋")

st.success("✅ If you can see this, your Streamlit app is working!")