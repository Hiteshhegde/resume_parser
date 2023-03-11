import re


def extract_email(email):
    mail = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)

    if mail:
        try:
            return mail[0].split()[0].strip(';')
        except IndexError:
            return None
