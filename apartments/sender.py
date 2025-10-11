from oai import openai_query

import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

sender_email = 'charlesfuss8@gmail.com'
recipient_email = ['charlesfuss8@gmail.com', 'gingersakarya@gmail.com']

if __name__ == '__main__':
    with open("query.txt", 'r', encoding='utf-8') as f: query = f.read()
    resp = openai_query(query)

    email_subject = "Newest Apartments"
    email_body = resp
    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(config['email']["smtp_server"], config['email']["smtp_port"]) as server:
            server.starttls()
            server.login(sender_email, config['email']["sender_password"])
            for mail in recipient_email:
                server.sendmail(sender_email, mail, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        breakpoint()
        print(f"❌ Failed to send email: {e}")
