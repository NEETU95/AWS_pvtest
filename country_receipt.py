import re
import pandas as pd
import pycountry
import json
from fastapi import HTTPException
from metapub import PubMedFetcher,config
def get_country_receipt(source_text, en_core, weekly_text_1, meta_data):
    all_text = source_text
    nlp = en_core
    pmid_pattern = re.compile(r'\b\d{8}\b')  # Assumes PMIDs are 8-digit numbers

    # Search for PMIDs in the PDF text
    matches = re.findall(pmid_pattern, all_text)
    if matches:
        # print(matches)
        pass
    # weekly_reader = PdfReader("Weekly literature Hits PDF-sosa.pdf")
    # # Get the number of pages in the PDF
    # weekly_num_pages = len(weekly_reader.pages)

    # Initialize an empty string to store the extracted text
    weekly_text = weekly_text_1

    # # Loop through all pages and extract text
    # for page_num in range(weekly_num_pages):
    #     page = weekly_reader.pages[page_num]
    #     text = page.extract_text()
    #     weekly_text += text

    # print("weekly text is", weekly_text)

    ###############################################

    # Finding author name using title
    meta = meta_data
    weekly_doc = nlp(weekly_text)
    doc = nlp(all_text)
    title_of_page = meta.title
    #print("title", title_of_page)

    title_from_literature = ""
    author_name = " "
    extracted_text = ""
    text_lines = ""
    doi = ""
    country_for_final = ""
    latest_receipt_date = ""
    success = True
    message = ""
    if not title_of_page:
        text_up_to_doi_for_author = ""
        # Iterate through the lines
        for line in all_text.split("\n"):
            for line in all_text.split("\n"):
                if "DOI:" in line or "doi:" in line:
                    text_up_to_doi_for_author = line
                    break  # Stop when the line containing "DOI:" is found
            affiliations = text_up_to_doi_for_author.split("\n")
            index_doi = text_up_to_doi_for_author.find('DOI:')
            doi_raw = text_up_to_doi_for_author[index_doi + len('doi:'):].strip()
            doi = re.sub(r'[^\x00-\x7F]+', '', doi_raw)
        #print("doi", doi)
        if not doi:
            print('yes')
            raise HTTPException(status_code=11, detail="DOI not found from source document")
        else:
            #print("yes into pubmed")
            fetch = PubMedFetcher()
            ##print(fetch)
            #print("again", doi)
            article = fetch.article_by_doi(doi)
            if article:
                title_of_page = article.title
            else:
                success = False

            # print("article is", article)
            if article is None:
                success = False
                #print("success", success)
            author = article.authors[0]
            digital_object_identifier = doi
            literature_reference = article.citation
            vol = article.volume
            year = article.year
            journal = article.journal
            page = article.pages
            if page and not any(char.isalpha() for char in page):
                pages = page

    #print('1')

    # getting title from literature
    #print('6')
    if title_of_page:
        #print('7')
        # print('title is', title_of_page)
        if title_of_page.split()[0] and title_of_page.split()[1] and title_of_page.split()[2] in weekly_doc.text:
            weekly_split = weekly_text.split('\n')
            #print('8')
            # print(weekly_split)
            for i, line in enumerate(weekly_split):
                # print(line)
                if (
                        title_of_page.split()[0] in line
                        and
                        title_of_page.split()[1] in line
                        and
                        title_of_page.split()[3] in line
                        and
                        title_of_page.split()[4] in line
                ):
                    line_index = i
                    # print('line_index', line_index)
                    extracted_text = '\n'.join(weekly_split[line_index + 1:])
                    # print('extracted_text', extracted_text)
                    #print('10')
                    break

            text_lines = extracted_text.split('\n')

            author_line = None
            text_up_to_affiliations = ""
            #print('9')
            for line in text_lines:
                if "Affiliations" in line:
                    break  # Stop when the line containing "DOI:" is found
                text_up_to_affiliations += line
            # print('text_up_to', text_up_to_affiliations)
            affiliations = text_up_to_affiliations.split("\n")
            # print(affiliations)
            # Extract text between "Authors" and the first occurrence of "1" after "Affiliations"
            match = re.search(r'Authors([\s\S]*?)\b1\b', text_up_to_affiliations)
            if match:
                author_name_before_1 = match.group(1).strip()
                if ',' in author_name_before_1:
                    first_author_name = author_name_before_1.split(',')[1]
                    author_name = re.sub(r'\d', '', first_author_name)
                    # print(author_name)
                else:
                    first_author_name = author_name_before_1
                    author_name = re.sub(r'\d', '', first_author_name)
                    # print(author_name)
            #print('10')

        # General tab
        # print("###### General #######")
        general_information = {
            "type_of_report": "Other(Literature)",
            "initial_receipt_date": "",
            "latest_receipt_date": "",
            "country": "",
            "medically_confirmation": "Yes",
            "expedited_report": "",
            "first_sender": "Other",
            "report_nullification_or_amendment": "",
            "reason_for_nullification_or_amendment": ""

        }

        type_of_report = "Other(Literature)"
        # print("Type of report:", type_of_report)

        # Initial receipt date
        weekly_doc = nlp(weekly_text)
        initial_receipt_date = ""
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
                general_information["initial_receipt_date"] = parsed_date.strftime('%d/%m/%Y')
                latest_receipt_date = parsed_date.strftime('%d/%m/%Y')
                # print("Initial Receipt Date:", general_information["initial_receipt_date"])


        # Latest receipt date
        general_information["latest_receipt_date"] = general_information["initial_receipt_date"]
        if not general_information["latest_receipt_date"]:
            success = False
            message = "Latest Receipt Date is not Found."

        # country
        found_countries = ""
        found_cities = []
        text_up_to_doi = ""
        is_part_of_city = False
        city = ""
        if author_name.lower() in weekly_doc.text.lower():
            #print('author_name', author_name.lower())
            #print('11')
            # Find the index of the specific word
            word_index = weekly_doc.text.find(author_name)

            # Extract text after the specific word
            extracted_text = weekly_doc.text[word_index + len(author_name):]
            # Iterate through the lines
            for line in extracted_text.split("\n"):
                # #print('line is', line)
                #print('12')
                if "DOI:" in line or "doi" in line:
                    break  # Stop when the line containing "DOI:" is found
                text_up_to_doi += line
                # print("text upto doi",text_up_to_doi)
            affiliations = text_up_to_doi.split("\n")
            # Loop through affiliations and search for country names and cities
            for affiliation in affiliations:
                country_found = False  # Flag to indicate if a country has been found in this affiliation
                deleted_countries = ['Iran', 'South Korea', 'North Korea', 'Korea', 'Sudan', 'MACAU',
                                     'Republic Of Ireland',
                                     'USA']
                for i in deleted_countries:
                    if i in affiliation:
                        found_countries = i
                        country_found = True
                        break

                for country in pycountry.countries:
                    if country.name in affiliation and not found_countries:
                        found_countries = country.name
                        country_found = True
                        break  # Stop searching for country names in this affiliation
                country_doc = nlp(affiliation)
                for token in country_doc:
                    if token.ent_type_ == "GPE" and token.text:
                        if not is_part_of_city:
                            is_part_of_city = True
                            city = token.text
                        else:
                            city += " " + token.text
                    else:
                        if is_part_of_city:
                            found_cities.append(city)
                            is_part_of_city = False
                            city = ""
            countries = " "
            # If the city string isn't finished at the end
            if is_part_of_city != found_countries:
                found_cities.append(city)

            general_information["country"] = found_countries
            country_for_final = found_countries
            if not general_information["country"]:
                success = False
                message = "Country is not Found."

    return country_for_final, latest_receipt_date
