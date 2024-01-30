#FROM pytorch/pytorch:latest
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

RUN pip install farm-haystack[all-gpu]
RUN pip install 'farm-haystack[docstores-gpu]'
RUN pip install pdf2image
RUN pip install pdfminer.six
RUN pip install fuzzywuzzy

COPY ./new_ml_based_pipeline /app/code/new_ml_based_pipeline

RUN mkdir -p /app/code/new_ml_based_pipeline/myhome/

RUN chgrp -R 0 /app/code/new_ml_based_pipeline && chmod g=u /app/code/new_ml_based_pipeline
RUN chmod -R 777 /app/code/new_ml_based_pipeline

RUN apt-get update && apt-get install -y wget sudo
RUN apt-get install -y poppler-utils
RUN apt-get install -y vim

# install Tesseract
RUN apt-get install -y tesseract-ocr libtesseract-dev

WORKDIR /app/code/new_ml_based_pipeline

RUN mkdir -p /app/server_logs

RUN chmod u+x entry.sh
CMD ./entry.sh
