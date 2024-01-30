# ============================================================================================================================
# PDF_Extractor
# File   : InputPDFAnalysis.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

'''Process PDFs and save it into a structured JSON file.'''

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed, PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import json

class InputPDFAnalysis:
    def __init__(self,pdf_path,json_save_path):
        self.pdf_path = pdf_path
        self.json_save_path = json_save_path
    
    @staticmethod
    def coor_normalized(p, p_min, p_max):
        '''Map the coordinates of PDF paragraphs to the range (0,1).'''
        new_min = 0
        new_max = 1
        p_norm = (p - p_min) * (new_max - new_min) / (p_max - p_min) + new_min
        # print("p_norm: ", p_norm)
        return p_norm

    def pdf_to_para(self):
        '''Extract Paragraphs, page number and coordinates from PDFs.'''
        with open(self.pdf_path, 'rb') as fp:
            parser = PDFParser(fp)
            # Create a PDF document object that stores the document structure.
            document = PDFDocument(parser)
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed

            # Create a PDF resource manager that stores shared resources
            resourcemgr = PDFResourceManager()
            # Set parameters for layout analysis
            laparams = LAParams()
            # Create a PDF page aggregator object.
            device = PDFPageAggregator(resourcemgr, laparams=laparams)
            # Create a PDF interpreter object.
            interpreter = PDFPageInterpreter(resourcemgr, device)

            page_number = 0
            paragraphs, page_numbers, coordinates = [],[],[]
            # Loop over all pages of PDF
            for page in PDFPage.create_pages(document):
                page_number += 1
                # read the page into a layout
                interpreter.process_page(page)
                # Get the LTPage object for the page
                layout = device.get_result()

                for obj in layout:
                    if hasattr(obj, 'get_text'):
                        x0, y0, x1, y1 = obj.bbox
                        # page_width = page.mediabox[2] - page.mediabox[0]
                        page_height = page.mediabox[3] - page.mediabox[1]
                        # change (0,0) from bottom-left to top-left
                        y0 = page_height - y0
                        y1 = page_height - y1
                        # coordinates normalization 
                        x0_norm = self.coor_normalized(x0, page.mediabox[0], page.mediabox[2])
                        y1_norm = self.coor_normalized(y1, page.mediabox[1], page.mediabox[3])
                        x1_norm = self.coor_normalized(x1, page.mediabox[0], page.mediabox[2])
                        y0_norm = self.coor_normalized(y0, page.mediabox[1], page.mediabox[3])

                        text = obj.get_text()
                        data = text.split('\n\n')
                        data = [sentence.replace('\n', ' ') for sentence in data]
                        data = [sentence.strip() for sentence in data]
                        data = [sentence for sentence in data if len(sentence) > 20]
                        if len(data) != 0:
                            page_numbers.append([page_number] * len(data))
                            paragraphs.append(data)
                            coordinates.append((x0_norm, y1_norm, x1_norm, y0_norm))

        return paragraphs, page_numbers, coordinates

    def save_para_to_json(self):
        ''' Saving extracted paragraphs, page number, and coordinates to JSON file.'''
        paragraphs, page_numbers, coordinates = self.pdf_to_para()
        data = []
        for i in range(len(paragraphs)):
            item = {
                'page': page_numbers[i],
                'paragraph': paragraphs[i],
                'coordinates': {
                    'x0': coordinates[i][0],
                    'y1': coordinates[i][1],
                    'x1': coordinates[i][2],
                    'y0': coordinates[i][3]
                }
            }
            data.append(item)

        with open(self.json_save_path, 'w') as file:
            json.dump(data, file, indent=4)
        print("JSON file is saved!")

