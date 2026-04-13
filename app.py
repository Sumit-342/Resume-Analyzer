
import streamlit as st
from utils import extract_text_from_pdf, match_skills, calculate_score
from skills import SKILLS
import pandas as pd
import base64
import io
import re
import fitz
import streamlit.components.v1 as components

def show_pdf_preview(uploaded_file):
    uploaded_file.seek(0)  # VERY IMPORTANT

    base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')

    pdf_display = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="220px"
        style="border-radius:8px; border:1px solid #e4e4e0;">
    </iframe>
    """

    st.markdown(pdf_display, unsafe_allow_html=True)

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem; max-width: 1100px; }
.stApp {
    background: linear-gradient(135deg, #f7f7f5, #eef3f8);
}

.hero-wrap {
    padding: 2.8rem 0 2rem;
    border-bottom: 1px solid #e8e8e4;
    margin-bottom: 1.8rem;
    text-align: center;        
}
.hero-badge {
    display: inline-block;
    background: #eaf3de;
    color: #3b6d11;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
    text-transform: uppercase;
}
.hero-title {
    font-size: 36px;
    font-weight: 600;
    background: linear-gradient(135deg, #1D9E75, #3266ad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin: 0 0 0.5rem;
}
.hero-sub {
    font-size: 15px;
    color: #6b6b66;
    margin: 0;
}

.card {
    background: #ffffff;
    border: 1px solid #e8e8e4;
    border-radius: 14px;
    padding: 1.2rem 1.3rem;
    margin-bottom: 14px;
}
.card-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #9e9e98;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.upload-zone {
    border: 1.5px dashed #c8c8c2;
    border-radius: 10px;
    padding: 2rem 1rem;
    text-align: center;
    background: #f9f9f7;
}
.upload-icon-wrap {
    width: 44px; height: 44px;
    border-radius: 10px;
    background: #eaf3de;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px;
    font-size: 20px;
}
.upload-hint { font-size: 13px; color: #6b6b66; margin: 4px 0; }
.upload-hint2 { font-size: 11px; color: #a0a09a; }

.preview-box {
    background: #f4f4f1;
    border-radius: 8px;
    padding: 14px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #4a4a46;
    line-height: 1.7;
    min-height: 120px;
    max-height: 180px;
    overflow: hidden;
    border: 1px solid #e4e4e0;
    white-space: pre-wrap;
    word-break: break-word;
}
.preview-page { font-size: 11px; color: #a0a09a; text-align: center; margin-top: 8px; }

@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position:  400px 0; }
}
.skel {
    border-radius: 3px;
    margin-bottom: 6px;
    background: linear-gradient(90deg, #e8e8e4 25%, #f4f4f1 50%, #e8e8e4 75%);
    background-size: 400px 100%;
    animation: shimmer 1.4s ease infinite;
}
.skel-name { width: 50%; height: 8px; background: #b8b8b2; }
.skel-med   { width: 68%; height: 6px; }
.skel-long  { width: 90%; height: 6px; }
.skel-short { width: 38%; height: 6px; }

.info-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #f0f0ec;
    font-size: 13px;
}
.info-row:last-child { border-bottom: none; }
.info-key { color: #8a8a84; }
.info-val { font-weight: 500; color: #1a1a18; }

.tags-wrap { display: flex; flex-wrap: wrap; gap: 7px; }
.tag {
    font-size: 11.5px; font-weight: 500;
    padding: 4px 11px; border-radius: 20px;
}
.tag-neutral { background: #f2f2ee; color: #4a4a46; border: 1px solid #e4e4e0; }
.tag-matched { background: #eaf3de; color: #27500a; }
.tag-missing  { background: #fcebeb; color: #791f1f; }

.score-num { font-size: 38px; font-weight: 600; color: #1a1a18; }
.score-denom { font-size: 15px; color: #8a8a84; }
.score-label { font-size: 12px; font-weight: 600; color: #1d9e75; }
.progress-track {
    width: 100%; height: 9px;
    background: #f0f0ec; border-radius: 5px;
    margin: 10px 0 4px; overflow: hidden;
}
.progress-fill {
    height: 100%; border-radius: 5px;
    background: linear-gradient(90deg, #5DCAA5, #1D9E75);
}
.progress-ends { display: flex; justify-content: space-between; font-size: 11px; color: #b0b0aa; }

.role-row {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px; font-size: 12.5px;
}
.role-name-cell { width: 138px; color: #3a3a36; flex-shrink: 0; }
.bar-track {
    flex: 1; height: 9px;
    background: #f0f0ec; border-radius: 5px; overflow: hidden;
}
.bar-fill { height: 100%; border-radius: 5px; }
.bar-pct { width: 34px; text-align: right; color: #8a8a84; font-size: 11.5px; flex-shrink: 0; }

.best-fit {
    background: #e1f5ee;
    border: 1px solid #5dcaa5;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    display: flex; align-items: center; gap: 12px;
    margin-top: 14px;
}
.best-fit-ico {
    width: 38px; height: 38px; border-radius: 50%;
    background: #1d9e75;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.best-fit-title { font-size: 13.5px; font-weight: 600; color: #085041; }
.best-fit-sub { font-size: 11.5px; color: #0f6e56; margin-top: 2px; }

.sugg-item {
    display: flex; gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid #f0f0ec;
    align-items: flex-start;
}
.sugg-item:last-child { border-bottom: none; }
.sugg-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #ef9f27; flex-shrink: 0; margin-top: 5px;
}
.sugg-main { font-size: 13px; color: #1a1a18; font-weight: 500; }
.sugg-sub { font-size: 11.5px; color: #8a8a84; margin-top: 2px; }

.stFileUploader > div { border: none !important; padding: 0 !important; background: transparent !important; }
.stFileUploader label { display: none; }
div[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #c8c8c2 !important;
    border-radius: 10px !important;
    background: #f9f9f7 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────
BAR_COLORS = ["#3266ad", "#5DCAA5", "#AFA9EC", "#F09995", "#c8c8c2",
              "#EF9F27", "#D4537E", "#378ADD", "#639922", "#D85A30"]




def extract_links(pdf_file):
    links = []

    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")

    for page in pdf:
        for link in page.get_links():
            if "uri" in link:
                links.append(link["uri"])

    return links



def extract_info(text, pdf_bytes):
    info = {}
    
# Email
    email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email:
        info["Email"] = min(email, key=len)  # shortest match is cleanest
    else:
        info["Email"] = "Not found"
    
    # Phone
    phone = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', text)
    info["Phone"] = phone[0] if phone else "Not found"
    
    # Name
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name = "Not found"
    for line in lines[:15]:
        cleaned = line.strip()
        # skip job titles / role keywords
        skip_keywords = ['developer', 'engineer', 'designer', 'analyst', 'manager', 
                        'enthusiast', 'summary', 'education', 'skills', 'profile',
                        'web', 'student', 'fresher']
        if (2 < len(cleaned) < 40
                and not any(c.isdigit() for c in cleaned)
                and '@' not in cleaned
                and '/' not in cleaned
                and '|' not in cleaned
                and cleaned.replace(' ', '').isalpha()
                and not any(kw in cleaned.lower() for kw in skip_keywords)):
            name = cleaned.title()
            break
    info["Name"] = name


    # LinkedIn & GitHub — pass bytes directly, no external variable
    links = extract_links(io.BytesIO(pdf_bytes))

    github = [l for l in links if "github.com" in l]
    linkedin = [l for l in links if "linkedin.com" in l]

    info["GitHub"] = github[0].rstrip('/').split('/')[-1] if github else "Not found"

    if linkedin:
        username = linkedin[0].rstrip('/').split('/')[-1]
        username = re.sub(r'-[a-f0-9]{8,}$', '', username)
        info["LinkedIn"] = username
    else:
        info["LinkedIn"] = "Not found"

    return info

def calculate_ats_score(text):
    score = 0
    breakdown = {}

    # 1. Contact Info (20 points)
    contact = 0
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text): contact += 7
    if re.search(r'[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9]', text): contact += 7
    if re.search(r'linkedin\.com', text.lower()): contact += 6
    breakdown["Contact Info"] = min(contact, 20)
    score += breakdown["Contact Info"]

    # 2. Section Headers (20 points)
    headers = 0
    for word in ['experience', 'education', 'skills', 'projects', 'summary', 'objective', 'certifications']:
        if word in text.lower(): headers += 3
    breakdown["Section Headers"] = min(headers, 20)
    score += breakdown["Section Headers"]

    # 3. Action Verbs (20 points)
    action_verbs = ['built', 'developed', 'designed', 'implemented', 'created', 
                    'managed', 'led', 'improved', 'increased', 'decreased',
                    'deployed', 'optimized', 'achieved', 'launched', 'delivered',
                    'collaborated', 'automated', 'integrated', 'analyzed', 'trained']
    verb_count = sum(1 for verb in action_verbs if verb in text.lower())
    breakdown["Action Verbs"] = min(verb_count * 4, 20)
    score += breakdown["Action Verbs"]

    # 4. Measurable Achievements (20 points)
    numbers = re.findall(r'\d+%|\d+ percent|\$\d+|\d+ users|\d+ projects', text.lower())
    breakdown["Measurable Impact"] = min(len(numbers) * 5, 20)
    score += breakdown["Measurable Impact"]

    # 5. Resume Length (20 points)
    word_count = len(text.split())
    if 300 <= word_count <= 800:
        breakdown["Resume Length"] = 20
    elif 200 <= word_count <= 1000:
        breakdown["Resume Length"] = 10
    else:
        breakdown["Resume Length"] = 5
    score += breakdown["Resume Length"]

    return score, breakdown


def score_label(score):
    if score >= 80: return "Excellent ↑"
    if score >= 60: return "Good ↑"
    if score >= 40: return "Fair →"
    return "Needs Work ↓"

def build_tags_html(skills, css_class):
    if not skills:
        return '<span style="font-size:12px;color:#8a8a84;">None found</span>'
    return "".join(f'<span class="tag {css_class}">{s.title()}</span>' for s in skills)

def build_role_bars_html(results):
    sorted_roles = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
    html = ""
    for i, (role, data) in enumerate(sorted_roles):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        score = data["score"]
        html += f"""
        <div class="role-row">
            <span class="role-name-cell">{role}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{score}%;background:{color};"></div></div>
            <span class="bar-pct">{score}%</span>
        </div>"""
    return html


# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ AI-Powered</div>
    <h1 class="hero-title">Resume Analyzer</h1>
    <p class="hero-sub">Upload your resume and get instant feedback, role predictions, and skill insights.</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════
left_col, right_col = st.columns([1, 1.85], gap="large")


with left_col:

# ── Upload ──
    with st.container(border=True):
        st.markdown('<div class="card-label" style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:12px;">Upload Resume</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf"], label_visibility="collapsed")


    # ── Preview ──


    if uploaded_file:
        file_bytes = uploaded_file.read()

        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')

        pdf_display = f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="250px"
            style="border-radius:8px; border:1px solid #e4e4e0;">
        </iframe>
        """

        st.markdown(f"""
            <div class="card">
                <div class="card-label">Resume Preview</div>
                {pdf_display}
            
            """, unsafe_allow_html=True)

        # 🔥 IMPORTANT: recreate file
        file_for_extraction = io.BytesIO(file_bytes)
        text = extract_text_from_pdf(file_for_extraction)



    # ── Extracted Info ──
    if uploaded_file:
        
        info = extract_info(text, file_bytes)
        all_matched = set()
        for role, skills in SKILLS.items():
            all_matched.update(match_skills(text, skills))
        detected_tags = "".join(f'''
        <span style="display:inline-flex;align-items:center;justify-content:center;
        background:#fbeaf0;color:#72243e;border:1px solid #ed93b1;
        font-size:11.5px;font-weight:500;padding:6px 14px;
        border-radius:999px;margin:3px;">{s.title()}</span>''' for s in sorted(all_matched))

        info_rows_html = ""
        for key, val in info.items():
            info_rows_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #f0f0ec;font-size:13px;">
                <span style="color:#8a8a84;">{key}</span>
                <span style="font-weight:500;color:#1a1a18;font-size:12px;">{val}</span>
            </div>"""

        num_skill_rows = -(-len(all_matched) // 3)  # ceiling division, 3 pills per row
        dynamic_height = 200 + (num_skill_rows * 44)

        total_chars = sum(len(s) for s in all_matched)
        skill_rows = max(1, total_chars // 30)
        info_rows_height = len(info) * 36
        skills_height = skill_rows * 44
        dynamic_height = 140 + info_rows_height + skills_height

        components.html(f"""
        <div style="background:#ffffff;border:1px solid #e8e8e4;border-radius:14px;padding:1.2rem 1.3rem;">
            <div style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:12px;">Extracted Info</div>
            {info_rows_html}
            <div style="margin-top:14px;font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:10px;">Skills Detected</div>
            <div style="display:flex;flex-wrap:wrap;gap:7px;">
                {detected_tags}
            </div>
        </div>
        """, height=dynamic_height)
# ──────────────────────────────────────────
# RIGHT COLUMN
# ──────────────────────────────────────────
with right_col:

    if uploaded_file:

        # ── Your logic (untouched) ──
        results = {}
        for role, skills in SKILLS.items():
            matched = match_skills(text, skills)
            score   = calculate_score(matched, skills)
            results[role] = {"score": score, "matched": matched}

        if not results:
            st.error("No roles found ❌")
            st.stop()

        best_role      = max(results, key=lambda x: results[x]["score"])
        best_score     = results[best_role]["score"]
        best_matched   = results[best_role]["matched"]
        total_skills   = SKILLS[best_role]
        missing_skills = list(set(total_skills) - set(best_matched))[:8]

        # ── Resume Score ──
        label = score_label(best_score)
        components.html(
            '<div style="background:#ffffff;border:1px solid #e8e8e4;border-radius:14px;padding:1.2rem 1.3rem;font-family:sans-serif;">'
            '<div style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:12px;">Resume Score</div>'
            '<div style="display:flex;align-items:center;gap:24px;">'
            '<div style="position:relative;width:120px;height:120px;flex-shrink:0;">'
            '<canvas id="donutChart"></canvas>'
            '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;">'
            f'<div style="font-size:22px;font-weight:600;color:#1a1a18;">{best_score}</div>'
            '<div style="font-size:11px;color:#8a8a84;">/ 100</div>'
            '</div></div>'
            '<div style="flex:1;">'
            f'<div style="font-size:20px;font-weight:600;color:#1a1a18;margin-bottom:4px;">{label}</div>'
            f'<div style="font-size:13px;color:#8a8a84;margin-bottom:16px;">Your resume scored <strong>{best_score}</strong> out of 100</div>'
            '<div style="display:flex;flex-direction:column;gap:6px;">'
            '<div style="display:flex;justify-content:space-between;font-size:12px;">'
            '<span style="color:#8a8a84;">Matched Skills</span>'
            f'<span style="font-weight:500;color:#1d9e75;">{len(best_matched)}</span>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;font-size:12px;">'
            '<span style="color:#8a8a84;">Missing Skills</span>'
            f'<span style="font-weight:500;color:#e24b4a;">{len(missing_skills)}</span>'
            '</div>'
            '<div style="display:flex;justify-content:space-between;font-size:12px;">'
            '<span style="color:#8a8a84;">Best Role</span>'
            f'<span style="font-weight:500;color:#1a1a18;">{best_role}</span>'
            '</div>'
            '</div></div></div></div>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>'
            '<script>'
            'new Chart(document.getElementById("donutChart"), {'
            '  type: "doughnut",'
            '  data: {'
            '    datasets: [{'
            f'      data: [{best_score}, {100 - best_score}],'
            '      backgroundColor: ["#1D9E75", "#f0f0ec"],'
            '      borderWidth: 0,'
            '      circumference: 360,'
            '    }]'
            '  },'
            '  options: {'
            '    responsive: true,'
            '    maintainAspectRatio: true,'
            '    cutout: "75%",'
            '    plugins: { legend: { display: false }, tooltip: { enabled: false } }'
            '  }'
            '});'
            '</script>',
            height=180
        )

        # ── ATS Score ──
        ats_score, ats_breakdown = calculate_ats_score(text)

        ats_items_html = ""
        for category, pts in ats_breakdown.items():
            pct = (pts / 20) * 100
            if pct >= 75:
                color = "#1D9E75"
            elif pct >= 40:
                color = "#EF9F27"
            else:
                color = "#E24B4A"
            ats_items_html += (
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;">'
                f'<span style="color:#3a3a36;">{category}</span>'
                f'<span style="font-weight:500;color:{color};">{pts}/20</span>'
                f'</div>'
                f'<div style="background:#f0f0ec;border-radius:4px;height:6px;overflow:hidden;">'
                f'<div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div>'
                f'</div></div>'
            )

        if ats_score >= 80:
            ats_label = "Excellent ↑"
            ats_color = "#1D9E75"
        elif ats_score >= 60:
            ats_label = "Good ↑"
            ats_color = "#1D9E75"
        elif ats_score >= 40:
            ats_label = "Fair →"
            ats_color = "#EF9F27"
        else:
            ats_label = "Needs Work ↓"
            ats_color = "#E24B4A"

        components.html(
            '<div style="background:#ffffff;border:1px solid #e8e8e4;border-radius:14px;padding:1.2rem 1.3rem;font-family:sans-serif;">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">'
            '<div style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;">ATS Score</div>'
            f'<div style="font-size:13px;font-weight:600;color:{ats_color};">{ats_score}/100 · {ats_label}</div>'
            '</div>'
            + ats_items_html +
            '</div>',
            height=36 + len(ats_breakdown) * 46
        )

        # ── Role Prediction + Best Fit ──
        bars_html = build_role_bars_html(results)
        st.markdown(f"""
        <div class="card">
            <div class="card-label">Role Prediction</div>
            {bars_html}
            <div class="best-fit">
                <div class="best-fit-ico">✓</div>
                <div>
                    <div class="best-fit-title">Best Fit: {best_role}</div>
                    <div class="best-fit-sub">{best_score}% match · {len(best_matched)} skills matched</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Radar Chart — Skill Coverage ──
        radar_labels = list(results.keys())
        radar_scores = [results[r]["score"] for r in radar_labels]

        labels_js = str(radar_labels)
        scores_js = str(radar_scores)

        components.html(
            '<div style="background:#ffffff;border:1px solid #e8e8e4;border-radius:14px;padding:1.2rem 1.3rem;font-family:sans-serif;margin-top:14px;">'
            '<div style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:12px;">Skill Coverage by Role</div>'
            '<div style="position:relative;width:100%;height:280px;">'
            '<canvas id="radarChart" role="img" aria-label="Radar chart showing skill coverage across roles"></canvas>'
            '</div></div>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>'
            '<script>'
            f'const labels = {labels_js};'
            f'const scores = {scores_js};'
            'new Chart(document.getElementById("radarChart"), {'
            '  type: "radar",'
            '  data: {'
            '    labels: labels,'
            '    datasets: [{'
            '      label: "Match %",'
            '      data: scores,'
            '      backgroundColor: "rgba(29,158,117,0.15)",'
            '      borderColor: "#1D9E75",'
            '      borderWidth: 2,'
            '      pointBackgroundColor: "#1D9E75",'
            '      pointRadius: 4,'
            '    }]'
            '  },'
            '  options: {'
            '    responsive: true,'
            '    maintainAspectRatio: false,'
            '    scales: {'
            '      r: {'
            '        min: 0, max: 100,'
            '        ticks: { stepSize: 25, font: { size: 10 }, color: "#9e9e98" },'
            '        pointLabels: { font: { size: 11 }, color: "#3a3a36" },'
            '        grid: { color: "#f0f0ec" },'
            '        angleLines: { color: "#f0f0ec" }'
            '      }'
            '    },'
            '    plugins: { legend: { display: false } }'
            '  }'
            '});'
            '</script>',
            height=380
        )

        # ── Matched + Missing Skills ──
        skill_l, skill_r = st.columns(2, gap="medium")

        with skill_l:
            matched_tags = build_tags_html(best_matched, "tag-matched")
            st.markdown(f"""
            <div class="card">
                <div class="card-label" style="color:#3b6d11;">✦ Matched Skills</div>
                <div class="tags-wrap">{matched_tags}</div>
            </div>
            """, unsafe_allow_html=True)

        with skill_r:
            missing_tags = build_tags_html(missing_skills, "tag-missing")
            st.markdown(f"""
            <div class="card">
                <div class="card-label" style="color:#a32d2d;">✦ Missing Skills</div>
                <div class="tags-wrap">{missing_tags}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Suggestions — each missing skill as an actionable item ──
        sugg_items_html = ""
        for skill in missing_skills:
            sugg_items_html += (
                '<div style="display:flex;gap:8px;align-items:flex-start;padding:8px 12px;'
                'background:#fffdf9;border:1px solid #f5e6c8;border-radius:10px;">'
                '<div style="width:6px;height:6px;border-radius:50%;background:#ef9f27;flex-shrink:0;margin-top:4px;"></div>'
                '<div>'
                f'<div style="font-size:12.5px;color:#1a1a18;font-weight:500;">Learn {skill.title()}</div>'
                f'<div style="font-size:11px;color:#8a8a84;margin-top:1px;">Required for {best_role}</div>'
                '</div></div>'
            )

        if not sugg_items_html:
            sugg_items_html = '<p style="font-size:13px;color:#1d9e75;">Great — no major skill gaps found!</p>'

        components.html(
            '<div style="background:#ffffff;border:1px solid #e8e8e4;border-radius:14px;padding:1.2rem 1.3rem;font-family:sans-serif;">'
            '<div style="font-size:10.5px;font-weight:600;color:#9e9e98;letter-spacing:0.09em;text-transform:uppercase;margin-bottom:12px;">Suggestions to Improve</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">'
            + sugg_items_html +
            '</div></div>',
            height=80 + (((len(missing_skills) + 1) // 2) * 80)
        )

    else:
        # ── Placeholder when no file uploaded ──
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem 1.5rem;">
            <div style="font-size:36px;margin-bottom:1rem;">📄</div>
            <p style="font-size:15px;font-weight:500;color:#1a1a18;margin-bottom:6px;">No resume uploaded yet</p>
            <p style="font-size:13px;color:#8a8a84;">Upload a PDF on the left to see your score,<br>role predictions, and skill analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
