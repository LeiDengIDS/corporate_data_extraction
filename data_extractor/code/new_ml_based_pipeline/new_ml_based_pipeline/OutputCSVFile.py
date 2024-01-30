# ============================================================================================================================
# PDF_Extractor
# File   : OutputCSVFile.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

'''Super Class OutPutFile supports to save the extracted KPI value
with some other data such as pdf name, Page Number, etc. into the CSV file.'''

import os
from abc import abstractmethod
import csv
from pathlib import Path

class OutputCSVFile:
    def __init__(self, csv_file_path, nlp_method):
        self.csv_file_path = csv_file_path
        self.nlp_method = nlp_method

    @abstractmethod
    def select_data_to_csv(self):
        ''' Two extractors return different data, and from the returned data, 
        choose the same data type to store in a CSV. '''
        pass

    def save_to_csv_file(self, selected_data):
        ''' Save extracted KPI data to a CSV file.'''
        if selected_data:
            file_exist = os.path.isfile(self.csv_file_path)

            with open(self.csv_file_path, mode='a', newline='') as f:
                fieldnames = ["PDF Name", "Question", "KPI value", "Paragraph", "Page number", "Coordinate", "Method", "Score"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                # write the header of the CSV file
                if not file_exist or f.tell() == 0:
                    writer.writeheader()

                if self.nlp_method == 'Haystack':
                    selected_method = 'Haystack'
                elif self.nlp_method == 'DQA':
                    selected_method = 'DQA'
                elif self.nlp_method == 'Both':
                    selected_method = 'Haystack,DQA'

                # write values to the CSV file
                writer.writerow({
                    # Use get() to handle missing keys
                    "PDF Name": selected_data.get("source", ""),
                    "Question": selected_data.get("query", ""),
                    "KPI value": selected_data.get("answer", ""),
                    "Paragraph": selected_data.get("content", ""),
                    "Page number": selected_data.get("page number", ""),
                    "Coordinate": selected_data.get("coordinate", ""),
                    "Method": selected_method,
                    "Score": selected_data.get("score", "")
                })
                print("KPI is saved!")
                print("---------------------------")
        else:
            print("There is no data to save.")
            print("---------------------------")

''' Subclass of OutputCSVFile - overwrite abstract method.'''
class HaystackOutput(OutputCSVFile):
    def __init__(self, result, csv_file_path, nlp_method):
        super().__init__(csv_file_path, nlp_method)
        self.result = result
    
    def select_data_to_csv(self):
        ''' Select data from extracted data by extractor haystack; 
        only save data with a score higher than 0.5 to the CSV file.'''
        score = self.result['answers'][0].to_dict()['score']
        if score > 0.5:
            selected_data = {
                "source": self.result['answers'][0].to_dict()['meta']['source'],
                "query": self.result['query'],
                "answer": self.result['answers'][0].to_dict()['answer'],
                "content": self.result['answers'][0].to_dict()['context'],
                "page number": self.result['answers'][0].to_dict()['meta']['page number'],
                "coordinate": self.result['answers'][0].to_dict()['meta']['coordinate'],
                "method": ('Haystack', 'DQA'),
                "score": score
            }
            print("--------")
            print("Save this KPI to CSV file:", selected_data)
        else:
            selected_data = {}
            print("--------")
            print("An appropriate answer was not found: ", selected_data)
        return selected_data

''' Another subclass of OutputCSVFile - overwrite abstract method.'''
class DQAOutput(OutputCSVFile):
    def __init__(self, csv_file_path, query, result, class_dqa, nlp_method, image_paths):
        super().__init__(csv_file_path, nlp_method)
        self.result = result
        self.query = query
        self.class_dqa = class_dqa
        self.image_paths = image_paths

    def select_data_to_csv(self):
        ''' Select data from extracted data by extractor DQA.'''
        answer_para = self.class_dqa.find_answer_para_in_image(self.image_paths, self.result)
        x0, y0 = self.class_dqa.get_para_coordinates(answer_para)
        if answer_para is not None:
            selected_data = {
                "source": Path(self.class_dqa.pdf_path).name,
                "query": self.query,
                "answer": self.result[1][0]['answer'],
                "content": answer_para,
                "page number": self.result[0],
                "coordinate": [x0, y0],
                "method": ('Haystack', 'DQA'),
                "score": self.result[1][0]['score']
            }
            print("--------")
            print("Save this KPI to CSV file:", selected_data)
        else:
            selected_data = {}
            print("--------")
            print("No paragraph containing the answer was found: ", selected_data)
        return selected_data



