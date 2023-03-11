import io
import pandas as pd
import spacy
import re
from nltk.corpus import stopwords
from docx2txt import docx2txt
from spacy.matcher import Matcher
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


class ResumeParse:
    """
    A basic class to parse name , email, phone, skills from a resume

    inputs : Filepath, skills File
    outputs : name, email, phone, skills, education
    """
    __nlp = spacy.load('en_core_web_sm')
    __matcher = Matcher(__nlp.vocab)
    __text = ''
    # Grad all general stop words
    __STOPWORDS = set(stopwords.words('english'))

    # Education Degrees
    __EDUCATION = [
        'BE', 'B.E.', 'B.E', 'BS', 'B.S',
        'ME', 'M.E', 'M.E.', 'MS', 'M.S',
        'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
        'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII',
        'B.Sc', 'B.SC'
    ]

    def __init__(self, file_path, skill_file):
        self.file_path = file_path
        self.skill_file = skill_file

    def parse_resume(self):

        name = self.__extract_name()
        phone = self.__extract_mobile_number()
        email = self.__extract_email()
        skills = self.__extract_skills()
        education = self.__extract_education()
        return name, phone, email, skills, education

    def __extract_resume_text(self):
        if self.file_path.endswith('.pdf'):
            return self.__extract_text_from_pdf()
        elif self.file_path.endswith('.docx'):
            return self.__extract_text_from_doc()
        else:
            return 'Not a valid filepath'

    def __extract_text_from_doc(self):
        temp = docx2txt.process(self.file_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)

    def __extract_text_from_pdf(self):
        with open(self.file_path, 'rb') as fh:
            # iterate over all pages of PDF document
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                # creating a resource manager
                resource_manager = PDFResourceManager()

                # create a file handle
                fake_file_handle = io.StringIO()

                # creating a text converter object
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )

                # creating a page interpreter
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )

                # process current page
                page_interpreter.process_page(page)

                # extract text
                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()

    def __extract_name(self):

        nlp_text = self.__nlp(self.__extract_resume_text())

        # First name and Last name are always Proper Nouns
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

        self.__matcher.add('NAME', [pattern])

        matches = self.__matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def __extract_email(self):
        mail = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", self.__extract_resume_text())

        if mail:
            try:
                return mail[0].split()[0].strip(';')
            except IndexError:
                return None

    def __extract_mobile_number(self):
        phone = re.findall(re.compile(
            r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
            self.__extract_resume_text())

        if phone:
            number = ''.join(phone[0])
            if len(number) > 10:
                return '+' + number
            else:
                return number

    def __extract_skills(self):
        nlp_text = self.__nlp(self.__extract_resume_text())

        # removing stop words and implementing word tokenization
        tokens = [token.text for token in nlp_text if not token.is_stop]

        # reading the csv file
        data = pd.read_csv(self.skill_file)

        # extract values
        skills = list(data.columns.values)

        skillset = []

        # check for one-grams (example: python)
        for token in tokens:
            if token.lower() in skills:
                skillset.append(token)

        # check for bi-grams and tri-grams (example: machine learning)
        for token in nlp_text.noun_chunks:
            token = token.text.lower().strip()
            if token in skills:
                skillset.append(token)

        return [i.capitalize() for i in set([i.lower() for i in skillset])]

    def __extract_education(self):
        nlp_text = self.__nlp(self.__extract_resume_text())

        # Sentence Tokenizer
        nlp_text = [sent.text.strip() for sent in nlp_text.sents]

        edu = {}
        # Extract education degree
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                # Replace all special symbols
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in self.__EDUCATION and tex not in self.__STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]

        # Extract year
        education = []
        for key in edu.keys():
            year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
            if year:
                education.append((key, ''.join(year[0])))
            else:
                education.append(key)
        return education
