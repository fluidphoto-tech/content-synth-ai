# content_synth_app.py
import streamlit as st
import anthropic
import pandas as pd
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Content Synth AI",
    page_icon="✨",
    layout="wide"
)

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
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA LOADING FUNCTIONS
# ==========================================

@st.cache_data
def load_datasets():
    """Load all 3 datasets and return them"""
    try:
        # Adjust paths based on your folder structure
        data_path = Path("../data")
        
        # Load Photography Business Data
        photo_df = pd.read_csv(data_path / "Photography_Business_Master_Analytics_With_PostingTimes.csv")
        
        # Load Clustering Marketing Data
        clustering_df = pd.read_excel(data_path / "Clustering_Marketing_FinalClean.xlsx")
        
        # Load Viral Trends Data
        viral_df = pd.read_excel(data_path / "Viral_Social_Media_Trends_FinalClean.xlsx")
        
        return photo_df, clustering_df, viral_df, None
    except Exception as e:
        return None, None, None, str(e)

@st.cache_data
def extract_photography_insights(photo_df):
    """Extract key insights from Photography Business Data"""
    insights = {}
    
    # Day of week performance
    day_engagement = photo_df.groupby('Day_of_Week')['Total_Social_Engagement'].mean()
    insights['friday_boost'] = day_engagement.get('Friday', 0)
    weekday_avg = day_engagement[['Monday', 'Tuesday', 'Wednesday', 'Thursday']].mean()
    insights['friday_multiplier'] = round(insights['friday_boost'] / weekday_avg, 2) if weekday_avg > 0 else 0
    
    # Mobile usage
    insights['mobile_pct'] = round(photo_df['Mobile_Percentage'].mean(), 2)
    
    # Cross-platform effectiveness
    cross_platform = photo_df[photo_df['Total_Posts_Today'] >= 2]['Total_Social_Engagement'].mean()
    single_platform = photo_df[photo_df['Total_Posts_Today'] == 1]['Total_Social_Engagement'].mean()
    insights['cross_platform_boost'] = round((cross_platform / single_platform - 1) * 100, 1) if single_platform > 0 else 0
    
    # Best posting days
    top_days = day_engagement.nlargest(3)
    insights['best_days'] = list(top_days.index)
    
    return insights

@st.cache_data
def extract_clustering_insights(clustering_df):
    """Extract key insights from Clustering Marketing Data"""
    insights = {}
    
    # Gender distribution
    gender_counts = clustering_df['gender'].value_counts()
    total_known = gender_counts.get('f', 0) + gender_counts.get('m', 0)
    insights['female_pct'] = round((gender_counts.get('f', 0) / total_known * 100), 2) if total_known > 0 else 0
    
    # Top interests
    interest_cols = ['music', 'dance', 'band', 'basketball', 'football', 'soccer', 'sports', 'rock']
    interest_totals = clustering_df[interest_cols].sum().sort_values(ascending=False)
    insights['top_interests'] = interest_totals.head(5).to_dict()
    
    # Age distribution
    insights['age_distribution'] = clustering_df['age_group'].value_counts().to_dict()
    
    return insights

@st.cache_data
def extract_viral_insights(viral_df):
    """Extract key insights from Viral Trends Data"""
    insights = {}
    
    # Calculate engagement rate
    viral_df['Engagement_Rate'] = ((viral_df['Likes'] + viral_df['Shares'] + viral_df['Comments']) / viral_df['Views'] * 100)
    
    # Platform performance
    platform_performance = viral_df.groupby('Platform')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['platform_engagement'] = platform_performance.to_dict()
    
    # Content type performance
    content_performance = viral_df.groupby('Content_Type')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['content_types'] = content_performance.to_dict()
    
    # Top hashtags by engagement
    hashtag_performance = viral_df.groupby('Hashtag')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['top_hashtags'] = hashtag_performance.head(10).to_dict()
    
    return insights

def get_relevant_hashtags(viral_insights, platform, campaign_type):
    """Get relevant hashtags based on viral trends data"""
    # Base education hashtags
    hashtags = ["#nzstudents", "#education", "#studentlife", "#studysmart"]
    
    # Add campaign-specific from top performing
    top_hashtags = list(viral_insights['top_hashtags'].keys())
    
    if "Music" in campaign_type:
        hashtags.extend(["#StudyPlaylist", "#MusicLearning", "#AudioLearning"])
    elif "Dance" in campaign_type:
        hashtags.extend(["#DanceLearning", "#MovementStudy", "#KinestheticLearning"])
    else:
        hashtags.extend(["#CourseEnrollment", "#SkillBuilding", "#LearnOnTheGo"])
    
    # Add platform-specific
    platform_lower = platform.lower()
    if "instagram" in platform_lower:
        hashtags.extend(["#studygram", "#studentmotivation"])
    elif "tiktok" in platform_lower:
        hashtags.extend(["#studenttok", "#educationtok"])
    elif "facebook" in platform_lower:
        hashtags.extend(["#EducationFirst", "#LearningCommunity"])
    
    return hashtags[:12]  # Limit to 12 hashtags

def build_data_driven_prompt(platform, campaign_type, audience, course_title, brand_tone, 
                             photo_insights, clustering_insights, viral_insights):
    """Build prompt using insights from all 3 datasets"""
    
    # Determine character limit based on platform and viral trends
    platform_lower = platform.lower()
    if "instagram" in platform_lower or "tiktok" in platform_lower:
        char_limit = 150
    else:
        char_limit = 200
    
    # Build context from all 3 datasets
    context_parts = []
    
    # Photography Business insights
    context_parts.append(f"• Friday posts achieve {photo_insights['friday_multiplier']}x higher engagement")
    context_parts.append(f"• {photo_insights['mobile_pct']}% of audience uses mobile devices")
    if photo_insights['cross_platform_boost'] > 0:
        context_parts.append(f"• Cross-platform posts show {photo_insights['cross_platform_boost']}% better performance")
    
    # Clustering insights (audience)
    if "student" in audience.lower() or "female" in audience.lower():
        context_parts.append(f"• Target audience is {clustering_insights['female_pct']}% female")
    
    top_interest = list(clustering_insights['top_interests'].keys())[0]
    context_parts.append(f"• Primary audience interest: {top_interest}")
    
    # Viral trends insights (platform-specific)
    if "instagram" in platform_lower:
        ig_engagement = viral_insights['platform_engagement'].get('instagram', 0)
        context_parts.append(f"• Instagram average engagement rate: {ig_engagement:.1f}%")
    elif "tiktok" in platform_lower:
        tt_engagement = viral_insights['platform_engagement'].get('tiktok', 0)
        context_parts.append(f"• TikTok average engagement rate: {tt_engagement:.1f}%")
    
    # Best content type
    best_content = list(viral_insights['content_types'].keys())[0]
    best_content_rate = viral_insights['content_types'][best_content]
    context_parts.append(f"• {best_content.capitalize()} format shows {best_content_rate:.1f}% engagement")
    
    context = "\n".join(context_parts)
    
    # Build the prompt
    prompt = f"""You are Content Synth AI, trained on real multi-source data:

DATA-DRIVEN INSIGHTS:
{context}

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
- Mobile-optimised for {photo_insights['mobile_pct']}% mobile users

Write ONLY the caption text:"""
    
    return prompt

# ==========================================
# MAIN APP
# ==========================================

# Header
st.markdown("""
<div class="main-header">
    <h1>✨ Content Synth AI</h1>
    <p>R.S.E Digital Labs | Data-Driven Social Media Caption Generator</p>
</div>
""", unsafe_allow_html=True)

# Load datasets
photo_df, clustering_df, viral_df, error = load_datasets()

if error:
    st.error(f"⚠️ Error loading datasets: {error}")
    st.info("💡 Make sure your data files are in the '../data' folder relative to this script!")
    st.stop()

# Extract insights from all datasets
photo_insights = extract_photography_insights(photo_df)
clustering_insights = extract_clustering_insights(clustering_df)
viral_insights = extract_viral_insights(viral_df)

# Initialize session state
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Sidebar
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
    st.markdown("### 📊 Live Data Sources")
    st.success(f"✅ Photography Business: {len(photo_df)} days")
    st.success(f"✅ Viral Trends: {len(viral_df)} posts")
    st.success(f"✅ Clustering Marketing: {len(clustering_df)} users")
    
    # Show a data insights tab
    with st.expander("🔍 View Data Insights"):
        st.markdown("**Photography Business:**")
        st.write(f"- Friday boost: {photo_insights['friday_multiplier']}x")
        st.write(f"- Mobile usage: {photo_insights['mobile_pct']}%")
        
        st.markdown("**Clustering Marketing:**")
        st.write(f"- Female audience: {clustering_insights['female_pct']}%")
        st.write(f"- Top interest: {list(clustering_insights['top_interests'].keys())[0]}")
        
        st.markdown("**Viral Trends:**")
        st.write(f"- Best platform: {list(viral_insights['platform_engagement'].keys())[0]}")
        st.write(f"- Best content: {list(viral_insights['content_types'].keys())[0]}")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">📝 INPUT SECTION</div>', unsafe_allow_html=True)
    
    platform = st.selectbox(
        "🔵 Platform",
        ["Instagram", "TikTok", "Facebook", "Cross-Platform (Instagram + TikTok + Facebook)"],
        help="Select your target platform"
    )
    
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
    
    audience = st.text_input(
        "🎯 Target Audience",
        value="University Students",
        help="Describe your target audience"
    )
    
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
    
    generate_clicked = st.button("✨ GENERATE", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📤 OUTPUT SECTION</div>', unsafe_allow_html=True)
    
    if generate_clicked:
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Claude API key in the sidebar!")
        else:
            with st.spinner("🤖 AI is analysing your data and crafting caption..."):
                
                # Build prompt using ALL 3 datasets
                prompt = build_data_driven_prompt(
                    platform, campaign_type, audience, course_title, brand_tone,
                    photo_insights, clustering_insights, viral_insights
                )
                
                # Get hashtags from viral trends
                hashtags = get_relevant_hashtags(viral_insights, platform, campaign_type)
                
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
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_sources_used": ["Photography Business", "Viral Trends", "Clustering Marketing"]
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
        st.markdown("**#️⃣ Optimised Hashtags:**")
        st.markdown(f'<div class="hashtag-box">{" ".join(result["hashtags"])}</div>', unsafe_allow_html=True)
        
        # Data insights applied with sources
        st.markdown("**📊 Data Insights Applied:**")
        
        insights_with_sources = [
            (f"Friday engagement: {photo_insights['friday_multiplier']}x boost", "Photography"),
            (f"Mobile-first design: {photo_insights['mobile_pct']}% mobile usage", "Photography"),
            (f"Target audience: {clustering_insights['female_pct']}% female students", "Clustering"),
            (f"{result['platform']} engagement optimised", "Viral Trends")
        ]
        
        for insight, source in insights_with_sources:
            st.markdown(f'<div class="insight-badge">• {insight}<span class="dataset-badge">{source}</span></div>', unsafe_allow_html=True)
        
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
    <p>Powered by real business data from Photography Business Analytics, Viral Trends Data, and Clustered Marketing Data</p>
</div>
""", unsafe_allow_html=True)