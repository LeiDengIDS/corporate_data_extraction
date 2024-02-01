import argparse
import os
import json

from flask import Flask, Response, request
from s3_communication import S3Communication

app = Flask(__name__)

def create_directory(directory_name):
    os.makedirs(directory_name, exist_ok=True)
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

#need to adjust
def run_new_ml_int(pdf_folder, questions, nlp_method, output_folder，nlp_model_rt='sentence-transformers/multi-qa-mpnet-base-dot-v1',nlp_model_re ='ahotrod/albert_xxlargev1_squad2_512', nlp_model_dqa='impira/layoutlm-invoices' ):
    cmd = (
        "python3 /app/code/new_ml_based_pipeline/new_ml_based_pipeline/main.py"
        + ' --pdf_folder "'
        + pdf_folder
        + '"'
        + ' --questions "'
        + questions
        + '"'
        + " --nlp_method "
        + str(nlp_method)
        + ' --output_folder "'
        + output_folder
        + '"'
        + ' --nlp_model_rt "'
        + str(nlp_model_rt)
        + '"'
        + ' --nlp_model_re "'
        + str(nlp_model_rt)
        + '"'
        + ' --nlp_model_dqa "'
        + str(nlp_model_rt)
        + '"'
    )
    print("Running command: " + cmd)
    os.system(cmd)

def run_hs(project_name, nlp_method="Haystack", s3_usage, s3_settings):
    base = r"/app/data/" + project_name
    pdf_folder = base + r"/interim/pdfs/"
    questions = base + r"/interim/newml/questions"
    output_folder = base + r"/output/KPI_EXTRACTION/newml"
    if s3_usage:
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings["main_bucket"]["s3_endpoint"]),
            aws_access_key_id=os.getenv(s3_settings["main_bucket"]["s3_access_key"]),
            aws_secret_access_key=os.getenv(s3_settings["main_bucket"]["s3_secret_key"]),
            s3_bucket=os.getenv(s3_settings["main_bucket"]["s3_bucket_name"]),
        )
        create_directory(base)
        create_directory(pdf_folder)
        create_directory(questions)
        create_directory(output_folder)
        project_prefix = s3_settings["prefix"] + "/" + project_name + "/data"
        s3c_main.download_files_in_prefix_to_dir(project_prefix + "/input/pdfs/inference", pdf_folder)
    run_new_ml_int(pdf_folder, questions, nlp_method="Haystack", output_folder)
    if s3_usage:
        s3c_main.upload_files_in_dir_to_prefix(output_folder, project_prefix + "/output/KPI_EXTRACTION/newml")
    return True

def run_dqa(project_name, nlp_method="DQA", s3_usage, s3_settings):
    base = r"/app/data/" + project_name
    pdf_folder = base + r"/interim/pdfs/"
    questions = base + r"/interim/newml/questions"
    output_folder = base + r"/output/KPI_EXTRACTION/newml"
    if s3_usage:
        s3c_main = S3Communication(
            s3_endpoint_url=os.getenv(s3_settings["main_bucket"]["s3_endpoint"]),
            aws_access_key_id=os.getenv(s3_settings["main_bucket"]["s3_access_key"]),
            aws_secret_access_key=os.getenv(s3_settings["main_bucket"]["s3_secret_key"]),
            s3_bucket=os.getenv(s3_settings["main_bucket"]["s3_bucket_name"]),
        )
        create_directory(base)
        create_directory(pdf_folder)
        create_directory(questions)
        create_directory(output_folder)
        project_prefix = s3_settings["prefix"] + "/" + project_name + "/data"
        s3c_main.download_files_in_prefix_to_dir(project_prefix + "/input/pdfs/inference", pdf_folder)
    run_new_ml_int(pdf_folder, questions, nlp_method="DQA", output_folder)
    if s3_usage:
        s3c_main.upload_files_in_dir_to_prefix(output_folder, project_prefix + "/output/KPI_EXTRACTION/newml")
    return True

@app.route("/liveness")
def liveness():
    return Response(response={}, status=200)

# start point, add optional parameters
@app.route("/run")
def run():
    try:
        args = json.loads(request.args["payload"])
        project_name = args["project_name"]
        s3_settings = None
        if args["s3_usage"]:
            s3_settings = args["s3_settings"]
        nlp_method = str(args["nlp_method"])
        if nlp_method == "Haystack": 
            run_hs(project_name, Haystack, args["s3_usage"], s3_settings)
        elif nlp_method == "DQA": 
            run_dqa(project_name, DQA, args["s3_usage"], s3_settings)
        return Response(response={}, status=200)
    except Exception as e:
        m = traceback.format_exc()
        return Response(response={m}, status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='new_ml server')
    # Add the arguments
    parser.add_argument('--port',
                        type=int,
                        default=8000,
                        help='port to use for the infer server')
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)
