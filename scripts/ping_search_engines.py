"""
Automated Search Engine & IndexNow Ping Script for Don Aurelius.
Notifies Google, Bing, and IndexNow to crawl the live sitemap immediately.
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SearchEnginePinger")

SITEMAP_URL = "https://smkanish2009-blip.github.io/don-aurelius/sitemap.xml"
HOST = "smkanish2009-blip.github.io"
KEY = "3dc68ac1e88c5dba"

URL_LIST = [
    "https://smkanish2009-blip.github.io/don-aurelius/",
    "https://smkanish2009-blip.github.io/don-aurelius/checkout.html",
    "https://smkanish2009-blip.github.io/don-aurelius/forward-test.html",
    "https://smkanish2009-blip.github.io/don-aurelius/thank-you.html",
    "https://smkanish2009-blip.github.io/don-aurelius/404.html"
]

def ping_google():
    url = f"https://www.google.com/ping?sitemap={SITEMAP_URL}"
    try:
        r = requests.get(url, timeout=10)
        logger.info(f"Google Sitemap Ping Response: {r.status_code}")
    except Exception as e:
        logger.warning(f"Google ping error: {e}")

def ping_bing():
    url = f"https://www.bing.com/ping?sitemap={SITEMAP_URL}"
    try:
        r = requests.get(url, timeout=10)
        logger.info(f"Bing Sitemap Ping Response: {r.status_code}")
    except Exception as e:
        logger.warning(f"Bing ping error: {e}")

def ping_indexnow():
    """IndexNow API instantly dispatches changes to Bing, Yandex, Seznam, and partner engines."""
    endpoint = "https://api.indexnow.org/IndexNow"
    payload = {
        "host": HOST,
        "key": KEY,
        "urlList": URL_LIST
    }
    try:
        r = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        logger.info(f"IndexNow API Dispatch Response: {r.status_code} ({r.text[:100]})")
    except Exception as e:
        logger.warning(f"IndexNow dispatch error: {e}")

if __name__ == "__main__":
    print("Initiating Global Search Engine Indexation Pings...")
    ping_google()
    ping_bing()
    ping_indexnow()
    print("Search engine notification cycle complete!")
