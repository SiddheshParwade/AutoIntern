from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .scraper import scrape_internships

@login_required
def dashboard(request):
    main_data=[]
    internships = []
    if request.method == "POST":
        urls_input = request.POST.get('urls', '')
        keywords_input = request.POST.get('keywords', '')
        start_page = int(request.POST.get('start_page', 1))
        end_page = int(request.POST.get('end_page', 1))

        urls = [url.strip() for url in urls_input.split(',') if url.strip()]
       
        keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]
        

        if urls and keywords:
            print(urls,keywords,start_page,end_page)
            main_data , internships = scrape_internships(urls, keywords, start_page, end_page)

    return render(request, "dashboard.html", {"internships": internships})
