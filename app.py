import streamlit as st
from utils import extract_text_from_pdf, match_skills, calculate_score
from skills import SKILLS
import pandas as pd

st.title("🚀🚀 AI Resume Analyzer")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.write("File uploaded successfully ✅")

    # 🔹 Extract text
    text = extract_text_from_pdf(uploaded_file)

    # 🔹 Store results
    results = {}

    for role, skills in SKILLS.items():
        matched = match_skills(text, skills)
        score = calculate_score(matched, skills)

        results[role] = {
            "score": score,
            "matched": matched
        }

    # 🔹 Find best role
    if results:
        best_role = max(results, key=lambda x: results[x]["score"])
    else:
        st.error("No roles found ❌")

    # 🔹 UI Output
    st.header("📜 Extracted Text Preview")
    st.write(text[:1000])

    st.subheader("📊 Role Scores")
    for role in results:
        st.write(f"{role}: {results[role]['score']}%")

    

    df = pd.DataFrame({
    "Role": list(results.keys()),
    "Score": [results[r]["score"] for r in results]
    })

    st.subheader("📊 Role Comparison")
    st.bar_chart(df.set_index("Role"))
    # 🎯 Best Role
    st.subheader("🎯 Best Fit Role")
    st.success(best_role)

    # 🔹 Show details for BEST ROLE ONLY
    st.subheader("✅ Matched Skills")
    best_matched = results[best_role]["matched"]

    for skill in best_matched:
        st.write(f"✔ {skill}")

    # 🔹 Missing skills
    total_skills = SKILLS[best_role]
    missing_skills = list(set(total_skills) - set(best_matched))
    missing_skills = missing_skills[:8]

    st.subheader("❌ Missing Skills")
    for skill in missing_skills:
        st.write(f"❌ {skill}")