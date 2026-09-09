import os
from playwright.sync_api import sync_playwright

url = os.environ["APP_URL"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, timeout=30000)
    try:
        page.get_by_text("Yes, get this app back up!").click(timeout=5000)
        print("App was asleep -- clicked wake button.")
        page.wait_for_timeout(15000)
    except Exception as e:
        print(f"No wake button found (app likely already awake): {e}")
    browser.close()
