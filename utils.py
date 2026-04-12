import PyPDF2
import fitz


def extract_text_from_pdf(pdf_file):
    pdf = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (round(b[1] / 20), b[0]))
        for block in blocks:
            text += block[4] + "\n"
    return text
    

def match_skills(text, skills):
    matched = []
    text_lower = text.lower()
    for skill in skills:
        if skill.lower() in text_lower:
            matched.append(skill)
    return matched


def calculate_score (matched,total_skills):
    return int((len(matched) /  len(total_skills)) * 100)

