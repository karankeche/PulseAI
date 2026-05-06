import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
from datetime import datetime
import random

st.set_page_config(page_title="PulseAI", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.hero{background:linear-gradient(135deg,#0d1b2a,#1b2838,#0a2744);border:1px solid #1e3a5f;border-radius:16px;padding:2.2rem;margin-bottom:1.5rem;text-align:center;}
.hero h1{font-size:2.6rem;font-weight:700;color:#e2e8f0;margin:0;}
.hero p{color:#94a3b8;font-size:1.05rem;margin-top:0.4rem;}
.mc{background:linear-gradient(135deg,#1e2330,#252d40);border:1px solid #2d3748;border-radius:10px;padding:1.1rem;text-align:center;margin-bottom:.5rem;}
.mv{font-size:1.9rem;font-weight:700;}
.ml{font-size:.8rem;color:#94a3b8;margin-top:.2rem;}
.sc{border-radius:10px;padding:1rem 1.2rem;margin-bottom:.7rem;border-left:4px solid;}
.s-critical{background:#2d0a0a;border-color:#ef4444;}
.s-high{background:#2d1a0a;border-color:#f97316;}
.s-medium{background:#2d260a;border-color:#eab308;}
.s-low{background:#0a2d1a;border-color:#22c55e;}
.badge{display:inline-block;padding:.18rem .6rem;border-radius:999px;font-size:.72rem;font-weight:600;}
.b-adr{background:#1e1b4b;color:#a5b4fc;}
.b-neg{background:#1c1917;color:#fdba74;}
.b-sho{background:#042f2e;color:#5eead4;}
.b-out{background:#450a0a;color:#fca5a5;}
.b-oth{background:#1e2330;color:#94a3b8;}
.lc{display:inline-block;padding:.15rem .5rem;background:#164e63;color:#67e8f9;border-radius:4px;font-size:.7rem;font-weight:600;margin-right:.3rem;}
.st-title{font-size:1.2rem;font-weight:600;color:#e2e8f0;border-bottom:2px solid #06b6d4;padding-bottom:.35rem;margin-bottom:.9rem;}
.stButton>button{background:linear-gradient(135deg,#0891b2,#0e7490);color:white;border:none;border-radius:8px;padding:.55rem 1.8rem;font-weight:600;}
</style>
""", unsafe_allow_html=True)

SEV_COLOR = {"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e"}
TYPE_BADGE = {"ADR":"b-adr","Hospital Negligence":"b-neg","Medicine Shortage":"b-sho","Outbreak Hint":"b-out","No Signal":"b-oth"}
GEO_MAP = {
    "Maharashtra":(19.75,75.71),"Tamil Nadu":(11.12,78.65),"West Bengal":(22.98,87.85),
    "Delhi":(28.70,77.10),"Andhra Pradesh":(15.91,79.74),"Karnataka":(15.31,75.71),
    "Rajasthan":(27.02,74.21),"Gujarat":(22.25,71.19),"Punjab":(31.14,75.34),"Kerala":(10.85,76.27),
}
DEMO_POSTS = [
    {"platform":"Twitter/X","region":"Maharashtra","post":"Is dawai se mujhe bahut chakkar aa raha hai aur ulti bhi ho rahi hai. Doctor ne Metformin 500mg diya tha diabetes ke liye. Kya yeh normal hai?","date":"2026-05-04"},
    {"platform":"Facebook","region":"Tamil Nadu","post":"Apollo Hospital Chennai la nurse proper care pannala. Enna patient kitta rude ah pesitanga. Complaint pannanum endru yosikiren.","date":"2026-05-04"},
    {"platform":"Twitter/X","region":"West Bengal","post":"Amoxicillin antibiotic Kolkata te pawa jacche na. 5ta dokan e giyechi, kothao stock nei. Ki korbo ekhon?","date":"2026-05-03"},
    {"platform":"WhatsApp","region":"Delhi","post":"After taking Paracetamol 650mg my skin developed rashes all over body. Is this an allergic reaction? Very scared right now.","date":"2026-05-03"},
    {"platform":"YouTube Comment","region":"Andhra Pradesh","post":"Vijayawada lo chala mandiki stomach problems vastunnai. Last week lo 20+ cases hospital ki vaccaru. Water contamination anukuntunna.","date":"2026-05-02"},
    {"platform":"Twitter/X","region":"Karnataka","post":"Atorvastatin tablets thinidaga thodai valikku aaguttu. Doctor kitta helbekku endru heltha idde. Side effect aa idu?","date":"2026-05-02"},
]

def analyze_with_claude(post_text, api_key):
    prompt = f"""You are a pharmacovigilance AI expert for India. Analyze this social media post for patient safety signals.

Post: "{post_text}"

Return ONLY valid JSON, no extra text:
{{
  "detected_language": "Hindi/Tamil/Marathi/Bengali/Telugu/Kannada/English/Other",
  "english_translation": "English translation (same if already English)",
  "signal_type": "ADR/Hospital Negligence/Medicine Shortage/Outbreak Hint/No Signal",
  "severity": "Critical/High/Medium/Low",
  "severity_score": <1-10>,
  "medical_entity": "drug or hospital or condition mentioned",
  "symptom_or_issue": "specific symptom or complaint",
  "confidence": <0.0-1.0>,
  "action_required": "Immediate Alert/Review Required/Monitor/No Action",
  "summary": "one sentence English summary",
  "geo_hint": "city or state if mentioned, else null"
}}"""
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":1000,"messages":[{"role":"user","content":prompt}]},
            timeout=30)
        raw = r.json()["content"][0]["text"].strip().replace("```json","").replace("```","").strip()
        return json.loads(raw), None
    except Exception as e:
        return None, str(e)

# Sidebar
with st.sidebar:
    st.markdown("## 🩺 PulseAI")
    st.markdown("**Multilingual Patient Safety Monitor**")
    st.divider()
    api_key = st.text_input("🔑 Anthropic API Key", type="password")
    st.divider()
    st.markdown("### 🌐 Supported Languages")
    for l in ["Hindi 🇮🇳","Tamil 🇮🇳","Marathi 🇮🇳","Bengali 🇮🇳","Telugu 🇮🇳","Kannada 🇮🇳","English 🌍"]:
        st.markdown(f"- {l}")
    st.divider()
    st.markdown("**AI for Bharat Hackathon**\n\n*Theme 6: Real-Time Social Listening*\n\n🏆 Shortlisted")

# Hero
st.markdown('<div class="hero"><h1>🩺 <span style="color:#06b6d4">Pulse</span><span style="color:#8b5cf6">AI</span></h1><p>Multilingual LLM-Powered Patient Safety Signal Detection from Social & Clinical Feedback</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Analyze Post","📊 Signal Dashboard","🗺️ India Map","📋 Demo Batch"])

# TAB 1
with tab1:
    st.markdown('<div class="st-title">Paste a Social Media Post</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3,2])
    with col1:
        post_input = st.text_area("Enter post in any Indian language or English", height=130,
            placeholder='e.g. "Is dawai se chakkar aa raha hai..." or paste any Indian language post')
        region = st.selectbox("Select Region", list(GEO_MAP.keys()))
        platform = st.selectbox("Platform", ["Twitter/X","Facebook","WhatsApp","YouTube Comment","Reddit"])
        analyze_btn = st.button("🔍 Analyze Signal", use_container_width=True)
    with col2:
        st.markdown("**💡 Try sample posts:**")
        for i, d in enumerate(DEMO_POSTS[:4]):
            if st.button(f"Demo {i+1}: {d['platform']} ({d['region'][:10]})", key=f"dp_{i}"):
                st.session_state.demo_post = d["post"]
                st.session_state.demo_region = d["region"]
                st.rerun()

    if "demo_post" in st.session_state:
        post_input = st.session_state.demo_post
        region = st.session_state.get("demo_region", region)

    if analyze_btn and post_input.strip():
        if not api_key:
            st.error("Enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("🧠 Claude analyzing..."):
                result, err = analyze_with_claude(post_input, api_key)
            if err:
                st.error(f"Error: {err}")
            elif result:
                sev = result.get("severity","Low")
                sc = SEV_COLOR.get(sev,"#94a3b8")
                sig = result.get("signal_type","No Signal")
                bc = TYPE_BADGE.get(sig,"b-oth")
                st.markdown("---")
                m1,m2,m3,m4 = st.columns(4)
                with m1: st.markdown(f'<div class="mc"><div class="mv" style="color:{sc}">{sev}</div><div class="ml">Severity</div></div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="mc"><div class="mv" style="color:#06b6d4">{result.get("severity_score","?")}/10</div><div class="ml">Score</div></div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="mc"><div class="mv" style="color:#8b5cf6">{result.get("confidence",0)*100:.0f}%</div><div class="ml">Confidence</div></div>', unsafe_allow_html=True)
                with m4:
                    act = result.get("action_required","Monitor")
                    ac = "#ef4444" if "Immediate" in act else "#eab308" if "Review" in act else "#22c55e"
                    st.markdown(f'<div class="mc"><div class="mv" style="color:{ac};font-size:.9rem">{act}</div><div class="ml">Action</div></div>', unsafe_allow_html=True)
                c1,c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Language:** <span class='lc'>{result.get('detected_language','?')}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Translation:** {result.get('english_translation','—')}")
                    st.markdown(f"**Medical Entity:** `{result.get('medical_entity','—')}`")
                    st.markdown(f"**Symptom/Issue:** {result.get('symptom_or_issue','—')}")
                with c2:
                    st.markdown(f"**Signal:** <span class='badge {bc}'>{sig}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Summary:** {result.get('summary','—')}")
                    st.markdown(f"**Location:** {result.get('geo_hint') or region}")
                if "signals" not in st.session_state: st.session_state.signals = []
                st.session_state.signals.append({**result,"post":post_input[:100]+"...","region":result.get("geo_hint") or region,"platform":platform,"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M")})
                st.success("✅ Signal saved to dashboard!")

# TAB 2
with tab2:
    signals = st.session_state.get("signals",[])
    if not signals:
        st.info("Analyze posts in Tab 1 or run Demo Batch in Tab 4 first.")
    else:
        total = len(signals)
        critical = sum(1 for s in signals if s.get("severity") in ["Critical","High"])
        types = {}
        for s in signals: types[s.get("signal_type","Other")] = types.get(s.get("signal_type","Other"),0)+1
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f'<div class="mc"><div class="mv" style="color:#06b6d4">{total}</div><div class="ml">Total Signals</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="mc"><div class="mv" style="color:#ef4444">{critical}</div><div class="ml">High/Critical</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="mc"><div class="mv" style="color:#a5b4fc">{types.get("ADR",0)}</div><div class="ml">ADR Reports</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="mc"><div class="mv" style="color:#fca5a5">{types.get("Outbreak Hint",0)}</div><div class="ml">Outbreak Hints</div></div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Pie(labels=list(types.keys()),values=list(types.values()),
                marker_colors=["#a5b4fc","#fdba74","#5eead4","#fca5a5","#94a3b8"],hole=0.5))
            fig.update_layout(title="Signal Types",template="plotly_dark",paper_bgcolor="#1e2330",height=300)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            sevs = {}
            for s in signals: sevs[s.get("severity","Low")] = sevs.get(s.get("severity","Low"),0)+1
            fig2 = go.Figure(go.Bar(x=list(sevs.keys()),y=list(sevs.values()),
                marker_color=[SEV_COLOR.get(k,"#94a3b8") for k in sevs],text=list(sevs.values()),textposition="outside"))
            fig2.update_layout(title="Severity Distribution",template="plotly_dark",paper_bgcolor="#1e2330",height=300)
            st.plotly_chart(fig2,use_container_width=True)
        st.markdown('<div class="st-title">📡 Signal Feed</div>', unsafe_allow_html=True)
        for s in reversed(signals):
            sv = s.get("severity","Low"); sc = SEV_COLOR.get(sv,"#94a3b8"); bc = TYPE_BADGE.get(s.get("signal_type","No Signal"),"b-oth")
            st.markdown(f'<div class="sc s-{sv.lower()}"><div style="display:flex;justify-content:space-between;align-items:center"><span class="badge {bc}">{s.get("signal_type","—")}</span><span class="lc">{s.get("detected_language","?")}</span><span style="color:{sc};font-weight:600;font-size:.85rem">{sv} ({s.get("severity_score","?")}/ 10)</span><span style="color:#475569;font-size:.75rem">{s.get("timestamp","")}</span></div><div style="color:#e2e8f0;margin-top:.5rem;font-size:.9rem">{s.get("summary","—")}</div><div style="color:#94a3b8;font-size:.8rem;margin-top:.3rem">📍 {s.get("region","—")} | 💊 {s.get("medical_entity","—")} | ⚡ {s.get("action_required","—")}</div></div>', unsafe_allow_html=True)

# TAB 3
with tab3:
    signals = st.session_state.get("signals",[])
    st.markdown('<div class="st-title">🗺️ India Safety Signal Map</div>', unsafe_allow_html=True)
    map_data = []
    src = signals if signals else [
        {"signal_type":"ADR","severity":"High","summary":"Paracetamol rash reaction","region":"Delhi","action_required":"Review Required"},
        {"signal_type":"Medicine Shortage","severity":"Medium","summary":"Amoxicillin stockout","region":"West Bengal","action_required":"Monitor"},
        {"signal_type":"Hospital Negligence","severity":"High","summary":"Patient care complaint","region":"Tamil Nadu","action_required":"Review Required"},
        {"signal_type":"Outbreak Hint","severity":"Critical","summary":"Stomach illness cluster","region":"Andhra Pradesh","action_required":"Immediate Alert"},
        {"signal_type":"ADR","severity":"Medium","summary":"Atorvastatin muscle pain","region":"Karnataka","action_required":"Monitor"},
        {"signal_type":"ADR","severity":"Low","summary":"Mild nausea with Metformin","region":"Maharashtra","action_required":"No Action"},
    ]
    for s in src:
        rk = s.get("region","")
        coords = next((v for k,v in GEO_MAP.items() if k.lower() in rk.lower() or rk.lower() in k.lower()), (20.59+random.uniform(-3,3),78.96+random.uniform(-3,3)))
        map_data.append({"lat":coords[0]+random.uniform(-.3,.3),"lon":coords[1]+random.uniform(-.3,.3),
            "signal_type":s.get("signal_type","Unknown"),"severity":s.get("severity","Low"),
            "summary":s.get("summary","—")[:60],"region":s.get("region","Unknown"),
            "size":{"Critical":20,"High":16,"Medium":12,"Low":8}.get(s.get("severity","Low"),10)})
    df_map = pd.DataFrame(map_data)
    fig_map = px.scatter_mapbox(df_map,lat="lat",lon="lon",color="severity",size="size",
        color_discrete_map=SEV_COLOR,hover_name="region",
        hover_data={"signal_type":True,"summary":True,"lat":False,"lon":False,"size":False},
        zoom=4,center={"lat":20.59,"lon":78.96},height=520,mapbox_style="carto-darkmatter",
        title="Patient Safety Signals Across India")
    fig_map.update_layout(template="plotly_dark",paper_bgcolor="#1e2330",margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig_map,use_container_width=True)
    lc1,lc2,lc3,lc4 = st.columns(4)
    for col,(sv,co) in zip([lc1,lc2,lc3,lc4],SEV_COLOR.items()):
        col.markdown(f'<div style="background:{co}22;border-left:3px solid {co};padding:.4rem .6rem;border-radius:4px;font-size:.85rem;color:{co};font-weight:600">{sv}</div>', unsafe_allow_html=True)

# TAB 4
with tab4:
    st.markdown('<div class="st-title">📋 Demo Batch — 6 Multilingual Posts</div>', unsafe_allow_html=True)
    st.markdown("6 posts across Hindi, Tamil, Bengali, English, Telugu, Kannada — covering all signal types.")
    st.dataframe(pd.DataFrame([{"Platform":d["platform"],"Region":d["region"],"Post":d["post"][:80]+"...","Date":d["date"]} for d in DEMO_POSTS]),use_container_width=True,hide_index=True)
    if st.button("🚀 Run Batch Analysis (All 6 Posts)",use_container_width=True):
        if not api_key:
            st.error("Enter your API key in the sidebar.")
        else:
            results = []
            prog = st.progress(0,text="Analyzing...")
            for i,demo in enumerate(DEMO_POSTS):
                prog.progress((i+1)/len(DEMO_POSTS),text=f"Post {i+1}/6...")
                result,err = analyze_with_claude(demo["post"],api_key)
                if result:
                    result.update({"post":demo["post"][:100]+"...","region":result.get("geo_hint") or demo["region"],"platform":demo["platform"],"timestamp":demo["date"]+" 00:00"})
                    results.append(result)
            if "signals" not in st.session_state: st.session_state.signals = []
            st.session_state.signals.extend(results)
            st.success(f"✅ {len(results)} signals processed! Check Dashboard and Map tabs.")
            for r in results:
                sv = r.get("severity","Low"); sc = SEV_COLOR.get(sv,"#94a3b8"); bc = TYPE_BADGE.get(r.get("signal_type","No Signal"),"b-oth")
                st.markdown(f'<div class="sc s-{sv.lower()}"><span class="badge {bc}">{r.get("signal_type","—")}</span> <span class="lc">{r.get("detected_language","?")}</span> <span style="color:{sc};font-weight:600;font-size:.8rem">{sv}</span><div style="color:#e2e8f0;margin-top:.4rem;font-size:.88rem">{r.get("summary","—")}</div><div style="color:#94a3b8;font-size:.78rem;margin-top:.2rem">📍 {r.get("region","—")} | ⚡ {r.get("action_required","—")}</div></div>', unsafe_allow_html=True)
