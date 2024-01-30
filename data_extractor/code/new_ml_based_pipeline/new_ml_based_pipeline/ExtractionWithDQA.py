# ============================================================================================================================
# PDF_Extractor
# File   : ExtractionWithDQA.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

''' An extractor using the Hugging Face NLP model - Document question answering (DQA).
PDF pages are saved as images, extractor exports answer(KPI) for a question from each image.'''

import re
from fuzzywuzzy import fuzz
from pdf2image import convert_from_path
from transformers import pipeline
import json
from PIL import Image
import pytesseract
import concurrent.futures

class ExtractionWithDQA:
    def __init__(self, pdf_path, output_directory, csv_file_path, json_save_path, dqa_model):
        self.pdf_path = pdf_path
        self.output_directory = output_directory
        self.csv_file_path = csv_file_path
        self.json_save_path = json_save_path
        self.dqa_model = dqa_model

    def pdf_to_image(self, image_format='png'):
        ''' Convert PDF pages into images and save each image.'''
        print("Save PDF pages into images:")
        images = convert_from_path(self.pdf_path)
        image_paths = []

        for index, image in enumerate(images):
            image_path = f"{self.output_directory}/page_{index + 1}.{image_format}"
            image.save(image_path, image_format)
            image_nr = index + 1
            image_paths.append((image_nr,image_path))
        return images, image_paths

    def extract_kpi_with_dqa_model(self, query, page_list, images):
        ''' Extract the KPI value for a question from each image, choose 
        the optimal KPI value as the answer to a question.'''

        # Check if year_contain is a boolean
        year_contain = re.search(r'\b\d{4}\b', query)
        year_contain = year_contain is not None

        print("Initializing Pipeline: ") # devoce =0 indicates use_gpu
        pipe = pipeline("document-question-answering", model=self.dqa_model, device=0)

        print("Iterate and feed image into pipeline: ")
        max_result = None
        max_score = 0.5
        score_threshold = 0.99
        for index, image in enumerate(images):
            page_nr = index + 1
            # If it's year sensitive question and page number are not in page_list, continue.
            if year_contain:
                if page_list is not None and hasattr(page_list, '__iter__'):
                    if page_nr not in page_list:
                        continue
                else:
                    # Handle the case where page_list is not iterable or is None
                    print(" ")

            pipe_result = pipe(image=image, question=query)
            result = (page_nr, pipe_result)
            if len(result[1]) > 0:
                score = result[1][0]['score']
                if max_score is None or score > max_score:
                    max_score = score
                    max_result = result
                    print("current max_result: ", max_result)
            else:
                print(" ")

            # If the max score reaches the threshold, stop the iteration.
            if max_score >= score_threshold:
                break

        print("Final Answer:", max_result)
        print("--------")
        return max_result

    @staticmethod
    def find_answer_para_in_image(image_paths, max_result):
        '''The DQA model doesn't return the Paragraph containing answers, 
        so we get it from the JSON file.'''
        print("Getting Paragraph from the JSON file: ")
        if max_result is not None:
            answer = max_result[1][0]['answer']
            page_number = max_result[0]
            image_path = None

            # Find the image that contains the answer
            for image_nr, image_ph in image_paths:
                if image_nr == page_number:
                    image_path = image_ph
                    break

            image = Image.open(image_path)
            # Text recognition using Tesseract
            text = pytesseract.image_to_string(image)
            paragraphs = text.split('\n\n')

            # Find the paragraph that contains the answer
            for i, paragraph in enumerate(paragraphs):
                if answer in paragraph:
                    answer_paragraph = paragraph
                    print("answer paragraph: ", answer_paragraph)
                    return answer_paragraph
            # No paragraph contains this answer
            return None
        else:
            print("No answer is found.")
            return None

    def get_para_coordinates(self, answer_paragraph):
        '''The DQA model doesn't return the coordinates, so we get it from the JSON file.'''
        print("Getting Coordinates from the JSON file: ")
        # Set paragraph similarity threshold
        threshold = 60
        if answer_paragraph is not None:
            with open(self.json_save_path, 'r') as f:
                datas = json.load(f)

            for i in datas:
                # Perform fuzzy string matching
                similarity = fuzz.token_set_ratio(i["paragraph"][0], answer_paragraph)
                if similarity >= threshold:
                    x0 = i["coordinates"]["x0"]
                    y0 = i["coordinates"]["y0"]
                    print("para coordinates: ", [x0, y0])
                    return x0, y0
                else:
                    return 0, 0
        else:
            return 0, 0

  








