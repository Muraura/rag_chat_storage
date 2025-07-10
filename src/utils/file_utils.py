from collections import OrderedDict
import os
# from pdfminer.high_level import extract_text as pdf_extract
# from docx import Document
import boto3
from fastapi import FastAPI, UploadFile, File, HTTPException
from uuid import uuid4
import os
s3_client = boto3.client("s3", region_name="us-east-2")
textract_client = boto3.client("textract", region_name="us-east-2")




ALLOWED_EXTENSIONS = [".pdf", ".docx"]
UPLOAD_DIR = "/tmp/resumes"


async def sort_dict(unsorted_dict):
    sorted_dict = OrderedDict(sorted(unsorted_dict.items()))
    return sorted_dict



# def extract_text_from_file(file_path):
#     ext = os.path.splitext(file_path)[1].lower()

#     if ext == ".pdf":
#         try:
#             # Try native text PDF first
#             text = pdf_extract(file_path)
#             if text.strip():
#                 return text
#         except:
#             pass
#         # fallback to Textract (OCR for scanned PDFs)
#         return extract_with_textract(file_path)

#     elif ext == ".docx":
#         doc = Document(file_path)
#         return "\n".join([p.text for p in doc.paragraphs])

#     else:
#         raise ValueError(f"Unsupported extension: {ext}")

def extract_text_from_file(file_path):
    return extract_with_textract(file_path)





def extract_with_textract(s3_key: str, bucket_name: str = "chatfileragchat"):
    try:
        response = textract_client.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': s3_key
                }
            }
        )

        lines = [b["Text"] for b in response.get("Blocks", []) if b.get("BlockType") == "LINE"]
        print("Extracted lines:", lines)  # optional preview
        return "\n".join(lines)

    except Exception as e:
        print(f"[extract_with_textract] Error processing s3://{bucket_name}/{s3_key}:", e)
        return ""


