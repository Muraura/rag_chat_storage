import re
import os

import ffmpeg
import uuid
import boto3
import spacy



import openai
from uuid import uuid4
from celery import Celery
from src.utils.file_utils import extract_text_from_file
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os
import tempfile
import uuid
import shutil
import asyncio

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

import ffmpeg
import openai


openai.api_key = "your-api-key"

s3_client = boto3.client("s3", region_name="us-east-2")
BUCKET_NAME = "chatfileragchat"
S3_PREFIX = "chat_files"


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

STATIC_JOB_DESCRIPTION = """
We are hiring a Python backend engineer with experience in FastAPI, PostgreSQL, and AWS.
"""

SKILL_KEYWORDS = [
    "Python", "FastAPI", "Django", "PostgreSQL", "MySQL", "MongoDB", "AWS", "Docker",
    "Kubernetes", "REST", "GraphQL", "Git", "Redis", "Celery", "Pandas", "Numpy"
]

EDUCATION_KEYWORDS = [
    "Bachelor", "B.Sc", "Bachelors", "Master", "M.Sc", "MBA", "PhD", "Doctorate", "Associate"
]

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?[\d\s\-]{6,15}', text)
    return match.group().strip() if match else None

def extract_skills(text):
    return [skill for skill in SKILL_KEYWORDS if skill.lower() in text.lower()]

def extract_education(text):
    found = []
    for keyword in EDUCATION_KEYWORDS:
        if keyword.lower() in text.lower():
            found.append(keyword)
    return found

def extract_latest_company(doc):
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    return orgs[-1] if orgs else None

def extract_location(doc):
    gpes = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return gpes[0] if gpes else None

def parse_and_process_resume(file_path_or_s3key):
    try:
        # Step 1: Extract full raw text from the resume
        resume_text = extract_text_from_file(file_path_or_s3key)
        print("Extracted text snippet:", resume_text[:300])

        # Step 2: Process with spaCy
        doc = nlp(resume_text)
        name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        skills = extract_skills(resume_text)
        education = extract_education(resume_text)
        latest_company = extract_latest_company(doc)
        location = extract_location(doc)

        # Step 3: Compute resume vs JD overall similarity
        resume_vec = sbert_model.encode(resume_text, convert_to_tensor=True)
        jd_vec = sbert_model.encode(STATIC_JOB_DESCRIPTION, convert_to_tensor=True)
        similarity_score = util.cos_sim(resume_vec, jd_vec).item()

        # Step 4: Score each skill vs JD
        filtered_skills = []
        if skills:
            skill_scores = {}
            for skill in skills:
                skill_vec = sbert_model.encode(skill, convert_to_tensor=True)
                score = util.cos_sim(skill_vec, jd_vec).item()
                skill_scores[skill] = score

            # Select top 5 relevant skills
            top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            filtered_skills = [skill for skill, _ in top_skills]

        # Step 5: Generate interview questions using top skills
        if filtered_skills:
            prompt = f"""
                    You are a backend technical interviewer.

                    Based on the candidate's most relevant skills and this job description, generate 5 technical interview questions that test real-world backend experience and AI/ML system integration.

                    Candidate Skills:
                    {', '.join(filtered_skills)}

                    Job Description:
                    {STATIC_JOB_DESCRIPTION}

                    Respond only with the list of questions.
                    """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )
            questions = response['choices'][0]['message']['content'].strip().split('\n')
        else:
            questions = []
        print("######questions", questions)
        # Final structured candidate output
        candidate_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "latest_company": latest_company,
            "location": location,
            "similarity_score": similarity_score,
            "top_relevant_skills": filtered_skills,
            "interview_questions": questions,
            "raw_text_snippet": resume_text[:500],
            "source_path": file_path_or_s3key,
        }

        print("### candidate_info", candidate_info)
        return {
                "candidate_info": candidate_info,
                "questions": questions
            }

    except Exception as e:
        print("[Error in parse_and_process_resume]:", e)
        return None





def upload_file_to_s3(file_bytes: bytes, file_ext: str) -> str:
    file_id = str(uuid4())
    s3_key = f"{S3_PREFIX}/{file_id}{file_ext}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes)
    return s3_key

def download_s3_file(s3_key: str) -> str:
    local_path = os.path.join("/tmp", os.path.basename(s3_key))  # or UPLOAD_DIR
    s3_client.download_file(BUCKET_NAME, s3_key, local_path)
    return local_path

def process_candidate_video(session_id: str, job_id: str, s3_video_key: str):
   
    video_temp_path = f"/tmp/{uuid.uuid4()}.mp4"
    audio_temp_path = f"/tmp/{uuid.uuid4()}.wav"
    extract_audio_from_video(video_temp_path, audio_temp_path)
    transcription_text = transcribe_audio(audio_temp_path)

    questions = get_interview_questions_for_session(session_id)
    scores = []
    for question in questions:
        score = score_answer(question, transcription_text)
        scores.append({"question": question, "score": score})

    # Save scores to DB here
    print(f"Session {session_id} scores: {scores}")

    # Clean up temp files
    try:
        os.remove(video_temp_path)
        os.remove(audio_temp_path)
    except Exception:
        pass

def extract_audio_from_video(video_path: str, audio_path: str):
    ffmpeg.input(video_path).output(audio_path, format="wav", ac=1, ar=16000).run(overwrite_output=True)

async def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        transcription = openai.Audio.transcribe("whisper-1", f)
    return transcription["text"]


async def score_answer(question: str, answer: str) -> int:
    prompt = f"""
    You are an expert technical interviewer.

    Question:
    {question}

    Candidate's answer transcription:
    {answer}

    Rate the answer on a scale from 1 to 10 based on relevance, correctness, and completeness.
    Only provide the score as an integer.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    try:
        score = int(response["choices"][0]["message"]["content"].strip())
    except Exception:
        score = 0
    return score
def get_interview_questions_for_session(session_id: str):
    # In real use: query DB for questions linked to session/job
    return [
        "What backend frameworks have you used?",
        "Explain how you would design a scalable API.",
        "Describe your experience with AI/ML integration.",
        "How do you handle error handling in microservices?",
        "What message brokers have you worked with?",
    ]