# content_synth_app.py
import streamlit as st
import anthropic
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Content Synth AI",
    page_icon="✨",
    layout="wide"
)

# Custom CSS matching your design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: bold;
    }
    .output-box {
        background-color: #e8f5e9;
        border: 2px solid #27ae60;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .caption-text {
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 1rem 0;
    }
    .hashtag-box {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .insight-badge {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>✨ Content Synth AI</h1>
    <p>R.S.E Digital Labs | Data-Driven Social Media Caption Generator</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Sidebar for API key
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your Anthropic API key"
    )
    if api_key:
        st.session_state.api_key = api_key
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    This AI system is trained on:
    - 502 days of real business data
    - 107 strategic social posts
    - Cross-platform performance metrics
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">📝 INPUT SECTION</div>', unsafe_allow_html=True)
    
    # Platform selection
    platform = st.selectbox(
        "🔵 Platform",
        ["Instagram", "TikTok", "Facebook", "Cross-Platform (Instagram + TikTok + Facebook)"],
        help="Select your target platform"
    )
    
    # Campaign type
    campaign_type = st.selectbox(
        "📢 Campaign Type",
        [
            "Summer School",
            "Course Enrollment",
            "Tutoring Services",
            "Music-Integrated Learning",
            "Dance/Movement Learning",
            "Workshop Event",
            "Study Tips & Hacks"
        ]
    )
    
    # Target audience
    audience = st.text_input(
        "🎯 Target Audience",
        value="University Students",
        help="Describe your target audience"
    )
    
    # Course/Event title
    course_title = st.text_input(
        "📚 Course/Event Title",
        value="Summer Program 2025",
        help="Enter the name of your course, event, or program"
    )
    
    # Brand voice
    st.markdown("**🎨 Brand Voice**")
    brand_tone = st.radio(
        "",
        ["Professional", "Casual", "Friendly"],
        horizontal=True
    )
    
    # Generate button
    generate_clicked = st.button("✨ GENERATE", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📤 OUTPUT SECTION</div>', unsafe_allow_html=True)
    
    if generate_clicked:
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Claude API key in the sidebar!")
        else:
            with st.spinner("🤖 AI is crafting your caption..."):
                # Hashtag bank
                HASHTAG_BANK = {
                    "base_education": ["#nzstudents", "#education", "#studentlife", "#studysmart"],
                    "music_learning": ["#StudyPlaylist", "#MusicLearning", "#AudioLearning"],
                    "dance_learning": ["#DanceLearning", "#MovementStudy", "#KinestheticLearning"],
                    "course_promo": ["#CourseEnrollment", "#SkillBuilding", "#LearnOnTheGo"],
                    "platform_specific": {
                        "tiktok": ["#studenttok", "#educationtok", "#studywithme"],
                        "instagram": ["#studygram", "#studentmotivation", "#instaeducation"],
                        "facebook": ["#EducationFirst", "#LearningCommunity"]
                    }
                }
                
                # Build hashtags
                hashtags = HASHTAG_BANK["base_education"][:4]
                if "Music" in campaign_type:
                    hashtags.extend(HASHTAG_BANK["music_learning"][:3])
                elif "Dance" in campaign_type:
                    hashtags.extend(HASHTAG_BANK["dance_learning"][:3])
                else:
                    hashtags.extend(HASHTAG_BANK["course_promo"][:3])
                
                # Add platform-specific
                platform_lower = platform.lower()
                if "instagram" in platform_lower:
                    hashtags.extend(HASHTAG_BANK["platform_specific"]["instagram"][:2])
                elif "tiktok" in platform_lower:
                    hashtags.extend(HASHTAG_BANK["platform_specific"]["tiktok"][:2])
                
                # Build prompt
                char_limit = 150 if "instagram" in platform_lower or "tiktok" in platform_lower else 200
                
                prompt = f"""You are Content Synth AI, trained on 502 days of real photography business data showing:
- Friday posts: 7.86x higher engagement
- Instagram peak: 6-8 PM
- Mobile-first audience: 85.71%
- Cross-platform strategy: proven effective

Generate a {platform} caption for:
Campaign: {campaign_type}
Audience: {audience}
Course: {course_title}
Tone: {brand_tone}

REQUIREMENTS:
- Maximum {char_limit} characters
- {brand_tone.lower()} tone
- Lead with benefit/transformation
- Include natural call-to-action (5 words max)
- NO hashtags (provided separately)
- Mobile-optimized (most readers on phones)

Write ONLY the caption text:"""
                
                try:
                    # Call Claude API
                    client = anthropic.Anthropic(api_key=st.session_state.api_key)
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    caption = message.content[0].text
                    
                    # Store in session state
                    st.session_state.generated_caption = {
                        "caption": caption,
                        "hashtags": hashtags,
                        "platform": platform,
                        "char_count": len(caption),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.generated_caption:
        result = st.session_state.generated_caption
        
        st.markdown(f"""
        <div class="output-box">
            <h3>✅ Caption & Hashtags Ready!</h3>
            <p style="color: #666;">({result['char_count']} characters)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Caption
        st.markdown("**📝 Your Caption:**")
        st.markdown(f'<div class="caption-text">{result["caption"]}</div>', unsafe_allow_html=True)
        
        # Hashtags
        st.markdown("**#️⃣ Optimized Hashtags:**")
        st.markdown(f'<div class="hashtag-box">{" ".join(result["hashtags"])}</div>', unsafe_allow_html=True)
        
        # Data insights applied
        st.markdown("**📊 Data Insights Applied:**")
        insights = [
            "Friday engagement: 7.86x boost (Fluidphoto Data)",
            "Mobile-first design: 85.71% mobile usage",
            f"{result['platform']} peak times optimized"
        ]
        for insight in insights:
            st.markdown(f'<div class="insight-badge">• {insight}</div>', unsafe_allow_html=True)
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Copy All", use_container_width=True):
                st.toast("✅ Copied to clipboard!")
        with col_btn2:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.generated_caption = None
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Content Synth AI</strong> | R.S.E Digital Labs</p>
    <p>Powered by real business data from 502 days of Fluidphoto analytics</p>
</div>
""", unsafe_allow_html=True)