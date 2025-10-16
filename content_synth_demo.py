import streamlit as st
import anthropic
from datetime import datetime

st.set_page_config(
    page_title="Content Synth AI",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Content Synth AI</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Content Generation for Educational Social Media**")
st.markdown("---")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Claude API Key", type="password")
    st.markdown("---")
    st.info("This prototype demonstrates AI-generated social media content.")

tab1, tab2 = st.tabs(["Generate Content", "Insights"])

with tab1:
    st.subheader("Campaign Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        industry = st.selectbox("Industry", ["Higher Education", "Online Learning", "Tutoring"])
        campaign_type = st.selectbox("Campaign Type", ["Summer School", "Course Enrollment", "Workshop"])
        platform = st.selectbox("Platform", ["Instagram", "Facebook", "TikTok"])
    
    with col2:
        brand_tone = st.select_slider("Brand Tone", options=["Professional", "Balanced", "Casual"], value="Balanced")
        include_emojis = st.checkbox("Include Emojis", value=True)
    
    campaign_details = st.text_area("Campaign Details", placeholder="Describe your campaign...")
    
    if st.button("Generate Content", type="primary"):
        if not api_key:
            st.error("Please enter API key")
        elif not campaign_details:
            st.warning("Please provide campaign details")
        else:
            with st.spinner("Generating..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    prompt = f"""Generate social media content:
Industry: {industry}
Campaign: {campaign_type}
Platform: {platform}
Tone: {brand_tone}
Details: {campaign_details}

Provide a caption and 8 hashtags."""

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    st.markdown("### Generated Content")
                    st.markdown(message.content[0].text)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Campaign Insights")
    st.info("Performance metrics will display here")
    st.markdown("**Optimal Posting Times (from Fluidphoto data):**")
    st.markdown("- Instagram: 12:00, 18:00, 20:00")
    st.markdown("- Facebook: 08:00, 18:00, 13:00")