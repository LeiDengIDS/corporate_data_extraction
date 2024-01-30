# ============================================================================================================================
# PDF_Extractor
# File: main.py
# Author: Lei Deng
# Date: 27.07.2023
# ============================================================================================================================

''' This KPI automated Extraction Tool provides 2 NLP methods- Haystack and DQA, eath method default models are set.
It also supports users to choose a suitable NLP model.'''

import argparse
import os.path
from ExtractionWithHaystack import ExtractionWithHaystack
from ExtractionWithDQA import ExtractionWithDQA
from InputQuestions import *
from InputPDFAnalysis import *

def get_pdf_files(folder_path):
    ''' Adding all the PDFs in the provided folder to a list.''' 
    pdf_files = []
    for fn in os.listdir(folder_path):
        if fn.lower().endswith('.pdf'):
            pdf_files.append(fn)
    return pdf_files

def clear_csv(file_path):
    ''' Cleaning CSV file before saving data to it.'''
    with open(file_path, 'w', newline='') as csvfile:
        csvfile.truncate(0)
    
def main():
    ''' Handling input PDFs and questions, extract KPI data and save it to CSV file.'''
    
    # 1. Parsing input data
    # create a parser
    parser = argparse.ArgumentParser('KPI extraction tool based on NLP models.')

    # Add parameters to created parser
    parser.add_argument('--pdf_folder', type=str, default=None, help='Please give the Path of the Folder where PDFs are stored.', required=True)
    parser.add_argument('--questions', type=str, help = 'Please give the Path of the file where the question is stored.', required=True)
    parser.add_argument('--nlp_method', type=str, choices=['Both', 'Haystack', 'DQA'], help="Please choose extractor 'Haystack' or 'DQA'.", required=True)
    parser.add_argument('--output_folder', type=str, default=None, help='Please give a path of a Folder where the extracted data will be stored.',required=True)

    args, remaining = parser.parse_known_args()
    nlp_method = args.nlp_method

    #Set NLP models
    nlp_model_rt,nlp_model_re,nlp_model_dqa = None,None,None
    if nlp_method == 'Haystack' or nlp_method == 'Both':
        parser.add_argument('--nlp_model_rt', type=str, default='sentence-transformers/multi-qa-mpnet-base-dot-v1',
                            help='Please give a semantic search NLP model, otherwise, default model will be used.')
        parser.add_argument('--nlp_model_re', type=str, default='deepset/roberta-base-squad2',
                            help='Please give a question answering NLP Model, otherwise, default model will be used.')
    if nlp_method == 'DQA' or nlp_method == 'Both':
        parser.add_argument('--nlp_model_dqa', type=str, default='impira/layoutlm-document-qa',
                            help='Please give a document question answering, otherwise, default model will be used.')

    # parse parameter
    args = parser.parse_args()
    pdf_folder = args.pdf_folder
    questions = args.questions
    nlp_method = args.nlp_method
    output_folder = args.output_folder
    
    if nlp_method == 'Haystack' or nlp_method == 'Both':
        nlp_model_rt = args.nlp_model_rt
        nlp_model_re = args.nlp_model_re
    if nlp_method == 'DQA' or nlp_method == 'Both':
        nlp_model_dqa = args.nlp_model_dqa

    # Hints for user
    if pdf_folder is None:
        pdf_folder = input("What is the folder where PDFs are stored?")
    if pdf_folder is None or pdf_folder == "":
        print("You have to give a folder path where PDFs are stored.")
        return

    if questions is None:
        questions  = input("Please give the path of the file where questions are stored.")
    if questions is None or questions == "":
        print("Question can not be empty.")
        return

    if nlp_method is None:
        nlp_method = input("Which NLP method do you wanna use?")
    if nlp_method is None or nlp_method == "":
        print("You have to choose one of these NLP Methods: 'Haystack', 'DQA'.")
        return

    if output_folder is None:
        output_folder = input("Where do you wanna store your extracted KPI datas?")
    if output_folder is None or output_folder == "":
        print("A folder path must be given that will be used to save extracted data.")
        return

     # 2. Creating a saving path and file 
    csv_file_path_hs,csv_file_path_dqa = None,None

    # Create a path for output files:
    if nlp_method == 'Haystack' or nlp_method == 'Both':
        csv_file_path_hs = os.path.join(output_folder, "output_kpi_hs.csv")
        print("csv file path:", csv_file_path_hs)
    if nlp_method == 'DQA' or nlp_method == 'Both':
        csv_file_path_dqa = os.path.join(output_folder, "output_kpi_dqa.csv")
        print("csv file path:", csv_file_path_dqa)
    
    # create a directory to save pictures
    pdfimage_output = os.path.join(output_folder, "output_image")
    if not os.path.exists(pdfimage_output):
        os.makedirs(pdfimage_output, exist_ok=True)

    # 3. Clean saving file
    if nlp_method == 'Haystack' or nlp_method == 'Both':
        clear_csv(csv_file_path_hs)
    if nlp_method == 'DQA' or nlp_method == 'Both':
        clear_csv(csv_file_path_dqa)

    # 4. Extract KPI from PDFs based on questions
    pdfs = get_pdf_files(pdf_folder)
    for pdf in pdfs:
        # 4.1 Read the PDF and save content to a structured JSON file
        pdf_path = os.path.join(pdf_folder, pdf)
        pdf_name = os.path.splitext(pdf)[0]
        json_save_path = os.path.join(output_folder, f"{pdf_name}.json")
        pdfanalysis = InputPDFAnalysis(pdf_path, json_save_path)
        print("Saving PDF: ", pdf, "to JSON file:", json_save_path)
        pdfanalysis.save_para_to_json()
        
        # 4.2 Create 2 extractors 
        hsextractor = ExtractionWithHaystack(pdf_path, json_save_path,  csv_file_path_hs, nlp_model_rt, nlp_model_re)
        dqaextractor = ExtractionWithDQA(pdf_path, pdfimage_output, csv_file_path_dqa, json_save_path, nlp_model_dqa)
        
        # 4.3 Extract KPIs based on questions and save KPIs into a CSV file
        questions = InputQuestions(questions, hsextractor, dqaextractor, nlp_method)
        unique_years, year_pages = questions.extract_year()
        questions.iterative_questions(unique_years, year_pages)
    print("All PDFs have been processed! Extraction is done!")


if __name__ == '__main__':
    main()


