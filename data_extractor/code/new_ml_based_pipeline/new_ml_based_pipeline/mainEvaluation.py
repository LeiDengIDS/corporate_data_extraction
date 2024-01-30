# ============================================================================================================================
# PDF_Extractor
# File   : mainEvaluation.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================
''' Main class for evaluation. Evaluate the performance of the Extractor by
comparing the extracted KPI data with the actual KPI data of PDFs.'''

import csv
from CompareKPIValue import *
import argparse
import matplotlib.pyplot as plt

def get_csv_data(csv_file_path):
    ''' Read extracted and actual KPI data from the CSV file.'''
    print("Get extracted and actual KPI data from CSV files: ")
    with open(csv_file_path, newline='') as csvf:
        reader = csv.reader(csvf)
        header_of_csv = next(reader)

        column_index_PDFn = header_of_csv.index("PDF Name")
        column_index_question = header_of_csv.index("Question")
        column_index_KPI = header_of_csv.index("KPI value")

        data = []
        for row in reader:
            pdf_name = row[column_index_PDFn]
            question = row[column_index_question]
            kpi_value = row[column_index_KPI]
            data_tuple = (pdf_name,question,kpi_value)
            data.append(data_tuple)
        # print("Data:", data)
        return data

def calculate_f1_score(compareKPIvalueobj):
    """ Compare extracted KPI and actual KPI of PDFs by calculating the F1_score."""
    print("Compare extracted KPI data vs. actual data:")
    compare_result = compareKPIvalueobj.compare_extracted_annotated_kpi()
    count_match_equal, count_match_unequal, count_extracted_only, count_annotated_only = compare_result
    tp = count_match_equal
    fp = count_extracted_only + count_match_unequal
    fn = count_annotated_only

    if tp > 0:
        print("Calculate F1 Score:")
        precision = tp/float(tp+fp)
        recall = tp/float(tp+fn)
        f1_score = 2*(precision*recall)/(precision+recall)
        print("F1 Score: ", f1_score)
        return f1_score
    else:
        # Deal with the case, tp is 0.
        return 0

def eval(extD_haystack, extD_dqa, anno_datas):
    ''' Perform evaluation.'''
    compareKPIValue_haystack = CompareKPIValue(extD_haystack, anno_datas)
    compareKPIValue_dqa = CompareKPIValue(extD_dqa, anno_datas)

    # Perform f1 score calculation 
    print("Compare Haystack data & actual data:")
    print("---------------------")
    f1_score_haystack = calculate_f1_score(compareKPIValue_haystack)
    print("Compare DQA data & actual data:")
    print("---------------------")
    f1_score_dqa = calculate_f1_score(compareKPIValue_dqa)
    return f1_score_haystack, f1_score_dqa

def visualize_f1_score(f1_score_haystack, f1_score_dqa):
    ''' Visualize the F1 scores.'''
    method_names = ['Haystack', 'DQA']
    plt.bar(method_names, [f1_score_haystack, f1_score_dqa], color=['blue', 'green'])
    plt.title('F1 Scores: Haystack and DQA')
    plt.xlabel('Methods')
    plt.ylabel('F1 Score')
    plt.show()

def main():
    ''' Processing the input arguments, perform and visualize the evaluation.'''
    parser = argparse.ArgumentParser('Evaluation for KPI extraction tool')
    parser.add_argument('--extracted_datas_haystack', type=str, default=None, help='File that contains extracted KPI',
                        required=True)
    parser.add_argument('--extracted_datas_dqa', type=str, default=None, help='File that contains extracted KPI',
                        required=True)
    parser.add_argument('--annotated_datas', type=str, default=None, help='File that contains real KPI',
                        required=True)

    # parse parameter
    args = parser.parse_args()
    extracted_datas_haystack = args.extracted_datas_haystack
    extracted_datas_dqa = args.extracted_datas_dqa
    annotated_datas = args.annotated_datas

    # Hints for user
    if extracted_datas_haystack is None:
        extracted_datas_haystack = input("Please give the file path of extracted KPI with Haystack.")
    if extracted_datas_haystack is None or extracted_datas_haystack == "":
        print("You have to give the file path of extracted KPIs with Haystack.")
        return

    if extracted_datas_dqa is None:
        extracted_datas_dqa = input("Please give the file path of extracted KPI with dqa.")
    if extracted_datas_dqa is None or extracted_datas_dqa == "":
        print("You have to give the file path of extracted KPIs with dqa.")
        return

    if annotated_datas is None:
        annotated_datas = input("Please give the file path of real datas.")
    if annotated_datas is None or annotated_datas == "":
        print("You have to give the file path of real datas.")
        return

    # Get extracted KPI and actual KPI
    extD_haystack = get_csv_data(extracted_datas_haystack)
    extD_dqa = get_csv_data(extracted_datas_dqa)
    annotated_datas = get_csv_data(annotated_datas)

    # Do the evaluation
    f1_score_haystack, f1_score_dqa = eval(extD_haystack, extD_dqa, annotated_datas)
    # print("f1_score_haystack and f1_score_dqa:", f1_score_haystack,f1_score_dqa)

    # Visualize F1 score chart
    visualize_f1_score(f1_score_haystack, f1_score_dqa)

if __name__ == '__main__':
    main()
