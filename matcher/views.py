from django.shortcuts import render
from pathlib import Path

def home(request):
    message = None

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

            message = f"Saved to data/resumes/{resume.name}"

    return render(request, "matcher/home.html", {"message": message})