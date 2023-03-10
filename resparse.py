import pandas as pd
import spacy
import re
from docx2txt import docx2txt
from spacy.matcher import Matcher


class ResumeParse:
    """
    A basic class to parse name , email, phone, skills from a resume

    inputs : Filepath, skills File
    outputs : name, email, phone, skills
    """
    __nlp = spacy.load('en_core_web_sm')
    __matcher = Matcher(__nlp.vocab)

    def __init__(self, file_path, skill_file):
        self.file_path = file_path
        self.skill_file = skill_file

    def parse_resume(self):
        if not self.file_path:
            return "enter a valid file_path"

        name = self.__extract_name()
        phone = self.__extract_mobile_number()
        email = self.__extract_email()
        skills = self.__extract_skills()

        return name, phone, email, skills

    def __extract_text_from_doc(self):
        temp = docx2txt.process(self.file_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)

    def __extract_name(self):

        nlp_text = self.__nlp(self.__extract_text_from_doc())

        # First name and Last name are always Proper Nouns
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

        self.__matcher.add('NAME', [pattern])

        matches = self.__matcher(nlp_text)

        for match_id, start, end in matches:
            span = nlp_text[start:end]
            return span.text

    def __extract_email(self):
        mail = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", self.__extract_text_from_doc())

        if mail:
            try:
                return mail[0].split()[0].strip(';')
            except IndexError:
                return None

    def __extract_mobile_number(self):
        phone = re.findall(re.compile(
            r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),
            self.__extract_text_from_doc())

        if phone:
            number = ''.join(phone[0])
            if len(number) > 10:
                return '+' + number
            else:
                return number

    def __extract_skills(self):
        nlp_text = self.__nlp(self.__extract_text_from_doc())

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
