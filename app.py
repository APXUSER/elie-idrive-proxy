from flask import Flask, request, jsonify
import boto3
from botocore.client import Config
import os

app = Flask(__name__)

# Configure iDrive e2 credentials
IDRIVE_ACCESS_KEY = os.environ.get("IDRIVE_ACCESS_KEY")
IDRIVE_SECRET_KEY = os.environ.get("IDRIVE_SECRET_KEY")
IDRIVE_BUCKET = os.environ.get("IDRIVE_BUCKET", "customer-documents")
IDRIVE_ENDPOINT = os.environ.get("IDRIVE_ENDPOINT", "https://s3.eu-central-2.idrivee2.com")

s3 = boto3.client(
    "s3",
    endpoint_url=IDRIVE_ENDPOINT,
    aws_access_key_id=IDRIVE_ACCESS_KEY,
    aws_secret_access_key=IDRIVE_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Receives JSON from APEX:
    {
        "customer": "432424",
        "category": "invoices",
        "filename": "invoice123.pdf",
        "filedata": "<base64>"
    }
    """
    data = request.get_json()
    customer = data["customer"]
    category = data["category"]
    filename = data["filename"]
    filedata = data["filedata"]

    import base64, io
    file_bytes = base64.b64decode(filedata)
    key = f"{customer}/{category}/{filename}"

    s3.upload_fileobj(io.BytesIO(file_bytes), IDRIVE_BUCKET, key)
    url = f"{IDRIVE_ENDPOINT}/{IDRIVE_BUCKET}/{key}"
    return jsonify({"status": "ok", "url": url})

@app.route("/")
def home():
    return "iDrive E2 Upload Proxy is running"
