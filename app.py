import streamlit as st

# ============ PAGE CONFIG (Pehle aana chahiye) ============
st.set_page_config(
    page_title="AI Video Editor VIP",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ IMPORTS ============
import whisper
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import tempfile

# ============ CUSTOM CSS (VIP UI) ============
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1, h2, h3 {
        color: white !important;
        font-family: 'Poppins', sans-serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 8px 25px rgba(245,87,108,0.5);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(245,87,108,0.7);
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 50px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 50px;
        color: white;
        padding: 10px 30px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        box-shadow: 0 5px 20px rgba(245,87,108,0.5);
    }
    .stFileUploader {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 20px;
        border: 2px dashed rgba(255,255,255,0.4);
    }
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: 2px solid rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.9);
        padding: 12px;
    }
    .stSuccess, .stInfo {
        border-radius: 15px;
        border-left: 5px solid #00ff88;
    }
    .stSelectbox > div > div {
        border-radius: 15px;
        background: rgba(255,255,255,0.95);
    }
</style>
""", unsafe_allow_html=True)

# ============ TITLE ============
st.markdown("""
<h1 style='text-align: center; font-size: 3.5em; margin-bottom: 0;'>
    🎬 AI VIDEO EDITOR
</h1>
<p style='text-align: center; color: white; font-size: 1.3em; opacity: 0.9;'>
    ✨ Auto Captions • Templates • Backgrounds • Export ✨
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ============ SESSION STATE ============
if 'captions' not in st.session_state:
    st.session_state.captions = []
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'bg_path' not in st.session_state:
    st.session_state.bg_path = None
if 'template' not in st.session_state:
    st.session_state.template = {"color": "#00FF00", "style": "box"}

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["📹 Video Upload", "🎨 Templates", "🖼️ Background"])

# ---- TAB 1: VIDEO UPLOAD ----
with tab1:
    st.markdown("### 📹 Upload Your Video")
    video_file = st.file_uploader(
        "Choose video (MP4, MOV, AVI)",
        type=["mp4", "mov", "avi"],
        key="video_upload"
    )
    
    if video_file:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.write(video_file.read())
        st.session_state.video_path = temp_video.name
        
        st.success("✅ Video uploaded successfully!")
        st.video(st.session_state.video_path)
    
    st.markdown("---")
    st.markdown("### 🎤 Generate Captions")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Language", ["en", "ur", "hi", "ar"], index=0)
    with col2:
        model_size = st.selectbox("AI Model (bigger = better)", ["tiny", "base", "small"], index=1)
    
    if st.button("🚀 GENERATE CAPTIONS", key="gen_cap"):
        if st.session_state.video_path:
            with st.spinner("🎤 AI sun raha hai... Captions ban rahe hain..."):
                model = whisper.load_model(model_size)
                result = model.transcribe(
                    st.session_state.video_path,
                    language=language,
                    word_timestamps=True
                )
                
                all_words = []
                for seg in result["segments"]:
                    if "words" in seg:
                        for w in seg["words"]:
                            all_words.append({
                                "word": w["word"].strip(),
                                "start": w["start"],
                                "end": w["end"]
                            })
                
                st.session_state.captions = all_words
                st.success(f"✅ {len(all_words)} words ke captions ban gaye!")
                st.rerun()
        else:
            st.error("❌ Pehle video upload karo!")
    
    # Caption Editor
    if st.session_state.captions:
        st.markdown("---")
        st.markdown("### ✏️ Edit Captions")
        st.info("💡 Yahan captions ko theek kar sakte ho")
        
        edited = []
        for i, cap in enumerate(st.session_state.captions[:50]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_word = st.text_input(
                    f"Word {i+1}",
                    value=cap["word"],
                    key=f"word_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                st.write(f"⏱️ {cap['start']:.1f}s")
            with col3:
                st.write(f"→ {cap['end']:.1f}s")
            
            edited.append({
                "word": new_word,
                "start": cap["start"],
                "end": cap["end"]
            })
        
        st.session_state.captions = edited

# ---- TAB 2: TEMPLATES ----
with tab2:
    st.markdown("### 🎨 Choose Caption Template")
    st.write("Apna pasandeeda style choose karo:")
    
    templates = {
        "neon_green": {"name": "🟢 Neon Green", "color": "#00FF00"},
        "neon_pink": {"name": "🩷 Neon Pink", "color": "#FF00FF"},
        "neon_yellow": {"name": "🟡 Neon Yellow", "color": "#FFFF00"},
        "neon_cyan": {"name": "🔵 Neon Cyan", "color": "#00FFFF"},
        "white_bold": {"name": "⚪ White Bold", "color": "#FFFFFF"},
        "orange_pop": {"name": "🟠 Orange Pop", "color": "#FF6600"},
        "purple_glow": {"name": "💜 Purple Glow", "color": "#BF00FF"},
        "red_alert": {"name": "🔴 Red Alert", "color": "#FF0000"},
    }
    
    cols = st.columns(4)
    for i, (key, t) in enumerate(templates.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style='
                background: rgba(0,0,0,0.4);
                border-radius: 20px;
                padding: 30px 10px;
                text-align: center;
                margin: 10px 0;
                border: 2px solid {t["color"]};
                box-shadow: 0 0 20px {t["color"]}80;
            '>
                <p style='color: {t["color"]}; font-weight: bold; font-size: 1.2em;'>
                    {t["name"]}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    selected_template = st.selectbox(
        "Selected Template:",
        list(templates.keys()),
        format_func=lambda x: templates[x]["name"]
    )
    st.session_state.template = templates[selected_template]
    st.success(f"✅ Template: {templates[selected_template]['name']}")

# ---- TAB 3: BACKGROUND ----
with tab3:
    st.markdown("### 🖼️ Video Background")
    
    bg_type = st.radio(
        "Background Type:",
        ["🖼️ Custom Image", "🎨 Solid Color", "🌫️ Blur Video"],
        horizontal=True
    )
    
    if bg_type == "🖼️ Custom Image":
        bg_file = st.file_uploader(
            "Upload background image",
            type=["jpg", "jpeg", "png"],
            key="bg_upload"
        )
        if bg_file:
            temp_bg = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_bg.write(bg_file.read())
            st.session_state.bg_path = temp_bg.name
            st.image(st.session_state.bg_path, caption="Your Background", use_column_width=True)
            st.success("✅ Background set!")
    
    elif bg_type == "🎨 Solid Color":
        color = st.color_picker("Pick a color", "#1a1a2e")
        st.session_state.bg_color = color
        st.markdown(f"""
        <div style='background: {color}; height: 200px; border-radius: 20px;
                    border: 3px solid white; box-shadow: 0 0 30px {color};'>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("🌫️ Video ka blurred version background banega")
        st.session_state.bg_blur = True

# ============ EXPORT BUTTON ============
st.markdown("---")
st.markdown("""
<h2 style='text-align: center;'>🎬 Ready to Export?</h2>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ EXPORT VIDEO ✨", key="export"):
        if not st.session_state.video_path:
            st.error("❌ Pehle video upload karo!")
        elif not st.session_state.captions:
            st.error("❌ Pehle captions generate karo!")
        else:
            with st.spinner("🎬 Video ban rahi hai... 3-5 minute lagenge..."):
                try:
                    video = VideoFileClip(st.session_state.video_path)
                    
                    if video.duration > 420:
                        video = video.subclip(0, 420)
                    
                    target_w, target_h = 1080, 1920
                    video_h = int(target_h * 0.45)
                    video_resized = video.resize(height=video_h)
                    video_resized = video_resized.set_position(("center", "top"))
                    
                    captions = st.session_state.captions
                    template = st.session_state.get('template', {"color": "#00FF00"})
                    
                    caption_clips = []
                    chunk_size = 4
                    
                    for i in range(0, len(captions), chunk_size):
                        chunk = captions[i:i+chunk_size]
                        if not chunk:
                            continue
                        
                        for j, word_data in enumerate(chunk):
                            if word_data["start"] > 420:
                                break
                            
                            bg = Image.new('RGB', (target_w, target_h), (26, 26, 46))
                            draw = ImageDraw.Draw(bg)
                            
                            try:
                                font = ImageFont.truetype(
                                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                    80
                                )
                            except:
                                font = ImageFont.load_default()
                            
                            text = word_data["word"]
                            bbox = draw.textbbox((0, 0), text, font=font)
                            tw = bbox[2] - bbox[0]
                            x = (target_w - tw) // 2
                            y = int(target_h * 0.70)
                            
                            draw.text(
                                (x, y), text,
                                font=font,
                                fill=template["color"],
                                stroke_width=4,
                                stroke_fill="black"
                            )
                            
                            frame = np.array(bg)
                            clip = (ImageClip(frame)
                                    .set_start(word_data["start"])
                                    .set_end(min(word_data["end"], 420)))
                            caption_clips.append(clip)
                    
                    final = CompositeVideoClip(
                        caption_clips + [video_resized],
                        size=(target_w, target_h)
                    ).set_duration(video_resized.duration)
                    
                    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                    final.write_videofile(
                        output,
                        fps=30,
                        codec="libx264",
                        audio_codec="aac",
                        preset="ultrafast",
                        threads=4,
                        logger=None
                    )
                    
                    st.success("✅ Video ready!")
                    st.video(output)
                    
                    with open(output, "rb") as f:
                        st.download_button(
                            "📥 DOWNLOAD VIDEO",
                            f.read(),
                            file_name="edited_video.mp4",
                            mime="video/mp4"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center; color: white; opacity: 0.7;'>
    Made with ❤️ using Streamlit + Whisper AI
</p>
""", unsafe_allow_html=True)
