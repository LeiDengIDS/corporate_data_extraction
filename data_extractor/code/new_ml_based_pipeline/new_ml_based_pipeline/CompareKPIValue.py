# ============================================================================================================================
# PDF_Extractor
# File   : CompareKPIValue.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

''' Compare the extracted KPI data with the actual KPI data by comparing the string and number.'''

import re

class CompareKPIValue:
    def __init__(self, extra_datas, anno_datas):
        self.extra_datas = extra_datas
        self.anno_datas = anno_datas

    @staticmethod
    def get_kpi_number(kpi_value):
        ''' Only extract the number in the extracted KPI value.'''
        # match one or more digits
        pattern = r'\d+'
        match = re.search(pattern, kpi_value)
        if match:
            number = int(match.group())
            return number

    @staticmethod
    def levenshtein_distance(extracted_kpi, annotated_kpi):
        ''' Using Levenshtein distance to allow a limited difference between two Strings.'''
        m = len(extracted_kpi)
        n = len(annotated_kpi)
        table = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            table[i][0] = i
        for j in range(n + 1):
            table[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if extracted_kpi[i - 1] == annotated_kpi[j - 1]:
                    table[i][j] = table[i - 1][j - 1]
                else:
                    table[i][j] = 1 + min(table[i - 1][j], table[i][j - 1], table[i - 1][j - 1])
        print(f'levensthein distance of KPI values:', table[-1][-1], "Is this small than 5?")
        return table[-1][-1]
    # Reference: https://www.youtube.com/watch?v=SqDjsZG3Mkc

    def is_kpi_value_same(self, extracted_kpi, annotated_kpi):
        ''' Only compare the extracted KPI value and real KPI value,
        and check if they are the same.'''
        extkpi_number = self.get_kpi_number(extracted_kpi)
        annokpi_number = self.get_kpi_number(annotated_kpi)
        print("Extracted and real number of KPI value:", extkpi_number, annokpi_number)

        if extkpi_number == annokpi_number:
            if self.levenshtein_distance(extracted_kpi,annotated_kpi) <= 5:
                print("KPI value are same.")
                return True
        else:
            print("KPI value are different.")
            return False

    def compare_extracted_annotated_kpi(self):
        ''' For the same PDF file, the same question checks
        if the extracted KPI and real KPi are the same.'''
        count_extracted_only, count_annotated_only, count_match_equal,count_match_unequal = 0, 0, 0, 0

        for i in self.extra_datas:
            print("Extracted KPI data:", i)
            ismatched = False
            for j in self.anno_datas:
                print("Real KPI data:", j)
                if i[0] == j[0] and i[1] == j[1]:
                    ismatched = True
                    if self.is_kpi_value_same(i[2], j[2]):
                        count_match_equal += 1
                        print("count match equal:", count_match_equal)
                    else:
                        count_match_unequal += 1
                        print("coung match unequal:", count_match_unequal)
            print("Inner loop is done:", ismatched)
            if not ismatched:
                count_extracted_only += 1
                print("count extracted only:", count_extracted_only)
        print("Outer loop is done:")
        count_annotated_only = len(self.anno_datas) - count_match_equal - count_match_unequal
        print("count annotated only:", count_annotated_only)

        print("---------------------")
        print("count extracted only:", count_extracted_only)
        print("count annotated only:", count_extracted_only)
        print("count match equal:", count_match_equal)
        print("count match unequal:", count_match_unequal)
        return count_match_equal, count_match_unequal, count_extracted_only, count_annotated_only
    # Reference: TestEvaluation.py of Dr. Ismail Demir
