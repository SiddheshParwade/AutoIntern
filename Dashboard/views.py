from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .scraper import scrape_internships
import threading

scraping_status = {"status": "", "page": 0}
latest_internships = []  # store data temporarily

@login_required
def dashboard(request):
    global scraping_status, latest_internships

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(scraping_status)

    # handle form submission
    if request.method == "POST":
        urls_input = request.POST.get('urls', '')
        keywords_input = request.POST.get('keywords', '')
        start_page = request.POST.get('start_page', '')
        end_page = request.POST.get('end_page', '')

        urls = [url.strip() for url in urls_input.split(',') if url.strip()]
        keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]

        if urls and keywords and start_page and end_page:
            scraping_status = {"status": "Starting...", "page": 0}

            def update_status(current_url, current_page):
                scraping_status["status"] = current_url
                scraping_status["page"] = current_page

            def run_scraper():
                global latest_internships
                _, latest_internships = scrape_internships(
                    urls, keywords, int(start_page), int(end_page)+1, update_callback=update_status
                )
                scraping_status["status"] = "Completed"
                scraping_status["page"] = 0

            threading.Thread(target=run_scraper).start()
            return redirect("dashboard")  # PRG: redirect after POST

    return render(request, "dashboard.html", {
        "internships": latest_internships,
        "urls_input": '',
        "keywords_input": '',
        "start_page": '',
        "end_page": ''
    })
