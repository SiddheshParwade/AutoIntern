import requests
from bs4 import BeautifulSoup
import random

def scrape_internships(urls, keywords, start_page=1, end_page=101):
    session = requests.Session()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
    ]

    products = []
    refined_products = []
    unfetched_pages = []

    def get_headers():
        return {
            "Accept": "application/x-clarity-gzip",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-US;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://internshala.com",
            "Referer": "https://internshala.com/",
            "User-Agent": random.choice(user_agents),
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

    def scrape_details(link):
        try:
            r = session.get(link, headers=get_headers())
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
                skill_tags = container[0].find_all('span', class_='round_tabs')
                skills = [i.text.strip() for i in skill_tags]

            return join_date, last_date, duration, skills
        except Exception as e:
            print(f"⚠️ Error scraping details from {link}: {e}")
            return "N/A", "N/A", "N/A", []

    def scrape_pages(base_url, start, end):
        for page in range(start, end):
            url = f"{base_url}/page-{page}/"
            print(f"Scraping: {url}")
            try:
                r = session.get(url, headers=get_headers())
                if r.status_code != 200:
                    unfetched_pages.append((base_url, page))
                    continue

                soup = BeautifulSoup(r.text, 'html.parser')
                cards = soup.find_all('div', class_='internship_meta duration_meta')
                if not cards:
                    continue

                for count, card in enumerate(cards, start=1):
                    job_link = "https://internshala.com" + card.find("a", class_="job-title-href").get('href')
                    join_date, last_date, duration, skills = scrape_details(job_link)

                    name = card.find("a", class_="job-title-href").text.strip()
                    location = card.find("div", class_="row-1-item locations").text.strip()
                    salary = card.find("span", class_="stipend").text.strip()
                    post_time = (card.find("div", class_="status-success") or 
                                 card.find("div", class_="status-info") or 
                                 card.find("div", class_="status-inactive"))
                    post_time = post_time.text.strip() if post_time else "N/A"

                    item = [count, name, location, salary, post_time, join_date, last_date, duration, skills, job_link]
                    products.append(item)

                    if any(k.lower() in s.lower() for s in skills for k in keywords):
                        refined_products.append(item)

            except Exception as e:
                print(f"❌ Failed scraping page {page} from {base_url}: {e}")
                continue

    # Start scraping
    for base_url in urls:
        scrape_pages(base_url, start_page, end_page)

    # Retry unfetched pages
    if unfetched_pages:
        print(f"\nRetrying failed pages: {unfetched_pages}\n")
        for base_url, page in unfetched_pages:
            scrape_pages(base_url, page, page+1)

    return products, refined_products



# urls = [
#     "https://internshala.com/internships/web-development-internship/",
#     "https://internshala.com/internships/python-django-internship/"
# ]

# keywords = {"django"}

# original, refined = scrape_internships(urls, keywords ,1,3)

# print(f"\nTotal: {len(original)} internships scraped")
# print(f"Matched: {len(refined)} with keywords {keywords}\n")
# for i in refined:
#     print(i)