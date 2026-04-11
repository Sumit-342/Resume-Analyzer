import PyPDF2

def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text.lower()
    

def match_skills(text, skills):
    matched = []

    for skill in skills:
        if skill.lower() in text:
            matched.append(skill)

    return matched


def calculate_score (matched,total_skills):
    return int((len(matched) /  len(total_skills)) * 100)

