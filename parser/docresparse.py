import docx2txt

doc_path = '/Users/hiteshhegde/Desktop/testresume.docx'


def extract_text_from_doc(doc_path):
    temp = docx2txt.process(doc_path)
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    return ' '.join(text)

# print(extract_text_from_doc(doc_path))
