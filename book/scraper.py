import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def fetch_html(url):
    for _ in range(3):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9"
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.text

        except requests.RequestException:
            pass

        time.sleep(2)

    return None


def scrape_book(url):
    html = fetch_html(url)

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    try:
        title = soup.select_one("h1")
        author = soup.select_one(".ContributorLink__name")
        rating = soup.select_one(".RatingStatistics__rating")
        description = soup.select_one('[data-testid="description"]')
        image = soup.select_one("img")

        return {
            "title": title.text.strip() if title else None,
            "author": author.text.strip() if author else None,
            "rating": rating.text.strip() if rating else None,
            "description": description.text.strip() if description else None,
            "image_url": image["src"] if image else None
        }

    except Exception:
        return None