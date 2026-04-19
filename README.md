# 📄 Resume Analyzer

A smart resume analysis tool built using Streamlit that extracts key information, analyzes skills, predicts suitable roles, and provides actionable feedback.
🔗 Live Demo: https://sumit-resume-analyzer.streamlit.app/
---

## 🚀 Features

### 📂 Upload & Preview

* Upload your resume in PDF format
* Instant in-app preview

### 🔍 Information Extraction

Extracts important details:

* Name
* Email
* Phone Number
* LinkedIn
* GitHub

### 🏷️ Skill Detection

* Detects skills from resume text
* Matches them with predefined role-based skills

### 🎯 Role Prediction

* Suggests best-fit roles
* Displays match percentage for each role

### 📊 Resume Score

* Calculates score based on skill matching

### 🤖 ATS Score

Evaluates resume on:

* Contact information
* Section headings
* Action verbs
* Measurable achievements
* Resume length

### 📈 Visual Insights

* Donut chart (Resume Score)
* Radar chart (Skill coverage)
* Role comparison bars

### 💡 Suggestions

* Shows missing skills
* Provides actionable improvement tips

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** (UI)
* **PyMuPDF (fitz)** – PDF parsing
* **Regex** – Information extraction
* **Chart.js** – Data visualization

---

## 📂 Project Structure

```
resume-analyzer/
│
├── app.py              # Main application
├── utils.py            # Extraction & scoring logic
├── skills.py           # Skill datasets
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone repository

```bash
git clone https://github.com/Sumit-342/Resume-Analyzer.git
cd resume-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## ✨ Future Improvements

* Support for DOCX resumes
* Better NLP-based skill extraction
* Resume keyword optimization suggestions
* Export analysis report (PDF)

---

## 🙌 Acknowledgements

Built as a personal project to learn NLP, UI design, and real-world problem solving.
