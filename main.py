import csv
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule 
import time
from datetime import datetime

SENDER = "nielswartz11@gmail.com"
PASSWORD = "Google_Password"
RECEIVER = "nielswartz11@gmail.com"

def send_mail(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg["Subject"] = subject
    
    # msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
        print("Email was successful")
    except Exception as e:
        print(f"Failed to send mail: {e}")

def format_prices(results):
    lines = ["Weekly price report!\n"]
    for site, price in results:
        lines.append(f"{site}: {price}")
    return "\n".join(lines)

def fetch_prices(url):
    headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/90.0 Safari/537.36")
    }
    
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    price_tag = soup.find(string=re.compile(r"R\s*[\d.,]+"))
    if not price_tag:
        raise RuntimeError("Price not found!")
    
    price_str = price_tag.strip()
    amount = re.sub(r"[^\d\.]", "", price_str)
    price_float = float(amount)
    print(f"Searching in: {soup.title.string if soup.title else 'No Title'}")
    print(f"Found price string: {price_tag}")
    return price_float

def fetch_all_prices(csv_file):
    prices = []
    with open(csv_file, newline='',encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            site = row["site"]
            url = row["url"]
            try:
                price = fetch_prices(url)
            except Exception as e:
                price = f"Error: {str(e)}"
            prices.append((site, price))
    return prices

def job():
    print(f"[{datetime.now()}] Running price check!")
    results = fetch_all_prices("sites.csv")
    email_body = format_prices(results)
    send_mail("Weekly Prices", email_body)
    
schedule.every().friday.at("14:00").do(job)

print("Scheduler started. Waiting for friday 14:00!")
while True:
    schedule.run_pending()
    time.sleep(60)
                
