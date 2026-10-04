from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from pathlib import Path

from matcher.bm25_search import get_job_by_id, load_jobs
from matcher.bm25_search import search_jobs as search_bm25
from matcher.rrf import reciprocal_rank_fusion
from matcher.vector_search import search_jobs as search_vector


def home(request):
    message = None
    final_results = []

    if request.method == "POST" and request.FILES.get("resume"):
        resume = request.FILES["resume"]

        if not resume.name.lower().endswith(".txt"):
            message = "Please upload a .txt file"
        else:
            save_dir = Path("data/resumes")
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / resume.name

            with open(save_path, "wb+") as f:
                for chunk in resume.chunks():
                    f.write(chunk)

            resume_text = save_path.read_text(encoding="utf-8", errors="replace")

            bm25_results = search_bm25(resume_text)
            vector_results = search_vector(resume_text)
            final_results = reciprocal_rank_fusion(
                [bm25_results, vector_results],
                top_k=10,
            )

            message = f"Saved {resume.name}. Found {len(final_results)} matches."

    return render(
        request,
        "matcher/home.html",
        {
            "message": message,
            "final_results": final_results,
        },
    )


def browse_jobs(request):
    query = (request.GET.get("q") or "").strip()
    jobs = load_jobs()

    if query:
        q = query.lower()
        jobs = [
            job
            for job in jobs
            if q in (job.get("title") or "").lower()
            or q in (job.get("employer") or "").lower()
            or q in (job.get("location") or "").lower()
            or q in (job.get("majors") or "").lower()
            or q in (job.get("position_description") or "").lower()
        ]

    paginator = Paginator(jobs, 25)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "matcher/jobs_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "total_count": paginator.count,
        },
    )


def job_detail(request, job_id):
    job = get_job_by_id(job_id)
    if not job:
        raise Http404("Job not found")
    return render(request, "matcher/job_detail.html", {"job": job})
