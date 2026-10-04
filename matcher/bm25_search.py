import csv
from pathlib import Path
from rank_bm25 import BM25Okapi

JOBS_CSV = Path("data/jobs/sample_jobs.csv")
# For local private data only (do not commit): data/jobs/all_drexel_coops_export.csv

def _tokenize(text: str):
    return text.lower().split()

def load_jobs():
    jobs = []
    with open(JOBS_CSV, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = " ".join([
                row.get("Job Title", ""),
                row.get("Employer", ""),
                row.get("Position Description", ""),
                row.get("Qualifications", ""),
                row.get("Majors Sought", ""),
            ])
            jobs.append({
                "id": row.get("Job ID", ""),
                "title": row.get("Job Title", ""),
                "employer": row.get("Employer", ""),
                "text": text,
                "location": row.get("Office Location", ""),
                "job_type": row.get("Job Type", ""),
                "duration": row.get("Duration", ""),
                "status": row.get("Status", ""),
                "company_description": row.get("Company Description", ""),
                "position_description": row.get("Position Description", ""),
                "qualifications": row.get("Qualifications", ""),
                "majors": row.get("Majors Sought", ""),
                "compensation": row.get("Compensation", ""),
                "hours": row.get("Hours/Week", ""),
                "min_gpa": row.get("Min GPA", ""),
            })
    return jobs

def get_job_by_id(job_id: str):
    for job in load_jobs():
        if str(job["id"]) == str(job_id):
            return job
    return None

def search_jobs(resume_text: str, top_k: int = 10):
    jobs = load_jobs()
    corpus = [_tokenize(job["text"]) for job in jobs]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(resume_text))

    ranked = sorted(
        zip(jobs, scores),
        key=lambda x: x[1],
        reverse=True,
    )[:top_k]

    results = []
    for job, score in ranked:
        results.append({
            "id": job["id"],
            "title": job["title"],
            "employer": job["employer"],
            "score": round(float(score), 3),
        })
    return results
