from flask import Flask, request, jsonify
import boto3
import base64
import os
from botocore.exceptions import ClientError

app = Flask(__name__)

# Load environment variables from Render or local .env
IDRIVE_ACCESS_KEY = os.environ.get("IDRIVE_ACCESS_KEY")
IDRIVE_SECRET_KEY = os.environ.get("IDRIVE_SECRET_KEY")
IDRIVE_BUCKET = os.environ.get("IDRIVE_BUCKET")
IDRIVE_ENDPOINT = os.environ.get("IDRIVE_ENDPOINT")

# Initialize boto3 S3 client
s3 = boto3.client(
    "s3",
    endpoint_url=IDRIVE_ENDPOINT,
    aws_access_key_id=IDRIVE_ACCESS_KEY,
    aws_secret_access_key=IDRIVE_SECRET_KEY,
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "iDrive e2 Flask Proxy running"})

@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Expected JSON body:
    {
      "filename": "customer123/invoices/invoice1.pdf",
      "data": "<base64-encoded file>"
    }
    """
    try:
        data = request.get_json()
        filename = data.get("filename")
        file_b64 = data.get("data")

        if not filename or not file_b64:
            return jsonify({"error": "Missing filename or data"}), 400

        # Decode base64 to bytes
        file_bytes = base64.b64decode(file_b64)

        # Upload to iDrive e2 (S3-compatible)
        s3.put_object(Bucket=IDRIVE_BUCKET, Key=filename, Body=file_bytes)

        return jsonify({"status": "success", "message": f"File '{filename}' uploaded"})
    except ClientError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/list", methods=["GET"])
def list_files():
    """List all files in the bucket (optional endpoint)"""
    try:
        objects = s3.list_objects_v2(Bucket=IDRIVE_BUCKET)
        files = [obj["Key"] for obj in objects.get("Contents", [])]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
