1. PREREQUISITES:

This Tool provides 2 NLP methods to extract KPI Data from PDF reports. One of them is Haystack, 
and the other one is the Hugging Face model - Document question and answering (DQA). You can choose which method 
you want to use by giving the method name "Haystack" or "DQA". 

To use this tool, Python3 and all required Python packages are needed (see requirements.txt). 


2. EXECUTION: 

2.1 Haystack

* Run elasticsearch and verify if elasticsearch is running
* Replace the path of the pdf folder, questions, and output_folder, and choose the nlp method between 'Haystack' and 'DQA'.

  4 mandatory inputs:
  
     *pdf_folder: place all PDFs to be processed into the PDF folder.
  
     *questions: place all KPI value-relevant questions into this CSV file.
  
     *nlp_method: choose the NLP method - Haystack.
  
     *output_folder: create a folder to save extracted KPI value.

  2 optional inputs:
  
    Haystack needs 2 NLP models - the retriever model & the reader model. There are default models.
    The user can choose any other suitable models by modifying optional inputs:
  

     *nlp_model_rt <model>
    
     *nlp_model_re <model>
    
   (The model can be found on this webpage: https://huggingface.co/models)
* Run python main.py (or python3 main.py)
* You can see the extracted KPI data in the output folder. 

2.2 DQA

DQA does not need to use elasticsearch, and can directly replace the path of 4 mandatory inputs (same as Haystack),
then run the main.py file and see the result in the output folder. 

The only difference is that DQA only uses 1 NLP model - The document question answering model. There is a default model. 
same as the Haystack method, the user can choose other models by modifying the below optional input: 

   *nlp_model_dqa <model>

3. EVALUATION:

To assess and visualize the performance of this tool, there is a tool for evaluation. this tool will calculate the F1
score by comparing the actual KPI value with the extracted KPI value by methods Haystack and DQA. 

Execution: 
* Replace the path of extracted_datas_haystack, extracted_datas_dqa, and annotated_datas. 

   3 inputs:
  
    *extracted_datas_haystack: extracted KPI results by using the Haystack method.
  
    *extracted_datas_dqa: extracted KPI results by using the DQA method.
  
    *annotated_datas: actual KPI data of PDF reports. 
* Run python mainEvaluation.py (or python3 mainEvaluation.py)
