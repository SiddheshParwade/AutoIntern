import requests
from bs4 import BeautifulSoup
import random

def scrape_internships(urls, keywords, start_page=1, end_page=101, update_callback=None):
    session = requests.Session()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    ]

    products, refined_products, unfetched_pages = [], [], []

    def get_headers():
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "application/x-clarity-gzip",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-US;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://internshala.com",
            "Referer": "https://internshala.com/",
        }

    def scrape_details(link):
        try:
            r = session.get(link, headers=get_headers(), timeout=10)
            if r.status_code != 200:
                return "N/A", "N/A", "N/A", []

            soup = BeautifulSoup(r.text, 'html.parser')
            data = soup.find_all('div', class_='item_body')
            join = soup.find('span', class_='start_immediately_desktop')
            container = soup.find_all('div', class_='round_tabs_container')

            join_date = join.text.strip() if join else "N/A"
            duration = data[1].text.strip() if len(data) > 1 else "N/A"
            last_date = data[3].text.strip() if len(data) > 3 else "N/A"

            skills = []
            if container:
                skills = [i.text.strip() for i in container[0].find_all('span', class_='round_tabs')]

            return join_date, last_date, duration, skills
        except Exception:
            return "N/A", "N/A", "N/A", []

    def scrape_pages(base_url, start, end):
        for page in range(start, end):
            if update_callback:
                update_callback(base_url, page)
            try:
                r = session.get(f"{base_url}/page-{page}/", headers=get_headers(), timeout=10)
                if r.status_code != 200:
                    unfetched_pages.append((base_url, page))
                    continue

                soup = BeautifulSoup(r.text, 'html.parser')
                cards = soup.find_all('div', class_='internship_meta duration_meta')
                if not cards:
                    continue

                for count, card in enumerate(cards, start=1):
                    job_tag = card.find("a", class_="job-title-href")
                    if not job_tag:
                        continue

                    job_link = "https://internshala.com" + job_tag.get('href')
                    name = job_tag.text.strip()
                    location = card.find("div", class_="row-1-item locations")
                    location = location.text.strip() if location else "N/A"
                    salary = card.find("span", class_="stipend")
                    salary = salary.text.strip() if salary else "N/A"
                    post_time = (
                        card.find("div", class_="status-success") or 
                        card.find("div", class_="status-info") or 
                        card.find("div", class_="status-inactive")
                    )
                    post_time = post_time.text.strip() if post_time else "N/A"

                    join_date, last_date, duration, skills = scrape_details(job_link)
                    item = [count, name, location, salary, post_time, join_date, last_date, duration, skills, job_link]
                    products.append(item)

                    if any(k in s.lower() for k in keywords for s in skills):
                        refined_products.append(item)
            except Exception:
                continue

    for base_url in urls:
        scrape_pages(base_url, start_page, end_page)

    for base_url, page in unfetched_pages:
        scrape_pages(base_url, page, page + 1)

    return products, refined_products
