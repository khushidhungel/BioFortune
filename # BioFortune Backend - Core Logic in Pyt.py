# BioFortune App – Streamlit Frontend + Backend (Prototype)
# -------------------------------------------------------------
# Run this with: streamlit run biofortune_app.py

import streamlit as st
import base64
import os
# set your API key
# It's best practice NOT to hardcode your OpenAI API key in the source code.
# Instead, store your API key securely (e.g., in Streamlit secrets or environment variables).

# For Streamlit Cloud or local secrets:
# For Gemini API, set the API key for google.generativeai instead of OpenAI:
import google.generativeai as genai
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# If running locally and not using Streamlit secrets, you can use an environment variable:
# openai.api_key = os.getenv("OPENAI_API_KEY")


# -----------------------------
# Herbal Remedy Database (Expanded with Many More Symptoms)
# -----------------------------
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
    "constipation": {
        "english_name": "Isabgol (Psyllium Husk)",
        "nepali_name": "ईसबगोल",
        "image": "isabgol.jpg",
        "remedy": "Mix 1 tbsp in warm water before bedtime.",
        "pros": ["Relieves constipation", "Improves gut health"],
        "cons": ["Needs to be taken with water"]
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
    },
    "muscle ache": {
        "english_name": "Epsom Salt",
        "nepali_name": "एप्सम नुन",
        "image": "epsomsalt.jpg",
        "remedy": "Soak in warm water with Epsom salt.",
        "pros": ["Relaxes muscles", "Soothes soreness"],
        "cons": ["May dry out skin"]
    },
    "shoulder pain": {
        "english_name": "Cayenne Pepper",
        "nepali_name": "खुर्सानी",
        "image": "cayenne.jpg",
        "remedy": "Apply cream with cayenne extract.",
        "pros": ["Pain relief", "Improves circulation"],
        "cons": ["May irritate sensitive skin"]
    },
    "sleep issues": {
        "english_name": "Chamomile",
        "nepali_name": "चामोमाइल",
        "image": "chamomile.jpg",
        "remedy": "Drink chamomile tea 30 mins before bed.",
        "pros": ["Calms mind", "Promotes sleep"],
        "cons": ["Allergic reactions in some"]
    },
    "low motivation": {
        "english_name": "Brahmi",
        "nepali_name": "ब्राम्ही",
        "image": "brahmi.jpg",
        "remedy": "Take Brahmi syrup or capsule daily.",
        "pros": ["Boosts mental energy", "Improves memory"],
        "cons": ["Can lower heart rate"]
    },
    "dizziness": {
        "english_name": "Lemongrass",
        "nepali_name": "लेमनग्रास",
        "image": "lemongrass.jpg",
        "remedy": "Drink lemongrass tea to refresh and balance.",
        "pros": ["Improves circulation", "Energizing"],
        "cons": ["Can lower blood pressure"]
    },
    "abdominal pain": {
        "english_name": "Ajwain",
        "nepali_name": "जवान",
        "image": "ajwain.jpg",
        "remedy": "Boil ajwain seeds and sip warm water.",
        "pros": ["Eases bloating", "Reduces stomach pain"],
        "cons": ["Overuse may cause heartburn"]
    },
    "stomach pain": {
        "english_name": "Ajwain",
        "nepali_name": "जवान",
        "image": "ajwain.jpg",
        "remedy": "Boil ajwain seeds and sip warm water.",
        "pros": ["Eases bloating", "Reduces stomach pain"],
        "cons": ["Overuse may cause heartburn"]
    }
}

critical_symptoms = [
    "chest pain", "fainting", "severe bleeding", "unconscious",
    "shortness of breath", "severe abdominal pain"
]

# -----------------------------
# Remedy Lookup Function
# -----------------------------
def get_remedy(user_symptom):
    user_symptom = user_symptom.lower()
    for word in critical_symptoms:
        if word in user_symptom:
            return {
                "status": "critical",
                "message": "Your symptoms seem serious. Please consult a doctor immediately."
            }
    for keyword, data in herbal_db.items():
        if keyword in user_symptom:
            return {
                "status": "ok",
                "remedy": data
            }
    return {
        "status": "not_found",
        "message": "Sorry, we could not find a remedy for your symptom so searching..... Try describing it differently."
    }
def get_ai_suggestion(symptom):
    prompt = f"""
You are a Nepali herbal medicine expert. A user reported this symptom: "{symptom}".
Suggest a possible Nepali herbal remedy with:
- Herb name (English and Nepali)
- Dosage or usage method
- Pros and cons
If symptom is critical, advise visiting a doctor.
Only suggest safe, natural remedies used in traditional Nepali medicine.
"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

        response = model.generate_content([prompt])
        return response.text
    except Exception as e:
        return f"⚠️ Error fetching AI response: {e}"
# -----------------------------
# Streamlit UI Starts Here
# -----------------------------
st.set_page_config(page_title="BioFortune", page_icon="🌿", layout="centered")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e6f2e6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌿 BioFortune")
st.subheader("Your Personalized Herbal Wellness Guide")

user_input = st.text_input("How are you feeling today? (e.g., stress, eye strain, diarrhea, joint pain, etc.)")
if st.button("Find Remedy"):
    if user_input:
        result = get_remedy(user_input)
        if result["status"] == "critical":
            st.error("⚠️ " + result["message"])
        elif result["status"] == "ok":
            remedy = result["remedy"]
            st.success("✅ Remedy Found!")
            st.markdown(f"**Herb (EN):** {remedy['english_name']}")
            st.markdown(f"**Herb (NP):** {remedy['nepali_name']}")
            st.markdown(f"**Suggested Use:** {remedy['remedy']}")
            st.markdown("**Pros:**")
            for p in remedy["pros"]:
                st.write("- ", p)
            st.markdown("**Cons:**")
            for c in remedy["cons"]:
                st.write("- ", c)
        else:
           st.warning(result["message"])
           with st.spinner("Consulting AI for a suggestion..."):
                ai_response = get_ai_suggestion(user_input)
                st.markdown("### 🤖 AI Suggested Remedy:")
                st.write(ai_response)

    else:
        st.info("Please enter a symptom to get started.")

st.markdown("---")
st.caption("Made with 💚 by Khushi - BioFortune Prototype")

