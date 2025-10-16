# content_synth_app.py - UPDATED VERSION
import streamlit as st
import anthropic
import pandas as pd
from datetime import datetime
from pathlib import Path
import json

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
    .output-box {data/
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
    .template-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONTENT TEMPLATES - Based on your analysis!
# ==========================================

CONTENT_TEMPLATES = {
    "Friday Educational Spotlight": {
        "optimal_day": "Friday",
        "engagement_multiplier": 7.86,
        "structure": {
            "hook": "Educational Hook",
            "learning_point": "Key Learning Point (1-2 sentences)",
            "cta": "Engagement question or challenge"
        },
        "description": "Leverage Friday's 7.86x engagement boost with educational content"
    },
    "Cross-Platform Educational Post": {
        "strategy": "Cross-platform posting",
        "performance_boost": "1033%",
        "structure": {
            "hook": "Benefit-driven opening",
            "value": "Specific educational value proposition",
            "cta": "Clear enrollment/action step"
        },
        "description": "1033% improvement from dual-platform posting"
    },
    "Mobile-First Student Engagement": {
        "mobile_optimization": "85.71%",
        "structure": {
            "hook": "Scroll-stopping question",
            "content": "Bite-sized learning tip",
            "cta": "Simple action (save, share, tag)"
        },
        "description": "Optimized for 85.71% mobile audience"
    },
    "Music/Arts Learning Content": {
        "top_interest": "music",
        "engagement": "10,000+",
        "structure": {
            "hook": "Music/arts connection",
            "learning": "How arts enhance learning",
            "cta": "Explore program/course"
        },
        "description": "Targets highest student interest (music)"
    },
    "Weekend Deep Dive": {
        "optimal_days": "Saturday/Sunday",
        "engagement_boost": "4.49",
        "structure": {
            "hook": "Weekend learning opportunity",
            "content": "Extended educational content (200-250 chars)",
            "cta": "Join weekend program/workshop"
        },
        "description": "Weekend engagement advantage (4.49 vs 4.10)"
    }
}

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
    
    top_days = day_engagement.nlargest(3)
    insights['best_days'] = list(top_days.index)
    
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
    
    insights['age_distribution'] = clustering_df['age_group'].value_counts().to_dict()
    
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
    
    hashtag_performance = viral_df.groupby('Hashtag')['Engagement_Rate'].mean().sort_values(ascending=False)
    insights['top_hashtags'] = hashtag_performance.head(10).to_dict()
    
    return insights

def get_relevant_hashtags(viral_insights, platform, campaign_type):
    """Get relevant hashtags based on viral trends data"""
    hashtags = ["#nzstudents", "#education", "#studentlife", "#studysmart"]
    
    top_hashtags = list(viral_insights['top_hashtags'].keys())
    
    if "Music" in campaign_type:
        hashtags.extend(["#StudyPlaylist", "#MusicLearning", "#AudioLearning"])
    elif "Dance" in campaign_type:
        hashtags.extend(["#DanceLearning", "#MovementStudy", "#KinestheticLearning"])
    else:
        hashtags.extend(["#CourseEnrollment", "#SkillBuilding", "#LearnOnTheGo"])
    
    platform_lower = platform.lower()
    if "instagram" in platform_lower:
        hashtags.extend(["#studygram", "#studentmotivation"])
    elif "tiktok" in platform_lower:
        hashtags.extend(["#studenttok", "#educationtok"])
    elif "facebook" in platform_lower:
        hashtags.extend(["#EducationFirst", "#LearningCommunity"])
    
    return hashtags[:12]

def select_best_template(campaign_type, day_of_week=None):
    """Select the most appropriate content template based on campaign and timing"""
    
    # Map campaign types to templates
    if "Music" in campaign_type or "Dance" in campaign_type:
        return "Music/Arts Learning Content"
    elif day_of_week and day_of_week.lower() == "friday":
        return "Friday Educational Spotlight"
    elif day_of_week and day_of_week.lower() in ["saturday", "sunday"]:
        return "Weekend Deep Dive"
    elif "Cross-Platform" in campaign_type:
        return "Cross-Platform Educational Post"
    else:
        return "Mobile-First Student Engagement"

def build_template_prompt(template_name, platform, campaign_type, audience, course_title, brand_tone, 
                         photo_insights, clustering_insights, viral_insights):
    """Build prompt using specific content template structure"""
    
    template = CONTENT_TEMPLATES[template_name]
    
    # Determine character limit
    platform_lower = platform.lower()
    if "instagram" in platform_lower or "tiktok" in platform_lower:
        char_limit = 150
    else:
        char_limit = 200
    
    # Build context
    context_parts = []
    context_parts.append(f"• Using template: {template_name}")
    context_parts.append(f"• Template strategy: {template.get('description', 'Data-driven approach')}")
    context_parts.append(f"• Friday posts achieve {photo_insights['friday_multiplier']}x higher engagement")
    context_parts.append(f"• {photo_insights['mobile_pct']}% of audience uses mobile devices")
    
    if clustering_insights['female_pct'] > 60:
        context_parts.append(f"• Target audience is {clustering_insights['female_pct']}% female")
    
    top_interest = list(clustering_insights['top_interests'].keys())[0]
    context_parts.append(f"• Primary audience interest: {top_interest}")
    
    context = "\n".join(context_parts)
    
    # Build structure guidance from template
    structure = template['structure']
    structure_guide = "\n".join([f"- {key.replace('_', ' ').title()}: {value}" for key, value in structure.items()])
    
    prompt = f"""You are Content Synth AI using proven content templates from real business data analysis.

CONTENT TEMPLATE: {template_name}
Template Structure:
{structure_guide}

DATA INSIGHTS:
{context}

Generate a {platform} caption for:
Campaign: {campaign_type}
Audience: {audience}
Course: {course_title}
Tone: {brand_tone}

REQUIREMENTS:
- Maximum {char_limit} characters
- {brand_tone.lower()} tone
- Follow the template structure above
- Lead with benefit/transformation
- Include natural call-to-action (5 words max)
- NO hashtags (provided separately)
- Mobile-optimized for {photo_insights['mobile_pct']}% mobile users

Write ONLY the caption text following the template structure:"""
    
    return prompt, template_name

# ==========================================
# EXPORT FUNCTIONS
# ==========================================

def create_export_text(result):
    """Create formatted text for export"""
    export_text = f"""=== CONTENT SYNTH AI - GENERATED CAPTION ===

Platform: {result['platform']}
Generated: {result['timestamp']}
Template: {result.get('template_used', 'N/A')}
Character Count: {result['char_count']}

CAPTION:
{result['caption']}

HASHTAGS:
{" ".join(result['hashtags'])}

DATA SOURCES APPLIED:
- Photography Business Analytics
- Viral Trends Data
- Clustering Marketing Data

KEY INSIGHTS:
{chr(10).join(result.get('insights_text', []))}

===================================
Generated by Content Synth AI | R.S.E Digital Labs
"""
    return export_text

def create_export_csv(results_list):
    """Create CSV export for multiple results"""
    df = pd.DataFrame([{
        'Timestamp': r['timestamp'],
        'Platform': r['platform'],
        'Template': r.get('template_used', 'N/A'),
        'Caption': r['caption'],
        'Hashtags': " ".join(r['hashtags']),
        'Character Count': r['char_count'],
        'Data Sources': ", ".join(r['data_sources_used'])
    } for r in results_list])
    
    return df.to_csv(index=False)

# ==========================================
# MAIN APP
# ==========================================

# Header
st.markdown("""
<div class="main-header">
    <h1>✨ Content Synth AI</h1>
    <p>R.S.E Digital Labs | Template-Based Social Media Caption Generator</p>
</div>
""", unsafe_allow_html=True)

# Load datasets
photo_df, clustering_df, viral_df, error = load_datasets()

if error:
    st.error(f"⚠️ Error loading datasets: {error}")
    st.info("💡 Make sure your data files are in the '/data' folder relative to this script!")
    st.stop()

# Extract insights
photo_insights = extract_photography_insights(photo_df)
clustering_insights = extract_clustering_insights(clustering_df)
viral_insights = extract_viral_insights(viral_df)

# Initialize session state
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

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
    
    with st.expander("📋 Content Templates Available"):
        for template_name, template_info in CONTENT_TEMPLATES.items():
            st.markdown(f"**{template_name}**")
            st.caption(template_info['description'])
            st.markdown("---")
    
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
        "📱 Platform",
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
    
    # Show recommended template
    recommended_template = select_best_template(campaign_type, "Friday")
    st.info(f"📋 Recommended Template: **{recommended_template}**")
    
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
    
    generate_clicked = st.button("✨ GENERATE CAPTION", type="primary", use_container_width=True)

with col2:
    st.markdown('<div class="section-header">📤 OUTPUT SECTION</div>', unsafe_allow_html=True)
    
    if generate_clicked:
        if not st.session_state.api_key:
            st.error("⚠️ Please enter your Claude API key in the sidebar!")
        else:
            with st.spinner("🤖 AI is using content templates and analyzing data..."):
                
                # Select and use template
                template_name = select_best_template(campaign_type, "Friday")
                
                # Build template-based prompt
                prompt, template_used = build_template_prompt(
                    template_name, platform, campaign_type, audience, course_title, brand_tone,
                    photo_insights, clustering_insights, viral_insights
                )
                
                # Get hashtags
                hashtags = get_relevant_hashtags(viral_insights, platform, campaign_type)
                
                try:
                    client = anthropic.Anthropic(api_key=st.session_state.api_key)
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    caption = message.content[0].text
                    
                    # Create insights text for export
                    insights_text = [
                        f"Template Used: {template_used}",
                        f"Friday engagement: {photo_insights['friday_multiplier']}x boost",
                        f"Mobile-first design: {photo_insights['mobile_pct']}% mobile usage",
                        f"Target audience: {clustering_insights['female_pct']}% female students",
                        f"{platform} engagement optimized"
                    ]
                    
                    # Store in session state
                    result = {
                        "caption": caption,
                        "hashtags": hashtags,
                        "platform": platform,
                        "char_count": len(caption),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_sources_used": ["Photography Business", "Viral Trends", "Clustering Marketing"],
                        "template_used": template_used,
                        "insights_text": insights_text,
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
        
        st.markdown(f"""
        <div class="output-box">
            <h3>✅ Caption & Hashtags Ready!</h3>
            <p style="color: #666;">({result['char_count']} characters)</p>
            <span class="template-badge">📋 Template: {result.get('template_used', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Caption
        st.markdown("**📝 Your Caption:**")
        st.markdown(f'<div class="caption-text">{result["caption"]}</div>', unsafe_allow_html=True)
        
        # Hashtags
        st.markdown("**#️⃣ Optimized Hashtags:**")
        st.markdown(f'<div class="hashtag-box">{" ".join(result["hashtags"])}</div>', unsafe_allow_html=True)
        
        # Data insights
        st.markdown("**📊 Data Insights Applied:**")
        
        insights_with_sources = [
            (f"Template: {result.get('template_used', 'N/A')}", "Template"),
            (f"Friday engagement: {photo_insights['friday_multiplier']}x boost", "Photography"),
            (f"Mobile-first: {photo_insights['mobile_pct']}% mobile", "Photography"),
            (f"Audience: {clustering_insights['female_pct']}% female", "Clustering"),
            (f"{result['platform']} optimized", "Viral Trends")
        ]
        
        for insight, source in insights_with_sources:
            st.markdown(f'<div class="insight-badge">• {insight}<span class="dataset-badge">{source}</span></div>', unsafe_allow_html=True)
        
        # Export/Action buttons
        st.markdown("---")
        st.markdown("**💾 Export & Actions:**")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        # Create exports
        export_txt = create_export_text(result)
        full_text_for_copy = f"{result['caption']}\n\n{' '.join(result['hashtags'])}"
        
        with col_btn1:
            st.download_button(
                label="📥 Download TXT",
                data=export_txt,
                file_name=f"caption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_btn2:
            # Copy button - show text area for manual copy
            if st.button("📋 Copy Caption", use_container_width=True):
                st.code(full_text_for_copy, language=None)
                st.caption("👆 Click inside the box above and press Ctrl+A then Ctrl+C")
        
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
    <p>Template-based generation powered by Photography Business Analytics, Viral Trends Data, and Clustered Marketing Data</p>
</div>
""", unsafe_allow_html=True)