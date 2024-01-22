import spacy
from PyPDF2 import PdfReader
import pandas as pd
import re
import json

#
# reader = PdfReader('Senkoro E_.pdf')
# source_file_num_pages = len(reader.pages)
#
# all_text = ""
#
# # Loop through all pages and extract text
# for page_num in range(source_file_num_pages):
#     page = reader.pages[page_num]
#     text = page.extract_text()
#     all_text += text
#
# print(all_text)
def get_events_tab(source_text, country):
    try:
        all_text = source_text
        nlp_1 = spacy.load("/var/task/custom_ner_model_with_disease")
        nlp_2 =spacy.load("/var/task/custom_ner_model_with_disease_1")
        test = """she developed mental shocks, seizures, anemia. and also fever. there is rise in immunoglobulin"""
        doc = nlp_1(test)
        for ent in doc.ents:
            if ent.label_ == "DISEASE":
                print(ent.text)

        report_to_discussion = ""
        first_three_lines = ""
        abstract_keywords = ["Introduction", "Abstract", "INTRODUCTION", "ABSTRACT"]
        case_keywords = ["Case Presentation", "Case presentation", "Case summary", "Case history", "Case Summary", "Case History", "Case description", "Case Report",
                             "Case report", "CASE", "Case", "CASE REPORT", "CASE DESCRIPTION", "CASE PRESENTATION", "CASE HISTORY", "CASE SUMMARY"]
        found_case_type = None
        text_after_case_type = ""
        all_reaction_information = []
        abstract_to_end = ""
        found_start_line_second = ""
        abstract_to_end_first = ""
        doc = nlp_1(all_text)
        for keyword in case_keywords:
            if keyword in all_text:
                #print("keyword is presnet")
                found_case_type = keyword
                break
        if "An official website of the United States government" in all_text:
            word_index = doc.text.find("Affiliations")
            word_index_keyword = doc.text.find("Keywords")
            #print(word_index_keyword)
            extracted_text = doc.text[word_index:word_index_keyword]
            # text_lines = text_after_case_type.split('\n')
            first_three_lines = extracted_text
            report_to_discussion = extracted_text
        else:
            abstract_terms = ["Introduction", "Abstract", "INTRODUCTION", "ABSTRACT"]
            count = 0
            found_start_line = -1
            end_line = -1
            searching = ""
            for i, line in enumerate(all_text.split('\n')):
                for searching in abstract_terms:
                    if searching in line:
                        #print("yes abstract keyword is present")
                        count += 1
                        found_start_line = i
                        break
            print("found_start_line is", found_start_line)
            # print("count is", count)
            if count > 0 and found_start_line != -1:
                #print("second yes")
                # Extract the found line and the subsequent 7 lines
                extracted_lines_from_abstract = all_text.split('\n')[found_start_line+len(searching):]
                # print(extracted_lines)
                abstract_to_end_first = '\n'.join(extracted_lines_from_abstract)
                print("abstract to end", abstract_to_end_first)
            count_2 = 0
            for i, line in enumerate(abstract_to_end_first.split('\n')):
                for searching in abstract_terms:
                    if searching in line:
                        #print("yes abstract keyword is present second time", line)
                        count_2 += 1
                        print("count is", count_2)
                        found_start_line_second = i
                    break
            #print("found_start_line second time is", found_start_line_second)
            # print("count is", count)
            if count_2 > 0 and found_start_line_second != -1:
                #print("second yes")
                # Extract the found line and the subsequent 7 lines
                extracted_lines_from_abstract = abstract_to_end_first.split('\n')[found_start_line:]
                # print(extracted_lines)
                abstract_to_end = '\n'.join(extracted_lines_from_abstract)
                print("abstract to end from count 2", abstract_to_end)
            else:
                abstract_to_end = abstract_to_end_first

            #print("abstract_to_end", abstract_to_end)

            case_keywords = ["Case Presentation", "Case presentation", "Case summary", "Case history", "Case Summary",
                             "Case History", "Case description", "Case Report","Case",
                             "Case report", "CASE", "CASE REPORT", "CASE DESCRIPTION", "CASE PRESENTATION", "CASE HISTORY",
                             "CASE SUMMARY"]
            found_case_type = None
            count_for_case = 0
            found_start_line_for_case = -1
            end_line = -1

            print("split of ab_to_end*****", abstract_to_end.split('\n'))
            for i, line in enumerate(abstract_to_end.split("\n")):
                for searching in case_keywords:
                    if searching in line:
                        print("Yes case keyword is present")
                        print("line is", line)
                        print("case keyword is", searching)

                        count_for_case += 1
                        print("count_for_case is",count_for_case)
                        if count_for_case == 1:
                            found_start_line_for_case = i
                            print(i)
                        break
                # Stop searching if a keyword is found in the line

                # Assuming you want to store the line index where "Case Report" is found
                if any(keyword in line for keyword in ["Discussion", "Conclusion", "DISCUSSION", "CONCLUSION"]):
                    print("line", line)
                    print("i", i)
                    end_line = i
                    break

            print("found_start_line_for_case is", found_start_line_for_case)

            # print("count is", count)

            if count_for_case > 0 and found_start_line_for_case != -1:
                print("second yes")
                # Extract the found line and the subsequent 7 lines
                extracted_lines = abstract_to_end.split('\n')[found_start_line_for_case:(end_line+1)]
                #print(extracted_lines)
                report_to_discussion = '\n'.join(extracted_lines)
                print("report to discussion is", report_to_discussion)
                first_three_lines_split = report_to_discussion.split("\n")[:10]
                first_three_lines = '\n'.join(first_three_lines_split)
                # if count > 0:
                #     extracted_text = doc.text[word_index:]
                #     text_lines = extracted_text.split('\n')
                #     first_three_lines = '\n'.join(text_lines[:8])
        # else:
        #     # print("Found case type:", found_case_type)
        #     word_index = doc.text.find(found_case_type)
        #     end_word_index = doc.text.find("Discussion")
        #     # Extract text after the specific word
        #     extracted_text = doc.text[word_index + len(found_case_type):  end_word_index]
        #     text_after_case_type = all_text.split(found_case_type, 1)[-1]
        #     text_lines = extracted_text.split('\n')
        #     report_to_discussion = '\n'.join(text_lines)
        #     first_three_lines_split = report_to_discussion.split("\n")[:10]
        #     first_three_lines = '\n'.join(first_three_lines_split)
        #     print(report_to_discussion)
        previous_lines = []
        text_before_medicine = ""
        text_after_medicine = """"""
        products = pd.read_excel("product_names.xlsx")
        # def join_lines(lines):
        #     joined_lines = []
        #     current_line = ""
        #
        #     for line in lines:
        #         if line.endswith('-'):
        #             current_line += line.rstrip('-').rstrip()
        #         else:
        #             current_line += line
        #             joined_lines.append(current_line)
        #             current_line = ""
        #
        #     if current_line:
        #         joined_lines.append(current_line)
        #
        #     return joined_lines

        count_for_drug = 0
        for line_number, line in enumerate(report_to_discussion.split('\n')):
            # Check if medicine has already been found
            if not text_before_medicine:
                for drug in products['product_name']:
                    if drug.lower() in line.lower():
                        print("found drug is", drug)

                        count_for_drug += 1
                        print("count for drug", count_for_drug)

                        line_index = line.lower().find(drug.lower())
                        print(line_index)
                        text_line = line[:line_index + len(drug)]
                        print(text_line)
                        # Combine the current line and the previous lines before the medicine
                        text_before_medicine += "\n".join(previous_lines) + "\n" + text_line + "\n"

                        lines = report_to_discussion.split('\n')[line_number + 1:]
                        print(lines)
                        # Extract lines after the medicine is found (adjust line_number accordingly)
                        text_after_medicine = "\n".join(lines)

                        # Clear previous_lines for the next iteration
                        previous_lines = []

                        # Stop searching for other drugs in the same line once one is found
                        break


            # If medicine is not found in the current line, store the line in previous_lines
            if not text_before_medicine:
                previous_lines.append(line)


        print("Text Before Medicine:")
        print(text_before_medicine)
        #
        print("\nText After Medicine:")
        print(text_after_medicine)
        cleaned_text = re.sub(r'\s*\n\s*', ' ', text_after_medicine)
        cleaned_text = re.sub(r'\s*-\s*', '-', cleaned_text)
        text_after_medicine = cleaned_text
        #print(cleaned_text)

        # all_functions
        def check_keywords(every_line, keywords):
            return any(every_keyword.lower() in every_line.lower() for every_keyword in keywords)

        # finding all events from text_after_medicine where there is no negative ones.

        llt_indicators = []
        # checking if the events are history and also improved or not resolved.
        history_llt = []
        doc = nlp_1(text_before_medicine)
        for ent in doc.ents:
            if ent.label_ == 'DISEASE':
                history_llt.append(ent.text)
        print("Events from medical history:", history_llt)

        doc = nlp_1(text_after_medicine)
        drugs_after_our_drug = []
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL" and ent.text != 'BA':
                drugs_after_our_drug.append(ent.text)

        print("drugs after our medicine:", drugs_after_our_drug)
        text_up_to_drug = ""
        text_after_drug = ""
        events_llt_repeated = []
        llt = []
        line_up_to_next_disease = ""

        doc = nlp_1(text_after_medicine)
        for ent in doc.ents:
            if ent.label_ == "DISEASE" and ' no ' not in ent.text.lower():
                llt.append(ent.text)
        #print("llt:", llt)
        text_split = text_after_medicine.split('.')
        for line in text_split:
            for ent in llt:
                if ent in line and not re.search(r'\bno\b', line):
                    events_llt_repeated.append(ent)


        # using customed and trained from our side
        doc = nlp_2(text_after_medicine)
        for ent in doc.ents:
            if ent.label_ == "DISEASE" and ' no ' not in ent.text.lower():
                llt.append(ent.text)
        # print("llt:", llt)
        text_split = text_after_medicine.split('.')
        for line in text_split:
            for ent in llt:
                if ent in line and not re.search(r'\bno\b', line):
                    events_llt_repeated.append(ent)

        events_llt_raw = list(set(events_llt_repeated))
        print("events_llt", events_llt_raw)

        resolved_keywords = ['stabilized', 'recovered', 'normalized', 'resolved', 'improved', 'disappeared', 'absense', 'heal', 'regulated', 'cleared', 'absen', 'reduction', 'reduced', 'responded well']
        not_resolved_keywords = ['not stabilized', 'not recovered', 'not normalized', 'not resolved', 'not improved', 'not disappeared', 'not absense', 'not heal', 'not regulated', 'not cleared', 'no reduction', 'not reduced', 'not responded']
        resolving_keywords = ['resolving', 'normalizing', 'recovering', 'stabilizing', 'improving', 'disappearing', 'healing', 'regulating']
        sequelae_keywords = ['disabled', 'chronic-illness', 'cognitive', 'handicapped', 'mental-illness','mental illness', 'impairment']
        fatal_keywords = ['terminal', 'life-threat', 'life threat', 'mortal', 'fatal', 'dead']
        unchanged_keywords = ['stable', 'unchanged', 'static', 'persistent', 'consistent', 'no improvement', 'no change']
        worsened_keywords = ['deteriorated', 'worsened', 'aggravated', 'relapse']

        events_llt = []
        # To check history_llt is in current llt or not
        for i, event in enumerate(events_llt_raw):
            if event in history_llt:
                print("matched from history llt", event)
                print("yes there are events matched form medical history")

                llt_start_index = text_after_medicine.find(event)
                next_disease_index = i + 1
                period_before_llt_index = ""
                # Check if llt is found
                if llt_start_index != -1:
                    # Find the period before llt
                    period_before_llt_index = text_after_medicine.rfind(".", 0, llt_start_index)
                if next_disease_index < len(events_llt_raw):
                    next_disease = events_llt_raw[next_disease_index]

                    next_disease_start_index = text_after_medicine.find(next_disease, llt_start_index)
                    period_before_next_disease = text_after_medicine.rfind(".", 0, next_disease_start_index)
                    if next_disease_start_index != -1:
                        line_up_to_next_disease = text_after_medicine[period_before_llt_index:period_before_next_disease]
                    if line_up_to_next_disease == "":
                        # Start searching for period after llt_start_index
                        for i in range(llt_start_index, len(text_after_medicine)):
                            if text_after_medicine[i] == '.':
                                index_after_llt = i
                                line_up_to_next_disease = text_after_medicine[period_before_llt_index:index_after_llt]
                                break
                    lines = line_up_to_next_disease.split('.')
                    found_keyword = False
                    # Iterate through lines and check for keywords
                    for line in lines:
                        if not check_keywords(line, resolved_keywords):

                            found_keyword = True
                            events_llt.append(event)
                            print("found_keyword from first for history_check", found_keyword)
                            print("present in resolved for history check", llt)
                            print(f"Resolved for history_check: {line}")
                            break
                        elif not check_keywords(line, resolving_keywords):

                            found_keyword = True
                            events_llt.append(event)
                            print("present in resolving for history_check", llt)
                            print(f"Resolving for history_check: {line}")
                            break
                        elif not check_keywords(line, unchanged_keywords):

                            found_keyword = True
                            events_llt.append(event)
                            print("present in unchanged for history_check ", llt)
                            print(f"Unchanged for history_check: {line}")
                            break

            else:
                print("there are no history llt")
                events_llt.append(event)
        print("after history filter", events_llt)

        term_highlighted_by_reporter_keywords = ['Yes, highlighted by the reporter, Not serious', 'No, not highlighted by the reporter, Not serious', 'Yes, highlighted by the reporter, Serious', 'No, not highlighted by the reporter, Serious']
        term_highlighted_by_reporter = ""



        comments = ""
        results_in_death = ""
        life_threatening = ""
        hospitalized = ""
        disabled = ""
        congenital = ""


        outcome_of_the_events_keywords = ['Unknown', 'Recovered/Resolved', 'Recovering/Resolving', 'Not Recovered/Not Resolved/Ongoing', 'Recovered/Resolved with Sequelae', 'Fatal', 'Unchanged', 'Worsened']
        outcome_of_the_events = ""


        def find_lines_with_keywords(keyword_list, keyword_lines):
            lines_with_keywords = []
            for every_line in keyword_lines:
                if any(events_keyword in every_line.lower() for events_keyword in keyword_list):
                    lines_with_keywords.append(every_line)
            return lines_with_keywords



        def is_common_word(word):
            common_words = {'the', 'in', 'a', 'and', 'to', 'of', 'for', 'with', 'on', 'at', 'by', 'from', 'as'}
            return word.lower() not in common_words


        text_lines = text_after_medicine.split('.')
        print(text_lines)
        resolved_lines = find_lines_with_keywords(resolved_keywords, text_lines)
        not_resolved_lines = find_lines_with_keywords(not_resolved_keywords, text_lines)
        resolving_lines = find_lines_with_keywords(resolving_keywords, text_lines)
        sequelae_lines = find_lines_with_keywords(sequelae_keywords, text_lines)
        fatal_lines = find_lines_with_keywords(fatal_keywords, text_lines)
        unchanged_lines = find_lines_with_keywords(unchanged_keywords, text_lines)
        worsened_lines = find_lines_with_keywords(worsened_keywords, text_lines)

        outcome_llt = set()

        event_terms = pd.read_excel("medical_event_terms.xlsx")

        for i, llt in enumerate(events_llt):
            llt_start_index = text_after_medicine.find(llt)
            next_disease_index = i + 1
            period_before_llt_index = ""
            # Check if llt is found
            if llt_start_index != -1:
                # Find the period before llt
                period_before_llt_index = text_after_medicine.rfind(".", 0, llt_start_index)
            if next_disease_index < len(events_llt):
                next_disease = events_llt[next_disease_index]

                next_disease_start_index = text_after_medicine.find(next_disease, llt_start_index)
                period_before_next_disease = text_after_medicine.rfind(".", 0, next_disease_start_index)
                if next_disease_start_index != -1:
                    line_up_to_next_disease = text_after_medicine[period_before_llt_index:period_before_next_disease]
                if line_up_to_next_disease == "":
                    # Start searching for period after llt_start_index
                    for i in range(llt_start_index, len(text_after_medicine)):
                        if text_after_medicine[i] == '.':
                            index_after_llt = i
                            line_up_to_next_disease = text_after_medicine[period_before_llt_index:index_after_llt]
                            break


                hospitalized_keywords = ['admitted', 'admission', 'hospitalized', 'checked']
                abnormality_keywords = ['abnormality', 'birth defects', 'birth-defects', 'anomaly']
                dead_keywords = ["expired", "died", "dead", "passed away", "demised", "murdered", "lost life"]
                death_comments = ""
                text = ""
                death_text = ""
                dod = ""
                lines = line_up_to_next_disease.split("\n")
                print("lines are", lines)


                pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, dead_keywords)) + r')\b', flags=re.IGNORECASE)

                # Search for the keywords in the text
                matches = pattern.findall(line_up_to_next_disease)

                # Output the matches
                if matches:
                    results_in_death = 'Yes'

                else:
                    results_in_death = 'No'
                # for line in lines:
                #     for keyword in dead_keywords:
                #         if keyword in line:
                #             results_in_death = 'Yes'
                #             break
                #         else:
                #             results_in_death = 'No'
                # if 'died' in text_after_medicine or 'dead' in text_after_medicine:
                #     results_in_death = 'Yes'
                # else:
                #     results_in_death = 'No'
                if 'life-threat' in line_up_to_next_disease or 'mortal' in line_up_to_next_disease:
                    life_threatening = 'Yes'
                else:
                    life_threatening = 'No'
                for hospi in hospitalized_keywords:
                    if hospi in text_before_medicine:
                        hospitalized = 'Yes'
                        break
                    elif hospi in text_after_medicine:
                        hospi_start_index = text_after_medicine.find(hospi)
                        hospitalized_lines = text_after_medicine[hospi_start_index:]
                        hospitalized = 'Yes'
                        break
                    else:
                        hospitalized = 'No'
                if 'disabled' in line_up_to_next_disease or 'chronic' in line_up_to_next_disease:
                    disabled = 'Yes'
                else:
                    disabled = 'No'
                for congi in abnormality_keywords:
                    if congi in text_before_medicine:
                        congenital = 'Yes'
                        break
                    else:
                        congenital = 'No'

                #
                duration = ""
                time_unit = ""
                time_units = ["year", "years", "days", "day", "decades", "decade", "months", "month", "hours", "hour", "week", "weeks", "second","seconds"]


                # Regular expression pattern to match age information with hyphen and different time units
                pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
                duration_pattern = re.compile(pattern)
                matches = duration_pattern.findall(line_up_to_next_disease)
                if matches:
                    ages, time_unit_ = int(matches[0][0]), matches[0][1]
                    match_index = line_up_to_next_disease.find(matches[0][1], first_three_lines.find(matches[0][0]))
                    if match_index != -1 and line_up_to_next_disease.find("old", match_index) != -1:
                        duration = ages
                        time_unit = time_unit_




                other_medically_important_condition = ""

                for event in event_terms['event_terms']:
                    if event in llt:
                        other_medically_important_condition = 'Yes'
                        print(event)
                        break
                    else:
                        other_medically_important_condition = 'No'

                if results_in_death == "Yes" or life_threatening == "Yes" or hospitalized == "Yes" or disabled == "Yes" or congenital == "Yes" or other_medically_important_condition =='Yes':
                    term_highlighted_by_reporter = term_highlighted_by_reporter_keywords[2]
                else:
                    term_highlighted_by_reporter = term_highlighted_by_reporter_keywords[0]
                # resolving outcome of events
                lines = line_up_to_next_disease.split('.')
                found_keyword = False
                # Iterate through lines and check for keywords
                for line in lines:
                    if check_keywords(line, sequelae_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[4]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in sequele", llt)
                        print(f"Sequelae: {line}")
                        break

                    elif check_keywords(line, resolved_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[1]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("found_keyword from first", found_keyword)
                        print("present in resolved", llt)
                        print(f"Resolved: {line}")
                        break
                    elif check_keywords(line, not_resolved_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[2]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in not resolved", llt)
                        print(f"NOT Resolved: {line}")
                        break
                    elif check_keywords(line, resolving_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[3]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in resolving", llt)
                        print(f"Resolving: {line}")
                        break

                    elif check_keywords(line, fatal_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[5]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in fatal", llt)
                        print(f"Fatal: {line}")
                        break
                    elif check_keywords(line, unchanged_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[6]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in unchanged", llt)
                        print(f"Unchanged: {line}")
                        break
                    elif check_keywords(line, worsened_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[7]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in worsened", llt)
                        print(f"Worsened: {line}")
                        break
                found_keyword_second = False

                if found_keyword is not True:
                    resolved_words = [word.lower() for line in resolved_lines for word in line.split()]
                    print("resolved words are", resolved_words)

                    words_in_line = [word for word in line_up_to_next_disease.lower().split() if is_common_word(word)]
                    print("About remaining llt", llt)
                    print("line_up_to_next_disease", line_up_to_next_disease)

                    common_words = {'the', 'in', 'a', 'and', 'to', 'of', 'for', 'with', 'on', 'at', 'by', 'from', 'as',
                                    'all'}  # Add other common words as needed

                    matching_words = [word for word in resolved_words if
                                      word not in common_words and word in line_up_to_next_disease.lower().split()]
                    resolved_matching_llt = []
                    doc_resolved = nlp_1(''.join(matching_words))
                    for ent in doc_resolved.ents:
                        if ent.label_ == "DISEASE":
                            resolved_matching_llt.append(ent.text)
                    if matching_words and any(word in resolved_matching_llt for word in matching_words):
                        outcome_of_the_events = outcome_of_the_events_keywords[1]
                        found_keyword_second = True
                        print("found_keyword from secon", found_keyword)
                        print("This event has matched from previous:", llt)
                        print("Matching Words:", matching_words)

                    not_resolved_words = [word.lower() for line in not_resolved_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_not_resolved = [word for word in not_resolved_words if
                                                       word not in common_words and word in line_up_to_next_disease.lower()]
                    not_resolved_matching_llt = []
                    doc_not_resolved = nlp_1(''.join(matching_words_for_not_resolved))
                    for ent in doc_not_resolved.ents:
                        if ent.label_ == "DISEASE":
                            not_resolved_matching_llt.append(ent.text)

                    if matching_words_for_not_resolved and any(word in not_resolved_matching_llt for word in matching_words_for_not_resolved):
                        outcome_of_the_events = outcome_of_the_events_keywords[2]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_not_resolved)

                    resolving_words = [word.lower() for line in resolving_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_resolving = [word for word in resolving_words if
                                                    word not in common_words and word in line_up_to_next_disease.lower()]
                    resolving_matching_llt = []
                    doc_resolving = nlp_1(''.join(matching_words_for_resolving))
                    for ent in doc_resolving.ents:
                        if ent.label_ == "DISEASE":
                            resolving_matching_llt.append(ent.text)

                    if matching_words_for_resolving and any(word in resolving_matching_llt for word in matching_words_for_resolving):
                        outcome_of_the_events = outcome_of_the_events_keywords[3]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_resolving)

                    sequelae_words = [word.lower() for line in sequelae_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_sequelae = [word for word in sequelae_words if
                                                   word not in common_words and word in line_up_to_next_disease.lower()]
                    sequelae_matching_llt = []
                    doc_sequelae = nlp_1(''.join(matching_words_for_sequelae))
                    for ent in doc_sequelae.ents:
                        if ent.label_ == "DISEASE":
                            sequelae_matching_llt.append(ent.text)
                    if matching_words_for_sequelae and any(word in sequelae_matching_llt for word in matching_words_for_sequelae):
                        outcome_of_the_events = outcome_of_the_events_keywords[4]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_sequelae)
                    fatal_words = [word.lower() for line in fatal_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_fatal = [word for word in fatal_words if
                                                word not in common_words and word in line_up_to_next_disease.lower()]
                    fatal_matching_llt = []
                    doc_fatal = nlp_1(''.join(matching_words_for_fatal))
                    for ent in doc_fatal.ents:
                        if ent.label_ == "DISEASE":
                            fatal_matching_llt.append(ent.text)
                    if matching_words_for_fatal and any(word in fatal_matching_llt for word in matching_words_for_fatal):
                        outcome_of_the_events = outcome_of_the_events_keywords[5]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_fatal)
                    unchanged_words = [word.lower() for line in unchanged_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_unchanged = [word for word in unchanged_words if
                                                    word not in common_words and word in line_up_to_next_disease.lower()]
                    unchanged_matching_llt = []
                    doc_unchanged = nlp_1(''.join(matching_words_for_unchanged))
                    for ent in doc_unchanged.ents:
                        if ent.label_ == "DISEASE":
                            unchanged_matching_llt.append(ent.text)
                    if matching_words_for_unchanged and any(word in unchanged_matching_llt for word in matching_words_for_unchanged):
                        outcome_of_the_events = outcome_of_the_events_keywords[6]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_unchanged)
                    worsened_words = [word.lower() for line in worsened_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_worsened = [word for word in worsened_words if
                                                   word not in common_words and word in line_up_to_next_disease.lower()]

                    worsened_matching_llt = []
                    doc_worsened = nlp_1(''.join(matching_words_for_worsened))
                    for ent in doc_worsened.ents:
                        if ent.label_ == "DISEASE":
                            worsened_matching_llt.append(ent.text)

                    if matching_words_for_worsened and any(word in worsened_matching_llt for word in matching_words_for_worsened):
                        outcome_of_the_events = outcome_of_the_events_keywords[7]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_worsened)
                if found_keyword_second is not True and found_keyword is not True:
                    print("found_keyword and second from last loop", found_keyword, found_keyword_second)
                    outcome_of_the_events = outcome_of_the_events_keywords[0]

                comments = line_up_to_next_disease
                reaction_information = {
                    "is_this_the_main_event": "",
                    "reaction_reported_by_primary_source_in_native_language": llt,
                    "term_highlight_by_reporter": term_highlighted_by_reporter,
                    "reporters_language": "",
                    "outcome_of_the_event": outcome_of_the_events,
                    "translated_version_of_the_event": "",
                    "country_where_the_ae_accured": country,
                    "seriousness_criteria": {
                        "results_in_death": results_in_death,
                        "life_threating": life_threatening,
                        "caused_prolonged_hospitalisation": hospitalized,
                        "disabling_incapacitating": disabled,
                        "congenital_anomaly_birth_defect": congenital,
                        "other_medically_important_condition": other_medically_important_condition
                    },
                    "meddra_term_code": {
                        "llt": "",
                        "pt": "",
                        "hlt": "",
                        "hlgt": "",
                        "soc": ""
                    },
                    "start_date": "",
                    "end_date": "",
                    "reaction_duration": "",
                    "reaction_duration_unit": "",
                    "medical_confirmation_by_hcp": "",
                    "comments": ""
                }

                all_reaction_information.append(reaction_information)
                print(f"reaction for every event {i} . {llt}", reaction_information)
                print("About Event", llt)
                print("comments for each event:", comments)
                print("duration:", duration)
                print('duration unit:', time_unit)
                #print(f"Line up to next disease: {line_up_to_next_disease}")
                    # Add any additional logic or actions for serious events
                print("term_highlighted_by_reporter:", term_highlighted_by_reporter)

                print("results in death:", results_in_death)
                print("life threat:", life_threatening)
                print("hospitalized:", hospitalized)
                print("disabled:", disabled)
                print("congenital:", congenital)
                print("outcome_of_events", outcome_of_the_events)
                print("other medically important condition", other_medically_important_condition)
                print("reaction_information_section", reaction_information)
                print("######################")

            else:
                # If there's no next disease in the list, take the text up to the end of the document
                line_up_to_next_disease = text_after_medicine[llt_start_index:]
                hospitalized_keywords = ['admitted', 'admission', 'hospitalized', 'checked']
                abnormality_keywords = ['abnormality', 'birth defects', 'birth-defects','anomaly']

                dead_keywords = ["expired", "died", "dead", "passed away", "demise", "murdered", "lost life"]
                death_comments = ""
                text = ""
                death_text = ""
                dod = ""
                lines = line_up_to_next_disease.split("/n")

                print("lines are", lines)

                pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, dead_keywords)) + r')\b', flags=re.IGNORECASE)

                # Search for the keywords in the text
                matches = pattern.findall(line_up_to_next_disease)

                # Output the matches
                if matches:
                    results_in_death = 'Yes'

                else:
                    results_in_death = 'No'
                # for i, line in enumerate(lines):
                #     for keyword in dead_keywords:
                #         if keyword in line:
                #             results_in_death = 'Yes'
                #             break
                #         else:
                #             results_in_death = 'No'
                dead_keywords = ["expired", "died", "dead", "passed away", "demised", "murdered", "lost life"]

                pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, dead_keywords)) + r')\b', flags=re.IGNORECASE)

                # Search for the keywords in the text
                matches = pattern.findall(line_up_to_next_disease)

                # Output the matches
                if matches:
                    for match in matches:
                        print(f"Found match: {match}")
                else:
                    print("************not matched*********")
                # if 'died' in text_after_medicine or 'dead' in text_after_medicine:
                #     results_in_death = 'Yes'
                # else:
                #     results_in_death = 'No'
                if 'life threat' in line_up_to_next_disease or 'mortal' in line_up_to_next_disease:
                    life_threatening = 'Yes'
                else:
                    life_threatening = 'No'
                for hospi in hospitalized_keywords:
                    if hospi in text_before_medicine:
                        hospitalized = 'Yes'
                        break
                    elif hospi in text_after_medicine:
                        hospi_start_index = text_after_medicine.find(hospi)
                        hospitalized_lines = text_after_medicine[hospi_start_index:]
                        if llt in hospitalized_lines:
                            hospitalized = 'Yes'
                            break
                    else:
                        hospitalized = 'No'
                if 'disabled' in line_up_to_next_disease or 'chronic' in line_up_to_next_disease:
                    disabled = 'Yes'
                else:
                    disabled = 'No'
                for congi in abnormality_keywords:
                    if congi in text_before_medicine:
                        congenital = 'Yes'
                        break
                    else:
                        congenital = 'No'

                #
                duration = ""
                time_unit = ""
                time_units = ["year", "years", "days", "day", "decades", "decade", "months", "month", "hours", "hour", "week",
                              "weeks", "second", "seconds"]

                # Regular expression pattern to match age information with hyphen and different time units
                pattern = r'(\d+)\s*-?\s*(' + '|'.join(time_units) + ')'
                duration_pattern = re.compile(pattern)
                matches = duration_pattern.findall(line_up_to_next_disease)
                if matches:
                    ages, time_unit_ = int(matches[0][0]), matches[0][1]
                    match_index = line_up_to_next_disease.find(matches[0][1], first_three_lines.find(matches[0][0]))
                    if match_index != -1 and line_up_to_next_disease.find("old", match_index) != -1:
                        duration = ages
                        time_unit = time_unit_


                comments = line_up_to_next_disease
                other_medically_important_condition = ""

                for event in event_terms['event_terms']:
                    if event in llt:
                        other_medically_important_condition = 'Yes'
                        print(event)
                        break
                    else:
                        other_medically_important_condition = 'No'

                if results_in_death == "Yes" or life_threatening == "Yes" or hospitalized == "Yes" or disabled == "Yes" or congenital == "Yes" or other_medically_important_condition == 'Yes':
                    term_highlighted_by_reporter = term_highlighted_by_reporter_keywords[2]
                else:
                    term_highlighted_by_reporter = term_highlighted_by_reporter_keywords[0]
                # resolving outcome of events
                found_keyword = False
                lines = line_up_to_next_disease.split('.')

                # Iterate through lines and check for keywords
                for line in lines:
                    if check_keywords(line, resolved_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[1]
                        found_keyword = True
                        print("found_keyword from first loop", found_keyword)
                        outcome_llt.add(llt)
                        print("present in resolved", llt)
                        print(f"Resolved: {line}")
                        break
                    elif check_keywords(line, not_resolved_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[2]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in not resolved", llt)
                        print(f"NOT Resolved: {line}")
                        break
                    elif check_keywords(line, resolving_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[3]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in resolving", llt)
                        print(f"Resolving: {line}")
                        break
                    elif check_keywords(line, sequelae_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[4]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in sequele", llt)
                        print(f"Sequelae: {line}")
                        break
                    elif check_keywords(line, fatal_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[5]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in fatal", llt)
                        print(f"Fatal: {line}")
                        break
                    elif check_keywords(line, unchanged_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[6]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in unchanged", llt)
                        print(f"Unchanged: {line}")
                        break
                    elif check_keywords(line, worsened_keywords):
                        outcome_of_the_events = outcome_of_the_events_keywords[7]
                        found_keyword = True
                        outcome_llt.add(llt)
                        print("present in worsened", llt)
                        print(f"Worsened: {line}")
                        break
                found_keyword_second = False

                if found_keyword is not True:
                    resolved_words = [word.lower() for line in resolved_lines for word in line.split()]
                    print("resolved words are", resolved_words)

                    words_in_line = [word for word in line_up_to_next_disease.lower().split() if is_common_word(word)]
                    print("About remaining llt", llt)
                    print("line_up_to_next_disease", line_up_to_next_disease)

                    common_words = {'the', 'in', 'a', 'and', 'to', 'of', 'for', 'with', 'on', 'at', 'by', 'from', 'as',
                                    'all'}  # Add other common words as needed

                    matching_words = [word for word in resolved_words if
                                      word not in common_words and word in line_up_to_next_disease.lower().split()]
                    resolved_matching_llt = []
                    doc_resolved = nlp_1(''.join(matching_words))
                    for ent in doc_resolved.ents:
                        if ent.label_ == "DISEASE":
                            resolved_matching_llt.append(ent.text)
                    if matching_words and any(word in resolved_matching_llt for word in matching_words):
                        outcome_of_the_events = outcome_of_the_events_keywords[1]
                        found_keyword_second = True
                        print("found_keyword from secon", found_keyword)
                        print("This event has matched from previous:", llt)
                        print("Matching Words:", matching_words)

                    not_resolved_words = [word.lower() for line in not_resolved_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_not_resolved = [word for word in not_resolved_words if
                                                       word not in common_words and word in line_up_to_next_disease.lower()]
                    not_resolved_matching_llt = []
                    doc_not_resolved = nlp_1(''.join(matching_words_for_not_resolved))
                    for ent in doc_not_resolved.ents:
                        if ent.label_ == "DISEASE":
                            not_resolved_matching_llt.append(ent.text)

                    if matching_words_for_not_resolved and any(
                            word in not_resolved_matching_llt for word in matching_words_for_not_resolved):
                        outcome_of_the_events = outcome_of_the_events_keywords[2]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_not_resolved)

                    resolving_words = [word.lower() for line in resolving_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_resolving = [word for word in resolving_words if
                                                    word not in common_words and word in line_up_to_next_disease.lower()]
                    resolving_matching_llt = []
                    doc_resolving = nlp_1(''.join(matching_words_for_resolving))
                    for ent in doc_resolving.ents:
                        if ent.label_ == "DISEASE":
                            resolving_matching_llt.append(ent.text)

                    if matching_words_for_resolving and any(
                            word in resolving_matching_llt for word in matching_words_for_resolving):
                        outcome_of_the_events = outcome_of_the_events_keywords[3]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_resolving)

                    sequelae_words = [word.lower() for line in sequelae_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_sequelae = [word for word in sequelae_words if
                                                   word not in common_words and word in line_up_to_next_disease.lower()]
                    sequelae_matching_llt = []
                    doc_sequelae = nlp_1(''.join(matching_words_for_sequelae))
                    for ent in doc_sequelae.ents:
                        if ent.label_ == "DISEASE":
                            sequelae_matching_llt.append(ent.text)
                    if matching_words_for_sequelae and any(
                            word in sequelae_matching_llt for word in matching_words_for_sequelae):
                        outcome_of_the_events = outcome_of_the_events_keywords[4]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_sequelae)
                    fatal_words = [word.lower() for line in fatal_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_fatal = [word for word in fatal_words if
                                                word not in common_words and word in line_up_to_next_disease.lower()]
                    fatal_matching_llt = []
                    doc_fatal = nlp_1(''.join(matching_words_for_fatal))
                    for ent in doc_fatal.ents:
                        if ent.label_ == "DISEASE":
                            fatal_matching_llt.append(ent.text)
                    if matching_words_for_fatal and any(word in fatal_matching_llt for word in matching_words_for_fatal):
                        outcome_of_the_events = outcome_of_the_events_keywords[5]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_fatal)
                    unchanged_words = [word.lower() for line in unchanged_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_unchanged = [word for word in unchanged_words if
                                                    word not in common_words and word in line_up_to_next_disease.lower()]
                    unchanged_matching_llt = []
                    doc_unchanged = nlp_1(''.join(matching_words_for_unchanged))
                    for ent in doc_unchanged.ents:
                        if ent.label_ == "DISEASE":
                            unchanged_matching_llt.append(ent.text)
                    if matching_words_for_unchanged and any(
                            word in unchanged_matching_llt for word in matching_words_for_unchanged):
                        outcome_of_the_events = outcome_of_the_events_keywords[6]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_unchanged)
                    worsened_words = [word.lower() for line in worsened_lines for word in line.split()]

                    # Check each word against line_up_to_next_disease and extract matching words
                    matching_words_for_worsened = [word for word in worsened_words if
                                                   word not in common_words and word in line_up_to_next_disease.lower()]

                    worsened_matching_llt = []
                    doc_worsened = nlp_1(''.join(matching_words_for_worsened))
                    for ent in doc_worsened.ents:
                        if ent.label_ == "DISEASE":
                            worsened_matching_llt.append(ent.text)

                    if matching_words_for_worsened and any(
                            word in worsened_matching_llt for word in matching_words_for_worsened):
                        outcome_of_the_events = outcome_of_the_events_keywords[7]
                        found_keyword_second = True
                        print(f"This event has matched from previous ({outcome_of_the_events}):", llt)
                        print("Matching Words:", matching_words_for_worsened)

                if found_keyword_second is not True and found_keyword is not True:
                    print("Found keyword and second keyword", found_keyword, found_keyword_second)
                    outcome_of_the_events = outcome_of_the_events_keywords[0]
                reaction_information = {
                    "is_this_the_main_event": "",
                    "reaction_reported_by_primary_source_in_native_language": llt,
                    "term_highlight_by_reporter": term_highlighted_by_reporter,
                    "reporters_language": "",
                    "outcome_of_the_event": outcome_of_the_events,
                    "translated_version_of_the_event": "",
                    "country_where_the_ae_accured": country,
                    "seriousness_criteria": {
                        "results_in_death": results_in_death,
                        "life_threating": life_threatening,
                        "caused_prolonged_hospitalisation": hospitalized,
                        "disabling_incapacitating": disabled,
                        "congenital_anomaly_birth_defect": congenital,
                        "other_medically_important_condition": other_medically_important_condition
                    },
                    "meddra_term_code": {
                        "llt": "",
                        "pt": "",
                        "hlt": "",
                        "hlgt": "",
                        "soc": ""
                    },
                    "start_date": "",
                    "end_date": "",
                    "reaction_duration": "",
                    "reaction_duration_unit": "",
                    "medical_confirmation_by_hcp": "",
                    "comments": ""
                }

                all_reaction_information.append(reaction_information)
                print(f"Reaction for  event {i} . {llt}:", reaction_information)
                print("About event from else", llt)
                # print(f"Line up to end of document: {line_up_to_next_disease}")
                print("term_highlighted_by_reporter:", term_highlighted_by_reporter)
                print("duration:", duration)
                print('duration unit:', time_unit)
                print("results in death:", results_in_death)
                print("life threat:", life_threatening)
                print("hospitalized:", hospitalized)
                print("disabled:", disabled)
                print("congenital:", congenital)
                print(f"outcome_of_the_events for ({llt})", outcome_of_the_events)
                print("other medically important condition", other_medically_important_condition)
                print("comments:", comments)
                print("####################")
                print("recation_information_section", reaction_information)
        #print("llt for outcome", outcome_llt)

        # again searching about outcome from symptoms or words that are not recognizable.







        reaction_event = {

            "reaction_information": all_reaction_information,

            "event_information": {

              "diagnosis": "",

              "onset_date_time": "",

              "onset_latency": "",

              "intencity": "",

              "onset_form_last_dose": "",

              "reciept_date": "",

              "stop_date_time": "",

              "patient_has_priroity": "",

              "frequency": "",

              "duration": "",

              "treatment_recieved": "",

              "lack_of_efficancy": "",

              "progression_of_diesease": "",

              "adverse_drug_withdrawal_reaction": "",

              "infection": "",

              "emergency_room_visit": "",

              "physician_office_visit": ""

            },

            "event_assessment": {

              "product": "",

              "causality_as_reported_source": "",

              "causality_as_reported_method": "",

              "causality_as_reported_result": "",

              "causality_as_determined_source": "",

              "causality_as_determined_method": "",

              "causality_as_determined_result": "",

              "other_causality_source": "",

              "other_causality_method": "",

              "other_causality_result": "",

              "event_pt_description_llt": "",

              "d_s": "",

              "seriousness_severity_duration": "",

              "data_sheet": "",

              "as_determined_listedness": ""

            }

        }

        print("5th tab output is", json.dumps(reaction_event))
        return reaction_event
    except Exception as e:
        print('Error! Code: {c}, Message, {m}'.format(c=type(e).__name__, m=str(e)))
