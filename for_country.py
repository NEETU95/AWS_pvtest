import re
import pandas as pd
import pycountry
import json
from fastapi import HTTPException
from metapub import PubMedFetcher, config

def get_country(title, weekly_text_1, en_core):
    title_of_page = title
    weekly_text = weekly_text_1
    nlp = en_core
    extracted_text = ""
    weekly_doc = nlp(weekly_text)

    # Initialize variables to avoid UnboundLocalError
    author_name = ""
    found_countries = ""

    # getting title from literature
    print('6')
    if title_of_page:
        print('7')
        if all(word in weekly_doc.text for word in title_of_page.split()[:3]):
            weekly_split = weekly_text.split('\n')
            print('8')
            for i, line in enumerate(weekly_split):
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
                    extracted_text = '\n'.join(weekly_split[line_index + 1:])
                    print('10')
                    break

            text_lines = extracted_text.split('\n')

            author_line = None
            text_up_to_affiliations = ""
            print('9')
            for line in text_lines:
                if "Affiliations" in line:
                    break
                text_up_to_affiliations += line

            affiliations = text_up_to_affiliations.split("\n")

            match = re.search(r'Authors([\s\S]*?)\b1\b', text_up_to_affiliations)
            if match:
                author_name_before_1 = match.group(1).strip()
                if ',' in author_name_before_1:
                    first_author_name = author_name_before_1.split(',')[1]
                    author_name = re.sub(r'\d', '', first_author_name)
                else:
                    first_author_name = author_name_before_1
                    author_name = re.sub(r'\d', '', first_author_name)
                print('10')

            # country
            found_countries = ""
            found_cities = []
            text_up_to_doi = ""
            is_part_of_city = False
            city = ""

            if author_name.lower() in weekly_doc.text.lower():
                print('author_name', author_name.lower())
                print('11')
                # Find the index of the specific word
                word_index = weekly_doc.text.find(author_name)

                # Extract text after the specific word
                extracted_text = weekly_doc.text[word_index + len(author_name):]
                # Iterate through the lines
                for line in extracted_text.split("\n"):
                    # print('line is', line)
                    print('12')
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
                print("found_countries", found_countries)

    return found_countries
