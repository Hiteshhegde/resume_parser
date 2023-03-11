from pdfresparse import extract_text_from_pdf
from docresparse import extract_text_from_doc
from nameparse import extract_name
from numberparse import extract_mobile_number
from emailparse import extract_email
from skillparse import extract_skills
from resparse import ResumeParse

pdf = '/Users/hiteshhegde/Desktop/testresume.pdf'
doc_path = '/Users/hiteshhegde/Desktop/testresume.docx'
directory = '/Users/hiteshhegde/Desktop/resumes'


def parse_res(pdf_path):
    if pdf_path:
        resume_text = extract_text_from_pdf(pdf_path)
    if doc_path:
        resume_text = extract_text_from_doc(doc_path)

    name = extract_name(resume_text)
    phone = extract_mobile_number(resume_text)
    email = extract_email(resume_text)
    skills = extract_skills(resume_text)

    return name, phone, email, skills


resume_parser = ResumeParse(doc_path, "skills.csv")

print(resume_parser.parse_resume())

