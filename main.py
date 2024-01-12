import requests
from PyPDF2 import PdfReader
from general_reporter import get_general_reporter
from patient_tab import get_patient_text
from parent import get_parent_text
import spacy
import pysftp
import os
import shutil
import re
from for_country import get_country
from receipt_file import get_receipt
import json

from metapub import PubMedFetcher


# Create a FastAPI instance

# C:\Users\kathiaja\Downloads\Pvtest-main\Pvtest-main\main.py

def pdf_extraction(event=None, context=None):
    data_event = json.loads(event['body'])
    pdf_info = str(data_event['pdf_info'])
    # shutil.copy2('*', '/tmp')

    os.chdir('/tmp')
    os.makedirs('random_temp', exist_ok=True)  ### changing directory
    os.chdir('random_temp')
    try:
        shutil.copy2('/var/task/product_names.xlsx', '/tmp/random_temp')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('/var/task/medical_event_terms.xlsx', '/tmp/random_temp')
    except shutil.SameFileError:
        pass
    try:
        shutil.copy2('/var/task/postal-codes.json', '/tmp/random_temp')
    except shutil.SameFileError:
        pass

    try:
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            ftp = pysftp.Connection('testnovumgen.topiatech.co.uk', username='pvtestuser', password='Umlup01cli$$6969',
                                    cnopts=cnopts)
            print("111111111111")
            with ftp.cd('/var/sftp/upload/pvtestusers/'):
                files = ftp.listdir()
                for file in files:
                    if pdf_info in file:
                        ftp.get(file)
                        print('yes downloaded both files')
                        if 'Weekly' in file:
                            weekly_reader_1 = file
                        else:
                            source_document = file
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            response = {
                "success": False,
                "message": str(e),
                "first_file_name": weekly_reader_1,
                "second_file_name": source_document,
            }
            print(json.dumps(response))
            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            print(
                "=--------------------------------------------------------------------------------------------------------")
            # Send the POST request with JSON data
            print(response)

        weekly_reader = PdfReader(weekly_reader_1)
        source_file_reader = PdfReader(source_document)
        # weekly_reader = PdfReader('Weekly literature hits PDF.pdf')
        weekly_reader_num_pages = len(weekly_reader.pages)
        print("222222222222222")

        source_file_num_pages = len(source_file_reader.pages)
        weekly_text = ""
        all_text = ""
        nlp = spacy.load("en_core_web_sm")
        nlp_1 = spacy.load("en_ner_bc5cdr_md")
        # Loop through all pages and extract text
        for page_num in range(source_file_num_pages):
            page = source_file_reader.pages[page_num]
            text = page.extract_text()
            if "References" in text or "Bibliography" in text:
                references_found = True
                break
            all_text += text
        for page_num in range(weekly_reader_num_pages):
            page = weekly_reader.pages[page_num]
            text = page.extract_text()
            weekly_text += text
        meta = source_file_reader.metadata
        title_of_page = ""
        print("title_of_page", meta.title)
        doi = ""
        json_response_from_api = {}
        try:
            if not title_of_page or len(title_of_page.split()) < 2:
                print("checking in first block")
                text_up_to_doi_for_author = ""
                # Iterate through the lines
                for i, line in enumerate(all_text.split("\n")):
                    if "DOI:" in line or "doi:" in line:
                        text_up_to_doi_for_author = line
                        break  # Stop when the line containing "DOI:" is found
                affiliations = text_up_to_doi_for_author.split("\n")
                index_doi = text_up_to_doi_for_author.find('DOI:')
                doi_raw = text_up_to_doi_for_author[index_doi + len('doi:'):].strip()
                doi = re.sub(r'[^\x00-\x7F]+', '', doi_raw)
                if doi:
                    print("yes into pubmed")
                    fetch = PubMedFetcher()
                    print(fetch)
                    print("again", doi)
                    pmid = fetch.pmids_for_query(doi)
                    article = fetch.article_by_pmid(pmid)
                    # article = fetch.article_by_doi(doi)
                    title_of_page_1 = article.title
                    if title_of_page_1 and len(title_of_page_1.split())>2:
                        print("title length is >2")
                        title_of_page = title_of_page_1
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            title_of_page = None
            doi = None
            if title_of_page is None or doi is None:
                response = {
                    "success": False,
                    "message": "Title is not found",
                    "first_file_name": weekly_reader_1,
                    "second_file_name": source_document,
                }
                print(json.dumps(response))
                url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
                print(
                    "=--------------------------------------------------------------------------------------------------------")
                response_from_api = requests.post(url, json=response)
                print("*" * 50)
                print(response_from_api.text)
                json_response_from_api = response_from_api.json()
                # Send the POST request with JSON data
                print(response)

        country_verify = ""
        latest_receipt_date = ""
        try:
            print("checking in 2nd blcok")
            latest_receipt_date = get_receipt(en_core=nlp, weekly_text_1=weekly_text)

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            if latest_receipt_date == "":
                print("no receipt block")
                response = {
                    "success": False,
                    "message": "Latest Receipt date is not found",
                    "first_file_name": weekly_reader_1,
                    "second_file_name": source_document
                }
                url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
                print(
                    "=--------------------------------------------------------------------------------------------------------")
                # Send the POST request with JSON data
                print(response)
                response_from_api = requests.post(url, json=response)
                print("*" * 50)
                print(response_from_api.text)
                json_response_from_api = response_from_api.json()
        try:
            print("checking in 3rd block")
            country_verify = get_country(title=title_of_page, weekly_text_1=weekly_text, en_core=nlp)

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            response = {
                "success": False,
                "message": "country is not found",
                "first_file_name": weekly_reader_1,
                "second_file_name": source_document,
            }
            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            print(
                "=--------------------------------------------------------------------------------------------------------")
            # Send the POST request with JSON data
            print(response)
            response_from_api = requests.post(url, json=response)
            print("*" * 50)
            print(response_from_api.text)
            json_response_from_api = response_from_api.json()
        general_extraction = {}
        reporter_extraction = {}
        patient_extraction = {}
        parent_extraction = {}
        try:
            if title_of_page is not None and country_verify is not None and latest_receipt_date is not None:
                general_extraction, reporter_extraction = get_general_reporter(
                    source_text=all_text,
                    weekly_text_1=weekly_text,
                    en_core=nlp,
                    meta_data=meta
                )
        except Exception as e:
                print(f"Exception occurred: {str(e)}")
                response = {
                    "success": False,
                    "message": f"Exception occurred from general_reporter: {str(e)}",
                    "first_file_name": weekly_reader_1,
                    "second_file_name": source_document
                }
                url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
                print(
                    "=--------------------------------------------------------------------------------------------------------")
                # Send the POST request with JSON data
                print(response)
                response_from_api = requests.post(url, json=response)
                print("*" * 50)
                print("repsonse from api",response_from_api.text)
                json_response_from_api = response_from_api.json()
                # print(general_extraction, reporter_extraction)
        try:
            patient_extraction = get_patient_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            response = {
                "success": False,
                "message": f"Exception occurred from patient_tab: {str(e)}",
                "first_file_name": weekly_reader_1,
                "second_file_name": source_document
            }
            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            print(
                "=--------------------------------------------------------------------------------------------------------")
            # Send the POST request with JSON data
            print(response)
            response_from_api = requests.post(url, json=response)
            print("*" * 50)
            print(response_from_api.text)
            json_response_from_api = response_from_api.json()
        try:
            parent_extraction = get_parent_text(source_text=all_text, en_core=nlp, bcd5r=nlp_1)
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            response = {
                "success": False,
                "message": f"Exception occurred from parent_tab: {str(e)}",
                "first_file_name": weekly_reader_1,
                "second_file_name": source_document
            }
            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            print(
                "=--------------------------------------------------------------------------------------------------------")
            # Send the POST request with JSON data
            print(response)
            response_from_api = requests.post(url, json=response)
            print("*" * 50)
            print(response_from_api.text)
            json_response_from_api = response_from_api.json()



            response_for_integration = {
                "success": True,
                "message": "Extracted successfully",
                "first_file_name": weekly_reader_1,
                "second_file_name": source_document,
                "general_information": general_extraction,
                "reporter": reporter_extraction,
                "patient": patient_extraction,
                "parent": parent_extraction
            }

            url = "https://demo1.topiatech.co.uk/PV/createCaseAI"
            print(
                "=--------------------------------------------------------------------------------------------------------")
            # Send the POST request with JSON data
            response = requests.post(url, json=response_for_integration)
            json_response_from_api = response.json()
            print("*" * 50)
            # Check the response status code
            if json_response_from_api['success'] == 'true':
                # Request was successful
                print("API request successful.")
                # print("Status Code:", json_response_from_api['statusCode'])
                # print("Response Headers:", response.headers)
                os.chdir('..')
                shutil.rmtree('random_temp', ignore_errors=True)
                os.chdir('..')
                return {'success': json_response_from_api['success'], 'body': json.dumps(
                    {"data": 'API request successful', "error ": {'msg': str("Status Code: 200")}, "status": 5})}

            else:
                # Request failed
                os.chdir('..')
                shutil.rmtree('random_temp', ignore_errors=True)
                os.chdir('..')
                print(
                    f"API request failed with status code {json_response_from_api['success']}: {json_response_from_api['message']}")
                # print(response.text)
                return {'failure': json_response_from_api['success'],
                        'body': json.dumps({"data": 'API request not success ', "error ": {
                            'msg': str(f"API request failure with {json_response_from_api['success']}")}})}

    except Exception as e:

        os.chdir('..')

        shutil.rmtree('random_temp', ignore_errors=True)

        os.chdir('..')

        return {'statusCode': 404, 'body': json.dumps({"data": 'failed ', "error ": {'msg': str(e)}, "status": 4})}

# trail = pdf_extraction(weekly_reader_1="Weekly Literature Hits PDF_plante_khaldy.pdf", source_document="Plante MM.pdf")
