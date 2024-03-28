#FROM pytorch/pytorch:latest
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

RUN pip install farm-haystack[all-gpu]
RUN pip install 'farm-haystack[docstores-gpu]'
RUN pip install pdf2image
RUN pip install pdfminer.six
RUN pip install fuzzywuzzy

# Install kubectl
# RUN apt-get update --allow-releaseinfo-change && apt-get install -y apt-transport-https gnupg2 wget
# RUN echo "deb [arch=amd64] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
# RUN wget -qO - https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
# RUN apt-get update
# RUN apt-get install -y kubectl

# install kubectl
# RUN apt-get update && apt-get install -y apt-transport-https gnupg wget
# RUN wget -qO- https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
# RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list
# RUN apt-get update
# RUN apt-get install -y kubectl

# Download kubectl binary using wget
RUN apt-get update && apt-get install -y apt-transport-https gnupg wget
RUN wget -qO /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(wget -qO- https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
# Make kubectl executable
RUN chmod +x /usr/local/bin/kubectl

COPY ./new_ml_based_pipeline /app/code/new_ml_based_pipeline
COPY ./s3_communication.py /app/code/new_ml_based_pipeline/new_ml_based_pipeline/s3_communication.py

RUN mkdir -p /app/code/new_ml_based_pipeline/myhome/

RUN chgrp -R 0 /app/code/new_ml_based_pipeline && chmod g=u /app/code/new_ml_based_pipeline
RUN chmod -R 777 /app/code/new_ml_based_pipeline

RUN apt-get update && apt-get install -y wget sudo
#RUN apt-get install -y wget sudo
RUN apt-get install -y poppler-utils
RUN apt-get install -y vim

# install Tesseract
RUN apt-get install -y tesseract-ocr libtesseract-dev

WORKDIR /app/code/new_ml_based_pipeline

RUN mkdir -p /app/server_logs
RUN chmod -R 777 /app/server_logs

# RUN chmod u+x entry.sh
CMD ./entry.sh
