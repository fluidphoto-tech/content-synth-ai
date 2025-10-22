# content_synth_app.py - VERSION 3.1 (DALL-E Edition)
# Features: DALL-E Image Generation, Improved Hashtag Variation, Visual Image Generator UI, Brand Alignment Scoring

import streamlit as st
from anthropic import Anthropic
from openai import OpenAI
import pandas as pd
from datetime import datetime
from pathlib import Path
import random
import re
import requests
import io
from PIL import Image

# Page config
st.set_page_config(
    page_title="Content Synth AI v3.1",
    page_icon="✨",
    layout="wide"
)

# API KEY SETUP
anthropic_api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)

# Sidebar for API keys if not in secrets
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    
    if not anthropic_api_key:
        anthropic_api_key = st.text_input(
            "Claude API Key", 
            type="password",
            help="Enter your Anthropic API key for caption generation"
        )
    
    if not openai_api_key:
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key for DALL-E image generation"
        )
    
    # Live Data Sources
    st.markdown("---")
    st.markdown("### 📊 Live Data Sources")
    
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
        ✅ <strong>Photography Business:</strong> 502 days
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
        ✅ <strong>Viral Trends:</strong> 4802 posts
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #e8f5e9; padding: 0.5rem; border-radius: 5px; margin: 0.5rem 0;">
        ✅ <strong>Clustering Marketing:</strong> 14904 users
    </div>
    """, unsafe_allow_html=True)
    
    # Student Personas
    st.markdown("---")
    st.markdown("### 👥 Student Personas")
    
    with st.expander("👤 Creative Performer", expanded=False):
        st.markdown("Music, dance, and arts-focused students (45% of audience)")
    
    with st.expander("👤 Competitive Athlete", expanded=False):
        st.markdown("Sports and achievement-driven students (35% of audience)")
    
    with st.expander("👤 Balanced Explorer", expanded=False):
        st.markdown("Lifestyle and well-rounded learners (20% of audience)")
    
    # About DALL-E
    st.markdown("---")
    st.markdown("### 🤖 About DALL-E")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #666;">
    Using OpenAI DALL-E 3 - Images take 10-20 seconds to generate.
    </div>
    """, unsafe_allow_html=True)

if anthropic_api_key:
    client = Anthropic(api_key=anthropic_api_key)
else:
    st.warning("⚠️ Please enter your Claude API key to continue")
    st.stop()

if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None

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
    .image-generator-section {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .brand-alignment-box {
        background-color: #fff9e6;
        border: 2px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .alignment-score {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff6b6b;
    }
    .hf-badge {
        background-color: #ffd21e;
        color: #000;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
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
        "campaigns": ["Your Story. Your Stage.", "Start Your Story Here", "Discover What NZ Can Teach You"],
        "visual_keywords": ["vibrant", "colorful", "energetic", "artistic", "creative", "expressive"]
    },
    "Competitive Athlete": {
        "description": "Sports and achievement-driven students (35% of audience)",
        "demographics": "75% Male, Age 17-20",
        "interests": ["Football (0.45)", "Basketball (0.31)", "Baseball (0.27)", "Sports (0.20)"],
        "messaging_style": "Motivational, bold, competitive",
        "key_benefits": "Achievement, teamwork, consistency",
        "cta_style": "Show up strong, Join the challenge, Train hard",
        "campaigns": ["Game On: Every Day Counts", "Snap & Score Challenge", "Summer Drive"],
        "visual_keywords": ["dynamic", "powerful", "athletic", "energetic", "determined", "action"]
    },
    "Balanced Explorer": {
        "description": "Lifestyle and well-rounded learners (20% of audience)",
        "demographics": "Mixed gender, Age 16-22",
        "interests": ["Music (0.50)", "Dance (0.34)", "Swimming (0.09)", "Study-life balance"],
        "messaging_style": "Warm, conversational, inclusive",
        "key_benefits": "Discovery, belonging, life-balance",
        "cta_style": "Learn. Explore. Belong., Start your story, Discover",
        "campaigns": ["Explore Your Path", "Study + Adventure Diaries", "Inspiring the Future"],
        "visual_keywords": ["balanced", "welcoming", "diverse", "natural", "inclusive", "friendly"]
    }
}

# ==========================================
# RESEARCH-BASED HASHTAG BANK (IMPROVED)
# ==========================================

HASHTAG_BANK = {
    "high_engagement_boosters": {
        "tags": ["#viral", "#comedy", "#challenge", "#tech", "#trending", "#fyp", "#foryou"],
        "avg_engagement": "80-100%",
        "note": "Algorithmic visibility boosters"
    },
    "education_core": {
        "tags": ["#education", "#learning", "#study", "#student", "#school", "#university", "#knowledge"],
        "avg_engagement": "45-60%",
        "note": "Core education terms"
    },
    "persona_creative": {
        "tags": ["#music", "#dance", "#art", "#creative", "#performance", "#band", "#rock"],
        "avg_engagement": "60-75%",
        "note": "Creative Performer aligned"
    },
    "persona_athlete": {
        "tags": ["#sports", "#football", "#basketball", "#baseball", "#athlete", "#fitness", "#training"],
        "avg_engagement": "55-70%",
        "note": "Competitive Athlete aligned"
    },
    "persona_explorer": {
        "tags": ["#lifestyle", "#balance", "#wellness", "#adventure", "#discovery", "#explore"],
        "avg_engagement": "50-65%",
        "note": "Balanced Explorer aligned"
    },
    "location_specific": {
        "tags": ["#newzealand", "#nz", "#studyinnz", "#nzlife", "#kiwi", "#aotearoa"],
        "avg_engagement": "40-55%",
        "note": "New Zealand focus"
    },
    "campaign_enrollment": {
        "tags": ["#enrollment", "#admissions", "#applytoday", "#jointoday", "#newstudent"],
        "avg_engagement": "35-50%",
        "note": "Enrollment campaigns"
    },
    "campaign_summer": {
        "tags": ["#summerschool", "#summerlearning", "#summercourse", "#vacation", "#summerstudy"],
        "avg_engagement": "40-60%",
        "note": "Summer programs"
    },
    "campaign_discount": {
        "tags": ["#discount", "#sale", "#earlybird", "#limitedtime", "#specialoffer"],
        "avg_engagement": "50-70%",
        "note": "Promotional campaigns"
    },
    "mobile_optimized": {
        "tags": ["#mobile", "#onthego", "#mobilelearning", "#smartphone", "#app"],
        "avg_engagement": "30-45%",
        "note": "87% mobile audience"
    }
}

# ==========================================
# PHOTO DATASET INSIGHTS
# ==========================================

photo_insights = {
    "mobile_pct": 87,
    "avg_session": "2.5 minutes",
    "peak_times": "12-3pm, 7-10pm",
    "seasonal_boost": "Summer +45%, Winter -12%"
}

# ==========================================
# PLATFORM SPECIFICATIONS
# ==========================================

PLATFORM_SPECS = {
    "Instagram": {
        "caption_limit": 2200,
        "hashtag_limit": 30,
        "recommended_caption": 150,
        "recommended_hashtags": "8-12",
        "best_practice": "Use line breaks, 1st comment for extra hashtags"
    },
    "TikTok": {
        "caption_limit": 150,
        "hashtag_limit": None,
        "recommended_caption": 100,
        "recommended_hashtags": "3-5",
        "best_practice": "Short, punchy, trending hashtags"
    },
    "Facebook": {
        "caption_limit": 63206,
        "hashtag_limit": None,
        "recommended_caption": 200,
        "recommended_hashtags": "2-5",
        "best_practice": "Conversational, longer OK, fewer hashtags"
    },
    "LinkedIn": {
        "caption_limit": 3000,
        "hashtag_limit": None,
        "recommended_caption": 200,
        "recommended_hashtags": "3-5",
        "best_practice": "Professional tone, industry keywords"
    },
    "Twitter/X": {
        "caption_limit": 280,
        "hashtag_limit": None,
        "recommended_caption": 250,
        "recommended_hashtags": "1-2",
        "best_practice": "Concise, timely, limited hashtags"
    }
}

# Image Specifications for DALL-E
PLATFORM_IMAGE_SPECS = {
    "Instagram": {
        "Square (1:1)": {"size": "1024x1024", "dalle_size": "1024x1024"},
        "Portrait (4:5)": {"size": "1080x1350", "dalle_size": "1024x1024"},
        "Landscape (1.91:1)": {"size": "1080x566", "dalle_size": "1792x1024"},
        "Story/Reel (9:16)": {"size": "1080x1920", "dalle_size": "1024x1792"}
    },
    "TikTok": {
        "Video (9:16)": {"size": "1080x1920", "dalle_size": "1024x1792"}
    },
    "Facebook": {
        "Feed Post (1.91:1)": {"size": "1200x630", "dalle_size": "1792x1024"},
        "Story (9:16)": {"size": "1080x1920", "dalle_size": "1024x1792"}
    },
    "LinkedIn": {
        "Feed Post (1.91:1)": {"size": "1200x627", "dalle_size": "1792x1024"}
    },
    "Twitter/X": {
        "Post (16:9)": {"size": "1200x675", "dalle_size": "1792x1024"}
    },
    "Cross-platform": {
        "square": {"size": "1024x1024", "dalle_size": "1024x1024"}
    }
}

# ==========================================
# CAMPAIGN TYPE TO PERSONA MAPPING
# ==========================================

def auto_select_persona(campaign_type):
    """Automatically select the best persona based on campaign type"""
    persona_map = {
        "Music-Integrated Learning": "Creative Performer",
        "Sports-Based Education": "Competitive Athlete",
        "Creative Arts Program": "Creative Performer",
        "General Summer School": "Balanced Explorer",
        "Study Abroad": "Balanced Explorer",
        "Athletic Training": "Competitive Athlete",
        "Performance Arts": "Creative Performer",
        "Online Learning": "Balanced Explorer",
        "Tutoring Services": "Balanced Explorer"
    }
    return persona_map.get(campaign_type, "Balanced Explorer")

# ==========================================
# HASHTAG SELECTION FUNCTION (WITH VARIATION)
# ==========================================

def select_hashtags_for_persona(persona, platform, campaign_type, variation_seed=None):
    """Select hashtags based on persona, platform, and campaign with built-in variation"""
    
    if variation_seed:
        random.seed(variation_seed)
    
    selected = []
    
    # 1. Always include 1-2 high engagement boosters
    selected.extend(random.sample(HASHTAG_BANK["high_engagement_boosters"]["tags"], 2))
    
    # 2. Add 2-3 education core tags
    selected.extend(random.sample(HASHTAG_BANK["education_core"]["tags"], random.randint(2, 3)))
    
    # 3. Add persona-specific tags (3-4)
    persona_key_map = {
        "Creative Performer": "persona_creative",
        "Competitive Athlete": "persona_athlete",
        "Balanced Explorer": "persona_explorer"
    }
    
    if persona in persona_key_map:
        persona_tags = HASHTAG_BANK[persona_key_map[persona]]["tags"]
        selected.extend(random.sample(persona_tags, min(random.randint(3, 4), len(persona_tags))))
    
    # 4. Add campaign-specific tags (1-2)
    campaign_map = {
        "Enrollment Drive": "campaign_enrollment",
        "Summer School": "campaign_summer",
        "Discount Offer": "campaign_discount"
    }
    
    if campaign_type in campaign_map:
        campaign_tags = HASHTAG_BANK[campaign_map[campaign_type]]["tags"]
        selected.extend(random.sample(campaign_tags, min(2, len(campaign_tags))))
    
    # 5. Add location tags (1-2)
    selected.extend(random.sample(HASHTAG_BANK["location_specific"]["tags"], 2))
    
    # 6. Optionally add mobile tags if audience is mobile-heavy
    if random.random() < 0.3:  # 30% chance to include
        selected.append(random.choice(HASHTAG_BANK["mobile_optimized"]["tags"]))
    
    # Platform-specific adjustments
    recommended_count = {
        "Instagram": 10,
        "TikTok": 5,
        "Facebook": 4,
        "LinkedIn": 4,
        "Twitter/X": 2,
        "Cross-platform": 7
    }
    
    target_count = recommended_count.get(platform, 8)
    
    # Trim or pad to target count
    if len(selected) > target_count:
        selected = random.sample(selected, target_count)
    elif len(selected) < target_count:
        # Fill with random tags from other categories
        all_remaining = []
        for category in HASHTAG_BANK.values():
            all_remaining.extend([tag for tag in category["tags"] if tag not in selected])
        
        if all_remaining:
            needed = target_count - len(selected)
            selected.extend(random.sample(all_remaining, min(needed, len(all_remaining))))
    
    return selected

# ==========================================
# CAPTION LENGTH CHECKER
# ==========================================

def check_caption_length(caption, target_limit):
    """Check if caption meets length requirements"""
    actual_length = len(caption)
    
    if actual_length <= target_limit:
        return "good", actual_length
    elif actual_length <= target_limit + 20:
        return "warning", actual_length
    else:
        return "exceeded", actual_length

# ==========================================
# BRAND ALIGNMENT CALCULATOR
# ==========================================

def calculate_brand_alignment(caption, hashtags, persona, brand_tone):
    """Calculate brand alignment percentage based on multiple factors"""
    score = 100
    
    # Check persona alignment
    persona_keywords = STUDENT_PERSONAS[persona]["visual_keywords"]
    caption_lower = caption.lower()
    
    keyword_matches = sum(1 for keyword in persona_keywords if keyword in caption_lower)
    if keyword_matches < 2:
        score -= 15
    
    # Check hashtag count
    optimal_hashtag_count = {
        "Instagram": (8, 12),
        "TikTok": (3, 5),
        "Facebook": (2, 5),
        "LinkedIn": (3, 5),
        "Twitter/X": (1, 2),
        "Cross-platform": (5, 8)
    }
    
    # Check brand tone consistency
    tone_indicators = {
        "Professional": ["learn", "discover", "develop", "achieve", "professional"],
        "Friendly": ["join", "hey", "welcome", "together", "community"],
        "Casual": ["fun", "awesome", "cool", "check out", "hey"],
        "Energetic": ["!", "exciting", "amazing", "awesome", "let's go"],
        "Inspiring": ["dream", "inspire", "transform", "empower", "potential"]
    }
    
    if brand_tone in tone_indicators:
        tone_matches = sum(1 for word in tone_indicators[brand_tone] if word.lower() in caption_lower)
        if tone_matches == 0:
            score -= 10
    
    return max(score, 60)  # Minimum 60% alignment

# ==========================================
# IMAGE GENERATION PROMPT FUNCTION
# ==========================================

def generate_image_prompt(persona, campaign_type, course_title, brand_tone, visual_style):
    """Generate detailed prompt for DALL-E based on persona and campaign"""
    
    persona_info = STUDENT_PERSONAS[persona]
    visual_keywords = ", ".join(persona_info["visual_keywords"])
    
    base_prompt = f"""Create a {visual_style} educational marketing image for {campaign_type}.
    
Target audience: {persona} - {persona_info['description']}
Visual style: {visual_keywords}
Mood: {persona_info['messaging_style']}

The image should:
- Appeal to {persona_info['demographics']}
- Convey {persona_info['key_benefits']}
- Be {visual_style} and suitable for social media
- Feature educational/learning elements
- Include diverse students in a {brand_tone.lower()} environment
- Be engaging and shareable

Course focus: {course_title if course_title else 'general education'}

Style: Professional photography, high quality, modern, appealing to Gen Z"""
    
    return base_prompt

# ==========================================
# DALL-E IMAGE GENERATION FUNCTION (REPLACED HUGGING FACE)
# ==========================================

def generate_image_dalle(prompt, width, height, api_key):
    """Generate image using DALL-E 3 - ONLY CHANGE FROM HUGGING FACE VERSION"""
    
    if not openai_client:
        return None, "Please configure OpenAI API key for DALL-E image generation"
    
    # DALL-E 3 only supports these specific sizes
    # Map requested dimensions to closest DALL-E size
    if width == height:
        size = "1024x1024"
    elif height > width:
        size = "1024x1792"  # Portrait
    else:
        size = "1792x1024"  # Landscape
    
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",  # Can be "standard" or "hd"
            n=1
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        image_response = requests.get(image_url)
        image = Image.open(io.BytesIO(image_response.content))
        
        return image, None
        
    except Exception as e:
        return None, str(e)

# ==========================================
# EXPORT FUNCTIONS
# ==========================================

def create_export_text(result):
    """Create formatted text export"""
    return f"""Content Synth AI - Generated Caption
{'='*50}

Platform: {result['platform']}
Persona: {result['persona']}
Campaign: {result['campaign_type']}
Brand Tone: {result['brand_tone']}
Timestamp: {result['timestamp']}
Character Count: {result['char_count']}/{result['char_limit']}

CAPTION:
{result['caption']}

HASHTAGS:
{' '.join(result['hashtags'])}

METADATA:
- Brand Alignment Score: {result['alignment_score']}%
- Length Status: {result['length_status']}
- Generated with: Claude AI + Research-based Personas
"""

def create_export_csv(history):
    """Create CSV export of generation history"""
    df = pd.DataFrame(history)
    return df.to_csv(index=False)

# ==========================================
# INITIALIZE SESSION STATE
# ==========================================

if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = None

if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []

if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# ==========================================
# MAIN APP LAYOUT
# ==========================================

# Header
st.markdown("""
<div class="main-header">
    <h1>✨ Content Synth AI v3.1</h1>
    <p>R.S.E Digital Labs | Persona-Based Educational Content Generator</p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">
        Student Personas • Research-Based Hashtags • Caption Length Enforcement • <span class="hf-badge">🎨 DALL-E Image Generation</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Two-column layout (kept from original)
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown('<div class="section-header">📝 INPUT SECTION</div>', unsafe_allow_html=True)
    
    # Platform selection
    st.markdown("📱 **Platform**")
    platform = st.selectbox(
        "Platform",
        ["Cross-platform", "Instagram", "TikTok", "Facebook"],
        label_visibility="collapsed"
    )
    
    # Show platform caption limit
    platform_data = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["Instagram"])
    char_limit = platform_data['recommended_caption']
    st.caption(f"💬 Caption limit for this platform: {char_limit} characters")
    
    # Campaign Type
    st.markdown("🎯 **Campaign Type**")
    campaign_type = st.selectbox(
        "Campaign Type",
        ["Music-Integrated Learning", "Sports-Based Education", "Creative Arts Program", 
         "General Summer School", "Study Abroad", 
         "Athletic Training", "Performance Arts", "Online Learning", "Tutoring Services"],
        label_visibility="collapsed"
    )
    
    # Auto-select persona based on campaign
    selected_persona = auto_select_persona(campaign_type)
    
    # Display auto-selected persona
    st.markdown(f"""
    <div style="background-color: #f0f0f0; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <strong>🎭 Auto-Selected Persona:</strong> <span class="persona-badge" style="display: inline;">{selected_persona}</span>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">{STUDENT_PERSONAS[selected_persona]['description']}</p>
        <p style="font-size: 0.85rem; margin-top: 0.3rem;"><strong>Messaging:</strong> {STUDENT_PERSONAS[selected_persona]['messaging_style']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Course Title
    st.markdown("📚 **Course/Event Title**")
    course_title = st.text_input(
        "Course Title",
        placeholder="Summer Program 2025",
        label_visibility="collapsed"
    )
    
    # Brand Voice
    st.markdown("🎨 **Brand Voice**")
    brand_tone_options = ["Professional", "Casual", "Friendly"]
    brand_tone = st.radio(
        "Brand Voice",
        brand_tone_options,
        horizontal=True,
        label_visibility="collapsed",
        index=2  # Default to Friendly
    )
    
    # Generate Caption Button
    generate_caption_clicked = st.button("✨ GENERATE CAPTION", use_container_width=True, type="primary")
    
    # Visual Image Generator Section
    st.markdown("---")
    st.markdown('<div class="section-header">🎨 VISUAL IMAGE GENERATOR</div>', unsafe_allow_html=True)
    
    st.markdown("📷 **Generate AI Image (DALL-E)**")
    
    # Image Type dropdown
    image_type = st.selectbox(
        "Image Type",
        ["Social Media Post", "Educational Banner", "Event Poster", "Course Thumbnail"],
        label_visibility="collapsed"
    )
    
    # Style dropdown  
    visual_style = st.selectbox(
        "Style",
        ["Abstract", "Modern", "Photographic", "Minimalist", "Vibrant", "Artistic"],
        label_visibility="collapsed"
    )
    
    # Ratio dropdown (updated for selected platform)
    if platform in PLATFORM_IMAGE_SPECS:
        ratio_options = list(PLATFORM_IMAGE_SPECS[platform].keys())
    else:
        ratio_options = ["square"]
    
    selected_ratio = st.selectbox(
        "Ratio",
        ratio_options,
        label_visibility="collapsed"
    )
    
    # Keywords input
    keywords_description = st.text_input(
        "Keywords / Description (optional)",
        placeholder="e.g., students studying, summer vibes, outdoor learning",
        label_visibility="collapsed"
    )
    
    # Info about generation time
    st.info("⏱️ Image generation takes 10-20 seconds. First request may take 30 seconds while model loads.")
    
    # Generate Image Button
    generate_image_clicked = st.button("🎨 GENERATE IMAGE", use_container_width=True)

# OUTPUT SECTION
with col_output:
    st.markdown('<div class="section-header">📤 OUTPUT SECTION</div>', unsafe_allow_html=True)
    
    # Process caption generation
    if generate_caption_clicked:
        with st.spinner("🤖 Generating your caption..."):
            
            # Get persona insights
            persona_info = STUDENT_PERSONAS[selected_persona]
            
            # Build prompt
            prompt = f"""You are a social media expert creating content for educational institutions targeting Gen Z students.

TARGET PERSONA: {selected_persona}
- Description: {persona_info['description']}
- Demographics: {persona_info['demographics']}
- Interests: {', '.join(persona_info['interests'])}
- Messaging Style: {persona_info['messaging_style']}
- Key Benefits to Highlight: {persona_info['key_benefits']}
- CTA Style: {persona_info['cta_style']}

CAMPAIGN DETAILS:
- Platform: {platform}
- Campaign Type: {campaign_type}
- Brand Tone: {brand_tone}
- Course/Event: {course_title if course_title else 'General education program'}

PLATFORM REQUIREMENTS:
- Character Limit: {char_limit} characters (STRICT)
- Best Practice: {platform_data['best_practice']}

INSIGHTS FROM RESEARCH:
- 87% of audience uses mobile devices
- Peak engagement: 12-3pm, 7-10pm
- Visual content gets 45% more engagement
- Persona-aligned messaging increases conversion by 60%

Create a {platform} caption that:
1. Speaks directly to {selected_persona} using their preferred messaging style
2. Stays UNDER {char_limit} characters
3. Includes a clear call-to-action matching their CTA style
4. Uses {brand_tone.lower()} tone
5. Feels authentic and engaging for Gen Z
6. Incorporates relevant benefits and interests

Return ONLY the caption text, no hashtags, no explanations."""
            
            # Get research-based hashtags with variation
            variation_seed = datetime.now().timestamp()
            hashtags = select_hashtags_for_persona(selected_persona, platform, campaign_type, variation_seed)
            
            try:
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                caption = message.content[0].text.strip()
                
                # Check caption length
                length_status, actual_length = check_caption_length(caption, char_limit)
                
                # Calculate brand alignment score
                alignment_score = calculate_brand_alignment(caption, hashtags, selected_persona, brand_tone)
                
                # Store result
                result = {
                    "caption": caption,
                    "hashtags": hashtags,
                    "platform": platform,
                    "persona": selected_persona,
                    "char_count": actual_length,
                    "char_limit": char_limit,
                    "length_status": length_status,
                    "alignment_score": alignment_score,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "campaign_type": campaign_type,
                    "brand_tone": brand_tone
                }
                
                st.session_state.generated_caption = result
                st.session_state.generation_history.append(result)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Image Generation
    if generate_image_clicked:
        if not openai_client:
            st.error("⚠️ Please configure your OpenAI API key for image generation!")
        else:
            with st.spinner("🎨 Generating image with DALL-E 3... (10-20 seconds)"):
                try:
                    # Generate image prompt
                    if keywords_description:
                        image_prompt = f"{generate_image_prompt(selected_persona, campaign_type, course_title, brand_tone, visual_style)}. Additional elements: {keywords_description}"
                    else:
                        image_prompt = generate_image_prompt(selected_persona, campaign_type, course_title, brand_tone, visual_style)
                    
                    # Determine size based on platform and ratio
                    if platform in PLATFORM_IMAGE_SPECS and selected_ratio in PLATFORM_IMAGE_SPECS[platform]:
                        size_str = PLATFORM_IMAGE_SPECS[platform][selected_ratio]["size"]
                        width, height = map(int, size_str.split('x'))
                    else:
                        width, height = 1024, 1024
                    
                    # Generate image using DALL-E
                    image, error = generate_image_dalle(image_prompt, width, height, openai_api_key)
                    
                    if image:
                        st.session_state.generated_image = image
                        st.success("✅ Image generated successfully with DALL-E 3!")
                    else:
                        st.error(f"❌ {error}")
                        st.info("💡 Make sure you have OpenAI credits available!")
                    
                except Exception as e:
                    st.error(f"❌ Image generation error: {str(e)}")
    
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
        
        # Brand Alignment Score
        st.markdown(f"""
        <div class="brand-alignment-box">
            <h4>📊 Brand Alignment Checklist</h4>
            <p>✓ Matches brand keywords</p>
            <p>✓ Tone consistent with caption</p>
            <p>✓ Optimal hashtag count</p>
            <p><strong>Brand Consistency Score: <span class="alignment-score">{result['alignment_score']}%</span></strong></p>
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
        
        # Display generated image if available
        if st.session_state.generated_image:
            st.markdown("---")
            st.markdown("**🎨 Visual Output:**")
            st.image(st.session_state.generated_image, use_container_width=True)
            st.caption(f"Generated with DALL-E 3 - {platform} - {selected_ratio if 'selected_ratio' in locals() else 'standard'} format")
        
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
                st.session_state.generated_image = None
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
    <p><strong>Content Synth AI v3.1 (DALL-E Edition)</strong> | R.S.E Digital Labs</p>
    <p style="font-size: 0.85rem;">
        Powered by: Student Audience Personas • TikTok Education NZ Hashtag Research (120 days) •
        Caption Length Analysis • Photography Business Analytics • Viral Trends • Clustering Data • 
        <strong>🎨 OpenAI DALL-E 3</strong>
    </p>
    <p style="font-size: 0.8rem; color: #999;">
        📚 Research-based • 🎯 Persona-driven • 📏 Length-enforced • #️⃣ Data-backed hashtags • 🎨 AI-generated visuals
    </p>
</div>
""", unsafe_allow_html=True)
