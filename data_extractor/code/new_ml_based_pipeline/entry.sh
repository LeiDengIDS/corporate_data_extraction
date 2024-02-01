#!/bin/bash

date_time=$(date +'%d_%h_%Y:%H_%M')
log_file_path="/app/server_logs/new_ml_based_logs_${date_time}.txt"
cd /app/code/new_ml_based_pipeline/new_ml_based_pipeline
python3 new_ml_server.py > $log_file_path 2>&1 &

export HOME="/app/code/new_ml_based_pipeline/myhome/"
sleep infinity
