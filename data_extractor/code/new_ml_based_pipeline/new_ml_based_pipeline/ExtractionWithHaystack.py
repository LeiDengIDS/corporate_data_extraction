# ============================================================================================================================
# PDF_Extractor
# File   : ExtractionWithHaystack.py
# Author : Lei Deng
# Date   : 27.07.2023
# ============================================================================================================================

''' An extractor using the Haystack method with 2 NLP models - the retriever model and the reader model.
The retriever model extracts question-relevant paragraphs; the reader model extracts answers (KPI) 
from returned paragraphs by the retriever model.'''

import subprocess
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import EmbeddingRetriever, TransformersReader
from haystack.pipelines import ExtractiveQAPipeline
from pathlib import Path
import json

class ExtractionWithHaystack:
    def __init__(self, pdf_path,json_save_path, csv_file_path, retriever_model,reader_model):
        self.pdf_path = pdf_path
        self.json_save_path = json_save_path
        self.csv_file_path = csv_file_path
        self.retriever_model = retriever_model
        self.reader_model = reader_model

    def create_elastics_docuStore(self):
        '''Creating a document store and read PDF Paragraphs from JSON into document store.'''
        # Start Search Engine: Elasticsearch
        command = "elasticsearch reopen"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Initializing Document Store
        # document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", return_embedding=True)
        document_store = ElasticsearchDocumentStore(host="elasticsearch.aicos-osc-demo.svc.cluster.local", username="",
                                                    password="", return_embedding=True)
        # reset document store to clean caches
        document_store.delete_documents()

        print("Import PDF data to Document Store:")
        with open(self.json_save_path, "r") as file:
            paras = json.load(file)

        dicts_list = []
        for paragraph in paras:
            page_number = paragraph["page"][0]
            para = paragraph["paragraph"][0]
            x0 = paragraph["coordinates"]["x0"]
            y0 = paragraph["coordinates"]["y0"]

            dicts_list.append({
                'content': para,
                'meta': {'source': Path(self.pdf_path).name, 'page number': page_number, 'coordinate': (x0, y0)}
            })

        document_store.write_documents(dicts_list)
        print(len(dicts_list), " Data is imported into Document Store.")
        return document_store

    def extract_kpi(self, document_store, query):
        '''Create the retriever and reader to extract KPI from PDF.'''
        print("Initializing Retriever: ")
        retriever = EmbeddingRetriever(
            document_store=document_store,
            embedding_model=self.retriever_model,
            model_format="sentence_transformers",
            use_gpu=True
        )
        print("Retriever update embeddings: ")
        document_store.update_embeddings(retriever)

        # print("testing retriever")
        # retr_doc = retriever.retrieve(query = query, top_k = 5)
        # print("Retriever - Top 5 Paragraphs: ",retr_doc)

        print("Initializing Reader: ")
        reader = TransformersReader(self.reader_model,use_gpu=True)

        # print("testing reader")
        # reader_doc = reader.predict(query = query, documents=document_store, top_k = 5)
        # print("Reader - Top 5 answers: ", reader_doc)

        # Initializing Pipeline (add reader and retriever together to a pipeline)
        print("Initializing Pipeline: ")
        pipe = ExtractiveQAPipeline(reader, retriever)
        preds = pipe.run(query=query, params={"Retriever": {"top_k": 5}, "Reader": {"top_k": 1}})
        print("Answer:", preds)
        return preds














