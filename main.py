import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load local .env if exists (optional for local testing)
load_dotenv()

# --- Twilio credentials from Render environment ---
ACCOUNT_SID = os.getenv("TWILIO_SID")
AUTH_TOKEN = os.getenv("TWILIO_TOKEN")
FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = os.getenv("TO_WHATSAPP")

# --- LinkedIn job search URL ---
URL = "https://www.linkedin.com/jobs/search/?keywords=fresher%20engineer%20intern&sortBy=DD"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Persist seen jobs to avoid duplicate messages across runs
SEEN_FILE = "seen_jobs.txt"

def load_seen_jobs():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen_jobs(seen_jobs):
    with open(SEEN_FILE, "w") as f:
        for job in seen_jobs:
            f.write(f"{job}\n")

def send_whatsapp_message(job_title, company, link):
    message = f"🆕 *New Job Alert!*\n\n{job_title} at {company}\n🔗 {link}"
    client.messages.create(from_=FROM_WHATSAPP, body=message, to=TO_WHATSAPP)
    print("✅ WhatsApp alert sent:", job_title)

def check_jobs():
    seen_jobs = load_seen_jobs()
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for job in soup.find_all("div", class_="base-card"):
        title_tag = job.find("h3", class_="base-search-card__title")
        company_tag = job.find("h4", class_="base-search-card__subtitle")
        link_tag = job.find("a", class_="base-card__full-link")

        if title_tag and company_tag and link_tag:
            title = title_tag.text.strip()
            company = company_tag.text.strip()
            link = link_tag["href"].split("?")[0]

            if link not in seen_jobs:
                seen_jobs.add(link)
                send_whatsapp_message(title, company, link)

    save_seen_jobs(seen_jobs)

if __name__ == "__main__":
    print("🚀 Running LinkedIn job alert...")
    try:
        check_jobs()
    except Exception as e:
        print("❌ Error:", e)
