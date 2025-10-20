from util import db_pipeline
import pandas as pd
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

sender_email = 'charlesfuss8@gmail.com'
recipient_email = ['charlesfuss8@gmail.com', 'gingersakarya@gmail.com']
sites = ['compass', 'redfin', 'zillow', 'streeteasy']

if __name__ == '__main__':
    for site in sites:
        print(f"Starting pipeline for {site}")
        resp = db_pipeline(site)
        if type(resp) == pd.DataFrame and len(resp) == 0: 
            print(f"ChatGPT couldn't find any new listings on {site.title()}; moving on...")
            continue
        print(f"debug: {type(resp)} {len(resp)}")
        # Create email
        email_subject = f"Newest Apartments ({site.title()} only)"
        email_body = resp
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Subject'] = email_subject
        msg.attach(MIMEText(email_body, 'plain'))

        try:
            with smtplib.SMTP(config['email']["smtp_server"], config['email']["smtp_port"]) as server:
                server.starttls()
                server.login(sender_email, config['email']["sender_password"])
                for mail in recipient_email:
                    server.sendmail(sender_email, mail, msg.as_string())
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")