# ============================================================================================================================
# PDF_Extractor
# File   : InputQuestions.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

'''Process input questions and feed them into the extractor.'''

import re
import csv
import json
from OutputCSVFile import HaystackOutput, DQAOutput

class InputQuestions:
    def __init__(self, questions, class_haystack, class_dqa, nlp_method):
        self.questions = questions
        self.class_haystack = class_haystack
        self.class_dqa = class_dqa
        self.nlp_method = nlp_method

    def extract_year(self):
        ''' Extract years from PDFs. This will be used for year sensitive questions.'''
        pattern = r'\b\d{4}\b'
        regex = re.compile(pattern)
        unique_years = []
        year_page_mapping = {}

        with open(self.class_haystack.json_save_path, "r") as file:
            paras = json.load(file)

        # Iterate paragraph and extract years
        for item in paras:
            paragraph = item["paragraph"][0]
            page_nr = item["page"][0]
            has_year = bool(regex.search(paragraph))

            if has_year:
                para_years = re.findall(pattern, paragraph)
                unique_years.extend(para_years)

                for year in para_years:
                    if year not in year_page_mapping:
                        year_page_mapping[year] = {page_nr}
                    else:
                        year_page_mapping[year].add(page_nr)

        # Remove duplicates by converting to a set and back to a list
        unique_years = list(set(unique_years))
        # Change dictionary to tuple list.
        year_pages = [(year, list(pages)) for year, pages in year_page_mapping.items()]

        print("Unique year in all paragraphs: ", unique_years)
        print("Year pages pair: ",  year_pages)
        return unique_years,  year_pages

    def switch_nlp_method(self, question, page_list, extractor, document_store, images,image_paths):
        ''' Feed question into extractor, extract KPI value and save it into CSV file.'''
        if extractor == self.class_haystack:
            print("Feed question into Haystack model:")
            result = extractor.extract_kpi(document_store, question)
            haystackop = HaystackOutput(result,extractor.csv_file_path,self.nlp_method)
            haystackop.save_to_csv_file(haystackop.select_data_to_csv())

        elif extractor == self.class_dqa:
            print("Feed question into DQA model:")
            result = extractor.extract_kpi_with_dqa_model(question, page_list, images)
            dqaop = DQAOutput(extractor.csv_file_path,question,result,extractor,self.nlp_method,image_paths)
            dqaop.save_to_csv_file(dqaop.select_data_to_csv())

    def iterative_questions(self, unique_years, year_pages):
        ''' Iterate questions, add years to year sensitive questions.'''
        global target_column_index
        document_store,images,image_paths = None,None,None

        # Doing this before iterating questions, avoid duplicate execution.
        if self.nlp_method == 'Haystack' or self.nlp_method == 'Both':
            document_store = self.class_haystack.create_elastics_docuStore()
        if self.nlp_method == 'DQA' or self.nlp_method == 'Both':
            images, image_paths = self.class_dqa.pdf_to_image(image_format='png')

        print("Iterate questions:")
        with open(self.questions, newline='') as f:
            reader = csv.reader(f)

            # Find the column containing all questions
            header_row = next(reader)
            target_text = 'question'
            for i, header in enumerate(header_row):
                if target_text in header.lower():
                    target_column_index = i
                    break

            # Start to iterate questions.
            for row in reader:
                if target_column_index < len(row):
                    question = row[target_column_index]
                    if question != "question":
                        page_list = None
                        # Year sensitive questions: replace '%YEAR' with years, then feed question into extractor.
                        if '%YEAR' in question:
                            if self.nlp_method == 'Haystack' or self.nlp_method == 'Both':
                                if unique_years is not None:
                                    for year in unique_years:
                                        questionyr = question.replace('%YEAR', year)
                                        print("Question: ", questionyr)
                                        self.switch_nlp_method(questionyr,  page_list, self.class_haystack, document_store, images,image_paths)
                            if self.nlp_method == 'DQA' or self.nlp_method == 'Both':
                                if year_pages is not None:
                                    for year, page_list in year_pages:
                                        questionyr = question.replace('%YEAR', year)
                                        print("Question: ", questionyr)
                                        print(year,"page list: ", page_list)
                                        self.switch_nlp_method(questionyr, page_list, self.class_dqa, document_store,images,image_paths)
                        # Year non sensitive questions: direct feed question into extractor
                        else:
                            print("Question: ", question)
                            if self.nlp_method == 'Haystack' or self.nlp_method == 'Both':
                                self.switch_nlp_method(question, page_list, self.class_haystack, document_store, images,image_paths)
                            if self.nlp_method == 'DQA' or self.nlp_method == 'Both':
                                self.switch_nlp_method(question, page_list, self.class_dqa, document_store, images,image_paths)
            print("Question iteration is done.")





              






