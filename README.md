# 🩺 PulseAI

**Multilingual LLM-Powered Patient Safety Signal Detection from Social & Clinical Feedback**

> Built for **AI for Bharat Hackathon** — Theme 6: Real-Time Social Listening for Patient Experience & Safety Signals

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🌐 Multilingual NLP | Detects Hindi, Tamil, Marathi, Bengali, Telugu, Kannada + English posts |
| 🔍 Signal Classification | Classifies into ADR, Hospital Negligence, Medicine Shortage, Outbreak Hint |
| 🗺️ India Heat Map | Geo-tags signals to district/state level on live map |
| 📊 Dashboard | Real-time severity distribution, signal type charts, signal feed |
| 🚨 Severity Scoring | 0–10 severity score + action recommendation per signal |
| 📋 Batch Analysis | Process 6 multilingual demo posts in one click |

---

## 🛠️ Setup & Run

```bash
git clone https://github.com/YOUR_USERNAME/pulseai.git
cd pulseai
python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Enter your **Anthropic API key** in the sidebar when the app opens.

---

## 🌐 Demo Posts (6 Languages)

| Language | Platform | Signal Type |
|---|---|---|
| Hindi | Twitter/X | ADR (Metformin dizziness) |
| Tamil | Facebook | Hospital Negligence |
| Bengali | Twitter/X | Medicine Shortage |
| English | WhatsApp | ADR (Paracetamol rash) |
| Telugu | YouTube | Outbreak Hint |
| Kannada | Twitter/X | ADR (Atorvastatin) |

---

## 🎯 Impact

- First multilingual patient safety radar built for India's linguistic diversity
- Catches outbreak signals days before official reports
- Plugs into India's Pharmacovigilance Programme (PvPI)
- Scalable to all 28 states with zero architecture change

---

## 👤 Author

**Karan Keche** | AI for Bharat Hackathon 2026
# PulseAI
