# content_synth_app.py - VERSION 2.0
# New Features: Student Personas, Research-Based Hashtags, Caption Length Enforcement

import streamlit as st
from anthropic import Anthropic
import pandas as pd
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Content Synth AI v2.0",
    page_icon="✨",
    layout="wide"
)

# API KEY SETUP
api_key = st.secrets.get("ANTHROPIC_API_KEY", None)

if not api_key:
    api_key = st.text_input(
        "🔑 Claude API Key", 
        type="password",
        help="Enter your Anthropic API key"
    )

if api_key:
    client = Anthropic(api_key=api_key)
else:
    st.warning("Please enter your Claude API key to continue")
    st.stop()

# Custom CSS
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
    .persona-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .caption-text {
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 1rem 0;
        padding: 1rem;
        background: white;
        border-radius: 6px;
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
    .dataset-badge {
        display: inline-block;
        background-color: #fff3e0;
        color: #f57c00;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .char-counter {
        font-size: 0.9rem;
        color: #666;
        font-weight: bold;
    }
    .char-limit-good {
        color: #27ae60;
    }
    .char-limit-warning {
        color: #f39c12;
    }
    .char-limit-exceeded {
        color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# STUDENT PERSONAS - Based on research
# ==========================================

STUDENT_PERSONAS = {
    "Creative Performer": {
        "description": "Music, dance, and arts-focused students (45% of audience)",
        "demographics": "70% Female, Age 16-18",
        "interests": ["Music (0.77)", "Dance (0.49)", "Band (0.30)", "Rock (0.25)"],
        "messaging_style": "Friendly, expressive, energetic",
        "key_benefits": "Empowerment, creativity, belonging",
        "cta_style": "Share your vibe, Turn up for your dreams, Join the movement",
        "campaigns": ["Your Story. Your Stage.", "Start Your Story Here", "Discover What NZ Can Teach You"]
    },
    "Competitive Athlete": {
        "description": "Sports and achievement-driven students (35% of audience)",
        "demographics": "75% Male, Age 17-20",
        "interests": ["Football (0.45)", "Basketball (0.31)", "Baseball (0.27)", "Sports (0.20)"],
        "messaging_style": "Motivational, bold, competitive",
        "key_benefits": "Achievement, teamwork, consistency",
        "cta_style": "Show up strong, Join the challenge, Train hard",
        "campaigns": ["Game On: Every Day Counts", "Snap & Score Challenge", "Summer Drive"]
    },
    "Balanced Explorer": {
        "description": "Lifestyle and well-rounded learners (20% of audience)",
        "demographics": "Mixed gender, Age 16-22",
        "interests": ["Music (0.50)", "Dance (0.34)", "Swimming (0.09)", "Study-life balance"],
        "messaging_style": "Warm, conversational, inclusive",
        "key_benefits": "Discovery, belonging, life-balance",
        "cta_style": "Learn. Explore. Belong., Start your story, Discover",
        "campaigns": ["Explore Your Path", "Study + Adventure Diaries", "Inspiring the Future"]
    }
}

# ==========================================
# RESEARCH-BASED HASHTAG BANK
# From TikTok Education NZ Research
# ==========================================

HASHTAG_BANK = {
    "high_engagement_boosters": {
        "tags": ["#viral", "#comedy", "#challenge", "#tech"],
        "avg_engagement": "80-100%",
        "note": "Algorithmic visibility boosters"
    },
    "education_core": {
        "tags": ["#education", "#study", "#learning", "#studywithme", "#studytips"],
        "avg_engagement": "65%+",
        "note": "Core discoverability tags"
    },
    "edtech_innovation": {
        "tags": ["#edtech", "#tech", "#AIinEducation", "#maker"],
        "avg_engagement": "Moderate-High",
        "note": "Modern digital learning"
    },
    "nz_localized": {
        "tags": ["#NZEducation", "#nzhistory", "#KiwiStudents"],
        "avg_engagement": "High for NZ",
        "note": "Regional targeting"
    },
    "career_vocational": {
        "tags": ["#careeradvice", "#welding", "#plastering", "#manufacturing", "#firelife"],
        "avg_engagement": "Moderate",
        "note": "Applied learning & trades"
    },
    "student_lifestyle": {
        "tags": ["#teacherlife", "#fitness", "#music", "#fashion"],
        "avg_engagement": "Medium-High",
        "note": "Lifestyle integration"
    }
}

# ==========================================
# CAMPAIGN TO PERSONA MAPPING
# ==========================================

def get_persona_for_campaign(campaign_type):
    """Auto-select appropriate persona based on campaign type"""
    
    campaign_persona_map = {
        "Music-Integrated Learning": "Creative Performer",
        "Dance/Movement Learning": "Creative Performer",
        "Sports Challenge": "Competitive Athlete",
        "Achievement Program": "Competitive Athlete",
        "Fitness & Wellness Program": "Competitive Athlete",
        "Summer School": "Balanced Explorer",
        "Course Enrollment": "Balanced Explorer",
        "Tutoring Services": "Balanced Explorer",
        "Workshop Event": "Balanced Explorer",
        "Study Tips & Hacks": "Balanced Explorer"
    }
    
    return campaign_persona_map.get(campaign_type, "Balanced Explorer")

# ==========================================
# HASHTAG SELECTION LOGIC
# ==========================================

def select_hashtags_for_persona(persona_name, platform, campaign_type):
    """Select 3-5 relevant hashtags based on persona, platform, and campaign"""
    
    selected_hashtags = []
    
    # Always include one high-engagement booster
    selected_hashtags.append("#viral")
    
    # Add core education tag
    selected_hashtags.append("#education")
    
    # Persona-specific hashtags
    if persona_name == "Creative Performer":
        selected_hashtags.extend(["#music", "#studywithme"])
        if "Music" in campaign_type:
            selected_hashtags.append("#tech")  # Modern music tech
        elif "Dance" in campaign_type:
            selected_hashtags.append("#challenge")
    
    elif persona_name == "Competitive Athlete":
        selected_hashtags.extend(["#challenge", "#motivation"])
        selected_hashtags.append("#careeradvice")
    
    else:  # Balanced Explorer
        selected_hashtags.extend(["#study", "#learning"])
        selected_hashtags.append("#studytips")
    
    # Platform-specific additions
    platform_lower = platform.lower()
    if "tiktok" in platform_lower:
        if "#comedy" not in selected_hashtags and len(selected_hashtags) < 5:
            selected_hashtags.append("#comedy")
    
    # Add NZ localization if room
    if len(selected_hashtags) < 5:
        selected_hashtags.append("#NZEducation")
    
    return selected_hashtags[:5]  # Return exactly 3-5 hashtags

# ==========================================
# CAPTION LENGTH ENFORCEMENT
# ==========================================

def get_caption_limit(platform):
    """Return strict character limit based on platform"""
    platform_lower = platform.lower()
    
    if "instagram" in platform_lower or "tiktok" in platform_lower:
        return 150
    elif "facebook" in platform_lower:
        return 200
    else:  # Cross-platform defaults to shortest
        return 150

def check_caption_length(caption, limit):
    """Check if caption meets length requirements"""
    length = len(caption)
    
    if length <= limit:
        return "good", length
    elif length <= limit + 10:
        return "warning", length
    else:
        return "exceeded", length

# ==========================================
# DATA LOADING FUNCTIONS
# ==========================================

@st.cache_data
def load_datasets():
    """Load all 3 datasets and return them"""
    try:
        data_path = Path("data")
        
        photo_df = pd.read_csv(data_path / "Photography_Business_Master_Analytics_With_PostingTimes.csv")
        clustering_df = pd.read_excel(data_path / "Clustering_Marketing_FinalClean.xlsx")
        viral_df = pd.read_excel(data_path / "Viral_Social_Media_Trends_FinalClean.xlsx")
        
        return photo_df, clustering_df, viral_df, None
    except Exception as e:
        return None, None, None, str(e)

@st.cache_data
def extract_photography_insights(photo_df):
    """Extract key insights from Photography Business Data"""
    insights = {}
    
    day_engagement = photo_df.groupby('Day_of_Week')['Total_Social_Engagement'].mean()
    insights['friday_boost'] = day_engagement.get('Friday', 0)
    weekday_avg = day_engagement[['Monday', 'Tuesday', 'Wednesday', 'Thursday']].mean()
    insights['friday_multiplier'] = round(insights['friday_boost'] / weekday_avg, 2) if weekday_avg > 0 else 0
    
    insights['mobile_pct'] = round(photo_df['Mobile_Percentage'].mean(), 2)
    
    cross_platform = photo_df[photo_df['Total_Posts_Today'] >= 2]['Total_Social_Engagement'].mean()
    single_platform = photo_df[photo_df['Total_Posts_Today'] == 1]['Total_Social_Engagement'].mean()
    insights['cross_platform_boost'] = round((cross_platform / single_platform - 1) * 100, 1) if single_platform > 0 else 0
    
    return insights

@st.cache_data
def extract_clustering_insights(clustering_df):
    """Extract key insights from Clustering Marketing Data"""
    insights = {}
    
    gender_counts = clustering_df['gender'].value_counts()
    total_known = gender_counts.get('f', 0) + gender_counts.get('m', 0)
    insights['female_pct'] = round((gender_counts.get('f', 0) / total_known * 100), 2) if total_known > 0 else 0
    
    interest_cols = ['music', 'dance', 'band', 'basketball', 'football', 'soccer', 'sports', 'rock']
    interest_totals = clustering_df[interest_cols].sum().sort_values(ascending=False)
    insights['top_interests'] = interest_totals.head(5).to_dict()
    
    return insights

@st.cache_data
def extract_viral_insights(viral_df):
    """Extract key insights from Viral Trends Data"""
    insights = {}
    
    viral_df['Engagement_Rate'] = ((viral_df['Likes'] + viral_df['Shares'] + viral_df['Comments']) / viral_df['Views'] * 100)
    
    platform_performance = viral_df.groupby('Platform')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['platform_engagement'] = platform_performance.to_dict()
    
    content_performance = viral_df.groupby('Content_Type')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['content_types'] = content_performance.to_dict()
    
    return insights

# ==========================================
# PROMPT BUILDING WITH PERSONA
# ==========================================

def build_persona_prompt(persona_name, platform, campaign_type, course_title, brand_tone, 
                         photo_insights, char_limit):
    """Build prompt incorporating student persona characteristics"""
    
    persona = STUDENT_PERSONAS[persona_name]
    
    prompt = f"""You are Content Synth AI v2.0, generating educational social media captions based on research-backed student personas.

TARGET PERSONA: {persona_name}
Description: {persona['description']}
Demographics: {persona['demographics']}
Top Interests: {', '.join(persona['interests'])}

MESSAGING GUIDELINES:
- Tone: {persona['messaging_style']}
- Key Benefits to Highlight: {persona['key_benefits']}
- Call-to-Action Style: {persona['cta_style']}

PLATFORM & DATA INSIGHTS:
- Platform: {platform}
- Mobile-first audience: {photo_insights['mobile_pct']}% mobile users
- Friday posts: {photo_insights['friday_multiplier']}x engagement boost

CONTENT DETAILS:
Campaign: {campaign_type}
Course/Event: {course_title}
Brand Voice: {brand_tone}

STRICT REQUIREMENTS:
✓ MAXIMUM {char_limit} characters (this is CRITICAL - research-based limit)
✓ Structure: Hook (≈40 chars) + Value Proposition (≈60 chars) + CTA (≈30 chars)
✓ Include 1-2 relevant emojis maximum
✓ {brand_tone.lower()} and {persona['messaging_style'].lower()} tone
✓ Lead with benefit/transformation
✓ NO hashtags in caption (provided separately)
✓ Complete, ready-to-post caption

Write ONLY the caption text, staying under {char_limit} characters:"""
    
    return prompt

# ==========================================
# EXPORT FUNCTIONS
# ==========================================

def create_export_text(result):
    """Create formatted text for export"""
    persona_info = STUDENT_PERSONAS[result.get('persona', 'Balanced Explorer')]
    
    export_text = f"""=== CONTENT SYNTH AI v2.0 - GENERATED CAPTION ===

Platform: {result['platform']}
Generated: {result['timestamp']}
Character Count: {result['char_count']}/{result['char_limit']}

TARGET PERSONA: {result.get('persona', 'N/A')}
Description: {persona_info['description']}
Demographics: {persona_info['demographics']}

CAPTION:
{result['caption']}

HASHTAGS (Research-Based):
{" ".join(result['hashtags'])}

PERSONA INSIGHTS APPLIED:
- Messaging Style: {persona_info['messaging_style']}
- Key Benefits: {persona_info['key_benefits']}
- CTA Style: {persona_info['cta_style']}

DATA SOURCES:
- Student Audience Personas (Campaign Integration)
- TikTok Education NZ Hashtag Research (120 days)
- Caption Length Analysis (BR1 Technical Justification)
- Photography Business Analytics
- Viral Trends Data
- Clustering Marketing Data

===================================
Generated by Content Synth AI v2.0 | R.S.E Digital Labs
"""
    return export_text

def create_export_csv(results_list):
    """Create CSV export for multiple results"""
    df = pd.DataFrame([{
        'Timestamp': r['timestamp'],
        'Platform': r['platform'],
        'Persona': r.get('persona', 'N/A'),
        'Campaign': r.get('campaign_type', 'N/A'),
        'Caption': r['caption'],
        'Hashtags': " ".join(r['hashtags']),
        'Character Count': f"{r['char_count']}/{r['char_limit']}",
        'Brand Tone': r.get('brand_tone', 'N/A')
    } for r in results_list])
    
    return df.to_csv(index=False)

# ==========================================
# MAIN APP
# ==========================================

# Header
st.markdown("""
<div class="main-header">
    <h1>✨ Content Synth AI v2.0</h1>
    <p>R.S.E Digital Labs | Persona-Based Educational Content Generator</p>
    <small>Now with Student Personas + Research-Based Hashtags + Caption Length Enforcement</small>
</div>
""", unsafe_allow_html=True)

# Load datasets
photo_df, clustering_df, viral_df, error = load_datasets()

if error:
    st.error(f"⚠️ Error loading datasets: {error}")
    st.info("💡 Make sure your data files are in the '/data' folder!")
    st.stop()

# Extract insights
photo_insights = extract_photography_insights(photo_df)
clustering_insights = extract_clustering_insights(clustering_df)
viral_insights = extract_viral_insights(viral_df)

# Initialize session state
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = None
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Info")
    
    st.markdown("---")
    st.markdown("### 📊 Live Data Sources")
    st.success(f"✅ Photography Business: {len(photo_df)} days")
    st.success(f"✅ Viral Trends: {len(viral_df)} posts")
    st.success(f"✅ Clustering Marketing: {len(clustering_df)} users")
    
    st.markdown("---")
    st.markdown("### 🎭 Student Personas")
    for persona_name, persona_info in STUDENT_PERSONAS.items():
        with st.expander(f"👤 {persona_name}"):
            st.write(f"**{persona_info['description']}**")
            st.write(f"📊 {persona_info['demographics']}")
            st.write(f"💡 Style: {persona_info['messaging_style']}")
    
    st.markdown("---")
    with st.expander("🔍 View Research Insights"):
        st.markdown("**Caption Length Research:**")
        st.write("- Instagram/TikTok: 150 chars max")
        st.write("- Facebook: 200 chars max")
        st.write("- Mobile truncation: ~125 chars")
        
        st.markdown("**Hashtag Strategy:**")
        st.write("- Use 3-5 hashtags per post")
        st.write("- Mix engagement boosters + niche tags")
        st.write("- Include NZ localization")
        
        st.markdown("**Data Insights:**")
        st.write(f"- Friday boost: {photo_insights['friday_multiplier']}x")
        st.write(f"- Mobile usage: {photo_insights['mobile_pct']}%")
        st.write(f"- Female audience: {clustering_insights['female_pct']}%")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">📝 INPUT SECTION</div>', unsafe_allow_html=True)
    
    platform = st.selectbox(
        "📱 Platform",
        ["Instagram", "TikTok", "Facebook", "Cross-Platform (Instagram + TikTok + Facebook)"],
        help="Select your target platform"
    )
    
    # Show character limit for selected platform
    char_limit = get_caption_limit(platform)
    st.caption(f"📏 Caption limit for this platform: **{char_limit} characters**")
    
    campaign_type = st.selectbox(
        "📢 Campaign Type",
        [
            "Summer School",
            "Course Enrollment",
            "Tutoring Services",
            "Music-Integrated Learning",
            "Dance/Movement Learning",
            "Workshop Event",
            "Study Tips & Hacks",
            "Sports Challenge",
            "Fitness & Wellness Program",
            "Achievement Program"
        ]
    )
    
    # Auto-select and display persona
    selected_persona = get_persona_for_campaign(campaign_type)
    persona_info = STUDENT_PERSONAS[selected_persona]
    
    st.markdown(f"""
    <div style="background-color: #f0f7ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <strong>🎯 Auto-Selected Persona:</strong>
        <span class="persona-badge">{selected_persona}</span>
        <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
        {persona_info['description']}<br>
        <strong>Messaging:</strong> {persona_info['messaging_style']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    course_title = st.text_input(
        "📚 Course/Event Title",
        value="Summer Program 2025",
        help="Enter the name of your course, event, or program"
    )
    
    st.markdown("**🎨 Brand Voice**")
    brand_tone = st.radio(
        "",
        ["Professional", "Casual", "Friendly"],
        horizontal=True
    )
    
    generate_clicked = st.button("✨ GENERATE CAPTION", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📤 OUTPUT SECTION</div>', unsafe_allow_html=True)
    
    if generate_clicked:
        if not api_key:
            st.error("⚠️ Please configure your Claude API key to continue!")
        else:
            with st.spinner(f"🤖 Generating {selected_persona} content for {platform}..."):
                
                # Get character limit
                char_limit = get_caption_limit(platform)
                
                # Build persona-based prompt
                prompt = build_persona_prompt(
                    selected_persona, platform, campaign_type, course_title, brand_tone,
                    photo_insights, char_limit
                )
                
                # Get research-based hashtags
                hashtags = select_hashtags_for_persona(selected_persona, platform, campaign_type)
                
                try:
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=512,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    caption = message.content[0].text.strip()
                    
                    # Check caption length
                    length_status, actual_length = check_caption_length(caption, char_limit)
                    
                    # Store result
                    result = {
                        "caption": caption,
                        "hashtags": hashtags,
                        "platform": platform,
                        "persona": selected_persona,
                        "char_count": actual_length,
                        "char_limit": char_limit,
                        "length_status": length_status,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "campaign_type": campaign_type,
                        "brand_tone": brand_tone
                    }
                    
                    st.session_state.generated_caption = result
                    st.session_state.generation_history.append(result)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results
    if st.session_state.generated_caption:
        result = st.session_state.generated_caption
        
        # Determine character count color
        if result['length_status'] == 'good':
            char_class = 'char-limit-good'
            char_icon = '✅'
        elif result['length_status'] == 'warning':
            char_class = 'char-limit-warning'
            char_icon = '⚠️'
        else:
            char_class = 'char-limit-exceeded'
            char_icon = '❌'
        
        st.markdown(f"""
        <div class="output-box">
            <h3>✅ Caption Ready!</h3>
            <p class="char-counter {char_class}">
                {char_icon} {result['char_count']}/{result['char_limit']} characters
            </p>
            <span class="persona-badge">🎭 {result['persona']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Warning if length exceeded
        if result['length_status'] == 'exceeded':
            st.warning(f"⚠️ Caption exceeds {result['char_limit']} character limit by {result['char_count'] - result['char_limit']} characters. Consider regenerating.")
        elif result['length_status'] == 'warning':
            st.info("💡 Caption is slightly over the recommended limit but may still work.")
        
        # Caption
        st.markdown("**📝 Your Caption:**")
        st.markdown(f'<div class="caption-text">{result["caption"]}</div>', unsafe_allow_html=True)
        
        # Hashtags
        st.markdown("**#️⃣ Research-Based Hashtags:**")
        st.markdown(f'<div class="hashtag-box">{" ".join(result["hashtags"])}</div>', unsafe_allow_html=True)
        st.caption("Based on TikTok Education NZ research (120-day analysis)")
        
        # Persona insights
        st.markdown("**🎯 Persona Insights Applied:**")
        persona_info = STUDENT_PERSONAS[result['persona']]
        
        insights_display = [
            f"👤 Target: {persona_info['demographics']}",
            f"💬 Tone: {persona_info['messaging_style']}",
            f"✨ Benefits: {persona_info['key_benefits']}",
            f"📱 Mobile-optimized: {photo_insights['mobile_pct']}% mobile users"
        ]
        
        for insight in insights_display:
            st.markdown(f'<div class="insight-badge">• {insight}</div>', unsafe_allow_html=True)
        
        # Export/Action buttons
        st.markdown("---")
        st.markdown("**💾 Export & Actions:**")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        export_txt = create_export_text(result)
        full_text_for_copy = f"{result['caption']}\n\n{' '.join(result['hashtags'])}"
        
        with col_btn1:
            st.download_button(
                label="📥 Download TXT",
                data=export_txt,
                file_name=f"caption_{result['persona'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_btn2:
            if st.button("📋 Copy Caption", use_container_width=True):
                st.code(full_text_for_copy, language=None)
                st.caption("👆 Click inside, Ctrl+A, then Ctrl+C to copy")
        
        with col_btn3:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.generated_caption = None
                st.rerun()
        
        # CSV export for history
        if len(st.session_state.generation_history) > 1:
            st.markdown("---")
            csv_data = create_export_csv(st.session_state.generation_history)
            st.download_button(
                label=f"📊 Export All ({len(st.session_state.generation_history)} captions) as CSV",
                data=csv_data,
                file_name=f"captions_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Content Synth AI v2.0</strong> | R.S.E Digital Labs</p>
    <p style="font-size: 0.85rem;">
        Powered by: Student Audience Personas • TikTok Education NZ Hashtag Research (120 days) •
        Caption Length Analysis (BR1) • Photography Business Analytics • Viral Trends • Clustering Data
    </p>
    <p style="font-size: 0.8rem; color: #999;">
        📚 Research-based • 🎯 Persona-driven • 📏 Length-enforced • #️⃣ Data-backed hashtags
    </p>
</div>
""", unsafe_allow_html=True)
