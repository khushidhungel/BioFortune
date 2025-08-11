# biofortune_app.py
# Modern BioFortune (Streamlit) — Mood tracker, Eye exercise, Animated, AI fallback
# Run: streamlit run biofortune_app.py

import streamlit as st
import google.generativeai as genai
import time
import os
from PIL import Image
import requests
from io import BytesIO

# -------------------------
# CONFIG & SAFETY
# -------------------------
st.set_page_config(page_title="BioFortune", page_icon="🌿", layout="centered")

# Try to configure Gemini; show a friendly message if secrets missing
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    # For local testing you can set environment variable 'GEMINI_API_KEY'
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    else:
        # We'll still let the app run but AI will be disabled until the key is present
        genai = None

# -------------------------
# Styles (soft green theme + simple animation)
# -------------------------
st.markdown(
    """
    <style>
    :root{
      --accent:#6fbf73;
      --accent-2:#8fd6a6;
      --bg:#ecf7ee;
      --card:#ffffff;
    }
    .stApp {
      background: linear-gradient(180deg, var(--bg) 0%, #f7fff7 100%);
      color: #123;
      font-family: 'Poppins', sans-serif;
    }
    .hero {
      background: linear-gradient(90deg, rgba(111,191,115,0.12), rgba(143,214,166,0.08));
      padding: 18px;
      border-radius: 14px;
      box-shadow: 0 6px 18px rgba(9,30,9,0.06);
      margin-bottom: 12px;
    }
    .mood-btn {
      font-size:22px;
      padding:8px 12px;
      border-radius:10px;
      margin:4px;
      border: none;
      cursor:pointer;
    }
    .card {
      background: var(--card);
      border-radius:12px;
      padding:14px;
      box-shadow: 0 4px 16px rgba(9,30,9,0.04);
    }
    .small-muted { color: #556; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helper Data & Functions
# -------------------------
# (Your extended herbal_db — add more as you like)
herbal_db = {
    "stress": {
        "english_name": "Tulsi (Holy Basil)",
        "nepali_name": "तुलसी",
        "image": "tulsi.jpg",
        "remedy": "Drink tulsi tea twice a day.",
        "pros": ["Reduces stress", "Boosts immunity"],
        "cons": ["Avoid if pregnant", "May lower blood sugar"]
    },
    "fatigue": {
        "english_name": "Ashwagandha",
        "nepali_name": "अश्वगन्धा",
        "image": "ashwagandha.jpg",
        "remedy": "Take 1 tsp of ashwagandha powder with warm milk at night.",
        "pros": ["Boosts energy", "Improves sleep"],
        "cons": ["Avoid during pregnancy"]
    },
    "indigestion": {
        "english_name": "Ginger",
        "nepali_name": "अदुवा",
        "image": "ginger.jpg",
        "remedy": "Boil ginger in water and drink after meals.",
        "pros": ["Improves digestion", "Reduces nausea"],
        "cons": ["May cause heartburn if taken in excess"]
    },
    "diarrhea": {
        "english_name": "Pomegranate Peel",
        "nepali_name": "अनारको बोक्रा",
        "image": "pomegranate.jpg",
        "remedy": "Boil peel in water and sip slowly.",
        "pros": ["Reduces loose motion", "Antibacterial"],
        "cons": ["Avoid if constipated"]
    },
    "eye strain": {
        "english_name": "Triphala",
        "nepali_name": "त्रिफला",
        "image": "triphala.jpg",
        "remedy": "Wash eyes with cooled Triphala decoction.",
        "pros": ["Improves eye health", "Reduces dryness"],
        "cons": ["May cause temporary stinging"]
    },
    "headache": {
        "english_name": "Peppermint",
        "nepali_name": "पुदिना",
        "image": "peppermint.jpg",
        "remedy": "Apply diluted peppermint oil to the temples.",
        "pros": ["Relieves headache", "Cools the skin"],
        "cons": ["Can cause irritation if not diluted"]
    },
    "joint pain": {
        "english_name": "Turmeric",
        "nepali_name": "बेसार",
        "image": "turmeric.jpg",
        "remedy": "Mix turmeric with warm milk and drink.",
        "pros": ["Anti-inflammatory", "Eases pain"],
        "cons": ["May cause upset stomach in high doses"]
    }
}

CRITICAL = [
    "chest pain", "fainting", "severe bleeding", "unconscious",
    "shortness of breath", "severe abdominal pain"
]

def lookup_remedy(symptom_text):
    low = symptom_text.lower()
    # exact keyword match first
    for key, val in herbal_db.items():
        if key in low:
            return {"status": "ok", "remedy": val}
    # check critical
    for c in CRITICAL:
        if c in low:
            return {"status":"critical", "message": "Your symptoms seem serious. Please consult a doctor immediately."}
    return {"status":"not_found", "message": "Not found in local database."}

def safe_image(path, width=200):
    """Return an st.image-capable object, fallback if missing."""
    try:
        if path.startswith("http"):
            resp = requests.get(path, timeout=6)
            img = Image.open(BytesIO(resp.content))
        else:
            img = Image.open(path)
        return img
    except Exception:
        # Use a simple placeholder (colored box)
        return None

def ask_genai(symptom):
    """Call Gemini model - uses gemini-2.5-flash-lite by default."""
    if genai is None:
        return "AI not configured. Add GEMINI_API_KEY to secrets to enable AI suggestions."
    prompt = f"""
You are a friendly Nepali herbal medicine assistant. The user reports: "{symptom}".
Give a short recommendation with:
- Herb name (English and Nepali)
- Simple dosage / how to use
- Pros and cons (2-3 each)
- When to see a doctor (if any)
Keep it concise (max ~180 words).
"""
    try:
        # Use flash-lite for speed and higher limits
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {e}"

# -------------------------
# Session State init
# -------------------------
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []  # list of tuples (timestamp, mood_label)

if "entered" not in st.session_state:
    st.session_state.entered = False  # whether user completed pre-check (mood + eye)

# -------------------------
# WELCOME / PRECHECK PAGE
# -------------------------
def precheck():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown("## 🌿 Welcome to **BioFortune**")
    st.markdown("A friendly herbal advisor — personal, Nepali-focused, and gentle. Before we begin, tell me how you're feeling and try a short eye exercise for healthy screen time.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Mood selection
    st.markdown("### How do you feel right now?")
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    moods = [("😄","joyful"), ("🙂","happy"), ("😐","neutral"), ("😔","sad"), ("😡","angry")]
    cols = [col1,col2,col3,col4,col5]
    for (emoji,name),c in zip(moods, cols):
        if c.button(f"{emoji}\n\n{name.capitalize()}", key=f"m_{name}"):
            # save mood
            st.session_state.mood_history.append((time.time(), name))
            st.session_state.selected_mood = name
            st.success(f"Saved mood: {name}")
    st.markdown("---")

    # Eye exercise box
    st.markdown("### 👀 Quick 30s Eye Exercise (recommended)")
    st.markdown("This helps reduce eye strain. You can skip it, but try if you can ❤️")
    col_a, col_b = st.columns([3,1])
    with col_a:
        st.write("Instructions: 1) Close eyes and gently rub palms. 2) Look at a distant object for 20 seconds. 3) Blink slowly for 10 seconds.")
    with col_b:
        if st.button("Start 30s exercise"):
            st.session_state.eye_started = True
            st.session_state.eye_start_time = time.time()
        if st.button("Skip and Enter"):
            st.session_state.entered = True

    # If started, show countdown and progress bar
   if st.session_state.get("eye_started", False) and not st.session_state.get("entered", False):
    elapsed = int(time.time() - st.session_state.eye_start_time)
    remaining = max(0, 30 - elapsed)
    st.progress(elapsed / 30)
    st.markdown(f"**Time left:** {remaining}s")

    if remaining <= 0:
        st.success("Great! You're ready. Entering the app...")
        st.session_state.entered = True
        st.session_state.eye_started = False
    else:
        time.sleep(1)          # pause for 1 second
        st.experimental_rerun()  # refresh the app to update the timer every second
    st.markdown("---")
    st.markdown("**Mood history (recent):**")
    if st.session_state.mood_history:
        for ts, m in st.session_state.mood_history[-6:]:
            st.markdown(f"- {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))} — **{m}**")
    else:
        st.write("No moods saved yet. Tap an emoji to save one.")
    st.markdown("---")

# -------------------------
# MAIN APP PAGE
# -------------------------
def main_app():
    # header and two column layout
    left, right = st.columns([2,1])
    with left:
        st.markdown("### 🔎 Find Herbal Remedies")
        st.markdown("<div class='small-muted'>Describe how you feel (e.g., 'stomach pain', 'feeling anxious and tired')</div>", unsafe_allow_html=True)
        user_input = st.text_input("How are you feeling today?", key="main_input")
        col_s, col_a = st.columns([3,1])
        with col_s:
            if st.button("Find Remedy"):
                if user_input:
                    result = lookup_remedy(user_input)
                    if result["status"] == "critical":
                        st.error("⚠️ " + result["message"])
                    elif result["status"] == "ok":
                        show_result_card(result["remedy"])
                    else:
                        st.warning("Not found in local database — fetching an AI suggestion...")
                        with st.spinner("Consulting the herbal AI..."):
                            ai_text = ask_genai(user_input)
                        st.markdown("### 🤖 AI Suggested Remedy")
                        st.info(ai_text)
                else:
                    st.info("Please enter a symptom to search.")
        with col_a:
            if st.button("Ask AI only"):
                if user_input:
                    with st.spinner("Asking AI..."):
                        ai_text = ask_genai(user_input)
                    st.markdown("### 🤖 AI Suggested Remedy")
                    st.info(ai_text)
                else:
                    st.info("Please enter symptoms first.")
    with right:
        st.markdown("### 🌿 Tip of the Day")
        st.markdown("> *Drink warm water first thing in the morning to support digestion.*")
        st.markdown("---")
        st.markdown("### 🔍 Quick Links")
        if st.button("Eye Exercises"):
            st.session_state.entered = False
        if st.button("Mood Log"):
            st.session_state.show_mood = True

def show_result_card(remedy):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    # image
    img_path = remedy.get("image", None)
    img = None
    if img_path:
        img = safe_image(img_path)
    if img:
        st.image(img, width=240, caption=remedy.get("english_name"))
    st.markdown(f"## {remedy.get('english_name')} — {remedy.get('nepali_name')}")
    st.markdown(f"**How to use:** {remedy.get('remedy')}")
    st.markdown("**Pros:**")
    for p in remedy.get("pros", []):
        st.write("- " + p)
    st.markdown("**Cons:**")
    for c in remedy.get("cons", []):
        st.write("- " + c)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Router: show precheck or main
# -------------------------
st.markdown("<div style='max-width:900px;margin:auto'>", unsafe_allow_html=True)
if not st.session_state.entered:
    precheck()
else:
    main_app()
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Made with 💚 by Khushi — BioFortune Prototype")


