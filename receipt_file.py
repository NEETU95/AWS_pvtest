import re
import pandas as pd
import pycountry
import json
from fastapi import HTTPException
from metapub import PubMedFetcher,config
def get_receipt(en_core, weekly_text_1):
    weekly_text = weekly_text_1

    nlp = en_core
    # Initial receipt date
    weekly_doc = nlp(weekly_text)
    initial_receipt_date = ""
    latest_receipt_date = ""
    sent_line = ''
    for line in weekly_text.split('\n'):
        if 'Sent on' in line:
            sent_line = line
            break
    if sent_line:
        # Split the line at the comma and get text after the comma
        split_text = sent_line.split(',')
        if len(split_text) > 1:
            text_after_comma = split_text[1].strip()
            parsed_date = pd.to_datetime(text_after_comma, format='%Y %B %d')
            # Format the date in the desired format

            latest_receipt_date = parsed_date.strftime('%d/%m/%Y')
            # print("Initial Receipt Date:", general_information["initial_receipt_date"])
    #     else:
    #         print("can't change date")
    #
    # else:
    #     print("No 'Sent on' line found in the text.")

    # Latest receipt date

    return latest_receipt_date
