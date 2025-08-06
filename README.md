# 🌿 BioFortune – Your Personalized Herbal Wellness Guide

**BioFortune** is a Streamlit-powered app that provides personalized Nepali herbal remedies based on user-reported symptoms. It combines traditional herbal knowledge with AI suggestions using Google's Gemini API.

## 🔮 Features

- 🧠 AI-powered suggestions for non-critical health symptoms
- 🌱 Herbal remedies from Nepali traditional medicine
- 📸 Images, pros and cons of each herb
- 🛑 Warning for critical symptoms (suggests seeing a doctor)
- 💡 Simple, clean user interface with soft green theme

## 🖥️ Live App

➡️ [Click here to open the app](https://your-deployed-url.streamlit.app)  
(*Replace with your actual URL after deployment*)

## 🚀 How to Run Locally

1. Clone the repo:
    ```bash
    git clone https://github.com/yourusername/biofortune.git
    cd biofortune
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv .venv
    .venv\Scripts\activate     # On Windows
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Add your API key:
    Create a file at `.streamlit/secrets.toml` and add:
    ```toml
    GEMINI_API_KEY = "your_google_gemini_api_key"
    ```

5. Run the app:
    ```bash
    streamlit run biofortune_app.py
    ```

## 🧪 Technologies Used

- [Streamlit](https://streamlit.io/) – UI framework
- [Google Generative AI (Gemini)](https://ai.google.dev/) – AI herbal suggestions
- Python 3.10+

## 🛡️ Disclaimer

This app is for informational purposes only and does not constitute medical advice. Always consult a healthcare provider for serious symptoms.

---

👩‍🔬 Built with love and curiosity by **Khushi Dhungel** 💚
