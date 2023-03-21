import os

from docresparse import extract_text_from_doc
from emailparse import extract_email
from nameparse import extract_name
from numberparse import extract_mobile_number
from pdfresparse import extract_text_from_pdf
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


# resume_parser = ResumeParse(doc_path, "skills.csv")

# print(resume_parser.parse_resume())


def get_file_paths(dir_path):
    files = []
    for file in os.listdir(dir_path):
        f = os.path.join(dir_path, file)

        if os.path.isfile(f):
            files.append(str(f))

    return files


resumes = get_file_paths(directory)
for resume in resumes:
    resume_parser = ResumeParse(resume, "skills.csv")

    print(resume_parser.parse_resume())
