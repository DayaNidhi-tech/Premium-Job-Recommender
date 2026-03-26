# future/resume_parser/parser.py

import pdfplumber

def parse_pdf(file_stream):
    raw_text = []

    with pdfplumber.open(file_stream) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_text.append(text)

    return "\n".join(raw_text)