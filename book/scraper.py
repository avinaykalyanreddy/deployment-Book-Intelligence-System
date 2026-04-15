from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def scrape_book(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(3)  # wait for page load

    try:
        title = driver.find_element(By.TAG_NAME, "h1").text
    except:
        title = ""

    try:
        author = driver.find_element(By.CSS_SELECTOR, "span.ContributorLink__name").text
    except:
        author = ""

    try:
        rating = driver.find_element(By.CSS_SELECTOR, "div.RatingStatistics__rating").text
    except:
        rating = ""

    try:
        description = driver.find_element(By.CSS_SELECTOR, "div.TruncatedContent__text").text
    except:
        description = ""

    try:
        image = driver.find_element(By.CSS_SELECTOR, "img.ResponsiveImage").get_attribute("src")
    except:
        image = ""

    driver.quit()

    return {
        "title": title,
        "author": author,
        "rating": rating,
        "description": description,
        "image_url": image,
        "book_url": url
    }