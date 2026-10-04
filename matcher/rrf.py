def reciprocal_rank_fusion(result_lists, k=60, top_k=10):
    """
    Merge several ranked lists into one list using RRF.

    Each item in a result list should be a dict with at least:
    - id
    - title
    - employer

    Rank starts at 1 for the first item in each list.
    """
    scores = {}
    info = {}

    for results in result_lists:
        for rank, job in enumerate(results, start=1):
            job_id = job["id"]
            scores[job_id] = scores.get(job_id, 0.0) + 1.0 / (k + rank)
            # Keep display fields from the first time we see this job
            if job_id not in info:
                info[job_id] = {
                    "id": job_id,
                    "title": job["title"],
                    "employer": job["employer"],
                }

    fused = []
    for job_id, rrf_score in scores.items():
        item = info[job_id].copy()
        item["score"] = round(rrf_score, 6)
        fused.append(item)

    fused.sort(key=lambda x: x["score"], reverse=True)
    return fused[:top_k]
