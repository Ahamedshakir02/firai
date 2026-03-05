import json
import os

from src.extract_text import extract_text_from_pdf
from src.clean_text import clean_text
from src.structure_fir import structure_fir


def process_new_fir(pdf_path):

    # 1 Extract text
    raw_text = extract_text_from_pdf(pdf_path)

    # 2 Clean text
    cleaned = clean_text(raw_text)

    # 3 Structure FIR
    fir_data = structure_fir(cleaned)

    return fir_data