import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from config import API_KEY
import io
import qrcode
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# 🔐 API KEY
# ==============================
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-3-flash-preview')

# ==============================
# 🧠 AI ANALYSIS
# ==============================
@st.cache_data(show_spinner=False)

def clean_json_response(raw):
    try:
        # إزالة ```json
        if "```" in raw:
            raw = raw.split("```")[1]
            raw = raw.replace("json", "")

        # استخراج JSON فقط
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group()

        # إصلاح quotes داخل النص العربي
        raw = re.sub(r'(?<!\\)"(.*?)"(?![:,}\]])', r'\"\1\"', raw)

        # إزالة newline
        raw = raw.replace("\n", " ").strip()

        return json.loads(raw)

    except Exception as e:
        return {
            "error": str(e),
            "raw": raw
        }


def analyze_data(desc, use_swot, use_pestel):

    analysis_parts = []
    if use_swot:
        analysis_parts.append("تحليل SWOT")
    if use_pestel:
        analysis_parts.append("تحليل PESTEL")

    analysis_text = " و ".join(analysis_parts)

    # JSON dynamic
    json_structure = "{"

    if use_swot:
        json_structure += """
        "SWOT": { "Strengths": [], "Weaknesses": [], "Opportunities": [], "Threats": [] },
        """

    if use_pestel:
        json_structure += """
        "PESTEL": {
            "Political": [],
            "Economic": [],
            "Social": [],
            "Technological": [],
            "Environmental": [],
            "Legal": []
        },
        """

    json_structure += """
    "IFE_Matrix": [{"factor": "", "weight": 0.0, "rating": 1, "rationale": ""}],
    "EFE_Matrix": [{"factor": "", "weight": 0.0, "rating": 1, "rationale": ""}],
    "Strategic_Objectives": [{"objective": "", "type": "", "link_to_swot": ""}]
    }
    """

    prompt = f"""
    النص التالي:

    {desc}

    المطلوب:
    1. استخرج وصف الشركة + الرؤية + الرسالة (إن أمكن)
    2. قم بـ {analysis_text}
    3. إعداد IFE و EFE و Strategic Objectives

    أخرج JSON فقط بالشكل:

    {json_structure}

    شروط:
    - اللغة عربية
    - مجموع الأوزان = 1
    - التقييم من 1 إلى 4
    - على الأقل 5 عناصر لكل قسم

    مهم جداً:
    - ممنوع استخدام " داخل النصوص
    - استخدم ' بدلاً منها داخل الجمل
    - أخرج JSON صالح 100% بدون أي نص خارج JSON
    """

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        if "```" in raw:
            raw = raw.split("```")[1].replace("json", "")

        cleaned = clean_json_response(raw)

        if "error" in cleaned:
            #st.warning("⚠️ حصلت مشكلة في التنسيق - عرض البيانات الخام")

            # نحاول fallback parsing بسيط
            try:
                return json.loads(raw)
            except:
                return {"raw": raw}

        return cleaned

    except Exception as e:
        return {"error": str(e), "raw": raw if 'raw' in locals() else ""}


# ==============================
# 🌐 URL Extraction
# ==============================
def extract_text_from_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            st.error("❌ فشل تحميل الصفحة")
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        return soup.get_text(separator=" ").strip()[:4000]

    except Exception as e:
        st.error(f"❌ خطأ: {e}")
        return None


# ==============================
# 🎥 YouTube
# ==============================
def get_youtube_transcript(url):
    try:
        video_id = url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript])[:4000]
    except:
        st.error("❌ لا يمكن استخراج الترجمة")
        return None


# ==============================
# 🎨 UI
# ==============================
st.set_page_config(
    page_title="ASAS - Strategic AI",
    page_icon="🧠",
    layout="centered"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: Tajawal, sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
    background-color:#333;
}
html{
    background-color: rgba(151, 166, 195, 0.15) !important;
}
.st-emotion-cache-1r4qj8v {
    position: absolute;
    background: transparent !important;
}            
h1, h2, h3, p, li {
    text-align: right !important;
    font-family: 'Tajawal', sans-serif !important;
}
li {
    margin-right: 15px;
    text-align: justify !important;
    margin-left: 15px;
}
.stButton button {
    width: 100%;
    background: linear-gradient(135deg, rgb(228, 0, 127) 0%, rgb(29, 32, 136) 100%);
    border: none;
    border-radius: 50px;
    padding: 22px 45px;
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 8px 30px rgba(228, 0, 127, 0.4), 0 4px 15px rgba(29, 32, 136, 0.2);
    min-width: 220px;
    min-height: 65px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-decoration: none;
    position: relative;
    overflow: hidden;
}

@media only screen and (max-width: 768px) {
    h1 { font-size: 22px !important; }
    .st-emotion-cache-1w723zb {
        width: 100% !important;
        max-width: 98% !important;
    }            
}
.stAppHeader{
    display:none !important;
}
.st-emotion-cache-1w723zb {
    padding: 25px 1rem 25px !important;
}
[data-testid="stDataFrame"] {
    direction: rtl !important;
    text-align: right !important;
}

[data-testid="stDataFrame"] th {
    text-align: right !important;
}
thead {
    background: linear-gradient(135deg, rgb(29, 32, 136) 0%, rgb(228, 0, 127) 100%);
    color: white;
}
.st-emotion-cache-tn0cau {
     height: 100% !important;
    overflow-y: hidden !important;;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.15) !important;;
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 10px !important;;
    padding: 10px 50px !important;;
}
textarea, 
        input[type="text"], 
        input[type="email"],
        input[type="url"],
            {
    text-align: right !important;
    background-color:#fff !important;
}
.st-bv {
    background-color:#fff !important;
}
.st-emotion-cache-p75nl5 {
    margin: auto !important;
}
.st-emotion-cache-1s8qyds h3 {
    font-size: 1.25rem;
}
div[data-testid="stTextInputRootElement"]{
    border-radius: 50px !important;
}
input[type="text"], 
input[type="email"], 
input[type="password"], 
textarea {
background-color: #f5f5f5 !important; /* Light gray background */
color: #000 !important;             /* Dark text color for contrast */
  
 
} 
.st-emotion-cache-1s8qyds hr {
    margin: 0.5em 0px !important;
    border-color: #f5f5f5 !important;
}       
</style>
""", unsafe_allow_html=True)
st.image("asset/images/ASAS.png", 
         caption="", 
         width=250)
st.divider()
# ==============================
# ⚙️ اختيار التحليل
# ==============================
st.subheader("⚙️ اختر نوع التحليل")

analysis_type = st.multiselect(
    "اختر التحليلات المطلوبة",
    ["SWOT", "PESTEL","BSC"],
    default=["SWOT"]
)

use_swot = "SWOT" in analysis_type
use_pestel = "PESTEL" in analysis_type
use_BSC = "BSC" in analysis_type

if not analysis_type:
    st.warning("⚠️ يجب اختيار نوع تحليل واحد على الأقل")

st.divider()

# ==============================
# 🧾 INPUT
# ==============================
mode = st.radio(
    "اختر طريقة الإدخال",
    ["🌐 تحليل من رابط", "✍️ إدخال يدوي"],
    horizontal=True
)

input_text = None

if mode == "✍️ إدخال يدوي":
    desc = st.text_area("وصف الشركة")
    vision = st.text_input("الرؤية")
    mission = st.text_input("الرسالة")

    if st.button("🚀 تحليل"):
        input_text = f"""
        وصف الشركة: {desc}
        الرؤية: {vision}
        الرسالة: {mission}
        """

elif mode == "🌐 تحليل من رابط":
    url = st.text_input("ضع الرابط")

    if st.button("🚀 تحليل الرابط"):
        input_text = extract_text_from_url(url)

# ==============================
# 🚀 RUN
# ==============================
if input_text and analysis_type:

    with st.spinner("🤖 جاري التحليل..."):
        results = analyze_data(input_text, use_swot, use_pestel)

    if "error" in results:
        st.error("❌ خطأ في التحليل")
        st.code(results.get("raw", ""))

    else:
        st.success("✅ تم التحليل")

        # ================= SWOT =================
        if use_swot and "SWOT" in results:
            st.header("📊 SWOT")

            col1, col2 = st.columns(2)

            with col1:
                st.success("Strengths")
                for i in results["SWOT"].get("Strengths", []):
                    st.write("-", i)

                st.info("Opportunities")
                for i in results["SWOT"].get("Opportunities", []):
                    st.write("-", i)

            with col2:
                st.warning("Weaknesses")
                for i in results["SWOT"].get("Weaknesses", []):
                    st.write("-", i)

                st.error("Threats")
                for i in results["SWOT"].get("Threats", []):
                    st.write("-", i)

        # ================= PESTEL =================
        if use_pestel and "PESTEL" in results:
            st.header("🌍 PESTEL")

            pestel = results["PESTEL"]

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            col5, col6 = st.columns(2)

            with col1:
                st.info("🏛️ Political")
                for i in pestel.get("Political", []):
                    st.write("-", i)

            with col2:
                st.success("💰 Economic")
                for i in pestel.get("Economic", []):
                    st.write("-", i)

            with col3:
                st.warning("👥 Social")
                for i in pestel.get("Social", []):
                    st.write("-", i)

            with col4:
                st.info("💻 Technological")
                for i in pestel.get("Technological", []):
                    st.write("-", i)

            with col5:
                st.success("🌱 Environmental")
                for i in pestel.get("Environmental", []):
                    st.write("-", i)

            with col6:
                st.error("⚖️ Legal")
                for i in pestel.get("Legal", []):
                    st.write("-", i)

        st.divider()

        # ================= IFE =================
        st.header("📈 IFE Matrix")
        df_ife = pd.DataFrame(results.get('IFE_Matrix', []))

        # ================= Chart IFE =================
        if not df_ife.empty:

            df_ife["score"] = df_ife["weight"] * df_ife["rating"]

            fig = px.bar(
                df_ife,
                x="factor",
                y="score",
                title="📊 IFE Factors Impact"
            )

            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)


        st.dataframe(df_ife)

        score_ife = sum(i['weight'] * i['rating'] for i in results.get('IFE_Matrix', []))
        st.metric("IFE Score", round(score_ife, 2))

        # ================= EFE =================
        st.header("📉 EFE Matrix")
        df_efe = pd.DataFrame(results.get('EFE_Matrix', []))

        # ================= Chart IFE =================
        if not df_efe.empty:

            df_efe["score"] = df_efe["weight"] * df_efe["rating"]

            fig = px.bar(
                df_efe,
                x="factor",
                y="score",
                title="📊 EFE Factors Impact"
            )

            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)


        st.dataframe(df_efe)

        score_efe = sum(e['weight'] * e['rating'] for e in results.get('EFE_Matrix', []))
        st.metric("EFE Score", round(score_efe, 2))

        # ================= Objectives =================
        st.header("🎯 الأهداف الاستراتيجية")

        for obj in results.get('Strategic_Objectives', []):
            st.markdown(f"""
            **{obj.get('objective', '')}**  
            النوع: {obj.get('type', '')}  
            الارتباط: {obj.get('link_to_swot', '')}
            """)

        # ================= Download =================
        st.download_button(
            label="📄 تحميل التقرير",
            data=json.dumps(results, ensure_ascii=False, indent=2),
            file_name="analysis.json",
            mime="application/json"
        )

elif input_text is None:
    st.warning("⚠️ أدخل بيانات أو رابط لبدء التحليل")

# ==============================
# 📱 QR CODE
# ==============================
app_url = "https://newasas.streamlit.app"  # غيرها بعد النشر

qr = qrcode.make(app_url)
buf = io.BytesIO()
qr.save(buf, format="PNG")
buf.seek(0)

st.divider()
st.markdown("### 📱 فتح التطبيق على الموبايل")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(buf, width=150)
    st.caption("امسح الكود لفتح التطبيق")    
