import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re 
import smtplib
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load email config
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

smtp_server = config["email"]["smtp_server"]
smtp_port = config["email"]["smtp_port"]
sender_email = config["email"]["sender_email"]
sender_password = config["email"]["sender_password"]
recipient_email = config["email"]["recipient_email"]

BLOG_URLS = [
    "https://medium.com/airbnb-engineering/",
    "https://www.uber.com/en-US/blog/engineering/",
    "https://slack.engineering/",
    "https://netflixtechblog.com/",
    "https://medium.com/pinterest-engineering/",
    "https://medium.com/paypal-engineering/",
    "https://engineering.fb.com/",
    "https://engineering.linkedin.com/",
    "https://corp.roblox.com/newsroom?filter=engineering",
    "https://newsroom.aboutrobinhood.com/category/engineering/",
    "https://www.coinbase.com/blog/engineering"
]
BLOG_URLS.extend(
    [
    "https://stripe.com/blog/engineering",                 
    "https://developer.squareup.com/blog",                 
    "https://plaid.com/blog/engineering",                  
    "https://developer.gs.com/blog/posts",                 
    "https://www.twosigma.com/topic/engineering/",         
    "https://blog.janestreet.com/",                        
    "https://www.hudsonrivertrading.com/hrtbeat/",         
    "https://tech.affirm.com/",                            
    "https://medium.com/adyen",                            
    "https://building.nubank.com/engineering/",            
    "https://medium.com/revolut/tagged/engineering",       
    "https://medium.com/wise-engineering"                  
]

)

BLOG_URLS.extend([
    "https://newsroom.aboutrobinhood.com/category/engineering/",
    "https://www.coinbase.com/blog/engineering",
    "https://stripe.com/blog/engineering",
    "https://developer.squareup.com/blog",
    "https://plaid.com/blog/engineering",
    "https://capitalone.com/tech/blog/",
    "https://medium.com/next-at-chase",
    "https://www.jpmorgan.com/technology/technology-blog",
    "https://developer.gs.com/blog/posts",
    "https://tech.affirm.com/",
    "https://building.nubank.com/engineering/",
    "https://medium.com/revolut/tagged/engineering",
    "https://tech.klarna.com/",
    "https://medium.com/wise-engineering",
    "https://tech.adyen.com/",
    "https://www.twosigma.com/topic/engineering/",
    "https://blog.janestreet.com/",
    "https://www.hudsonrivertrading.com/hrtbeat/",
    "https://engineering.monzo.com/",
    "https://www.starlingbank.com/blog/tags/engineering/",
    "https://tink.com/blog/engineering/",
    "https://engineering.braintreepayments.com/",
    "https://engineering.gocardless.com/",
    "https://blog.checkout.com/engineering",
    "https://medium.com/better-engineering",
    "https://medium.com/life-at-chime/tagged/engineering-at-chime",
    "https://medium.com/sofi-engineering",
    "https://medium.com/blend-eng",
    "https://canva.dev/blog/engineering/",
    "https://blog.datadoghq.com/engineering/",
    "https://engineering.vercel.com/",
    "https://about.sourcegraph.com/blog/tags/engineering",
    "https://developers.googleblog.com/",
    "https://aws.amazon.com/blogs/aws/",
    "https://cloud.google.com/blog/topics/developers-practitioners",
    "https://azure.microsoft.com/en-us/blog/tag/engineering/",
    "https://devblogs.microsoft.com/",
    "https://openai.com/blog",
    "https://dropbox.tech/",
    "https://engineering.atlassian.com/",
    "https://eng.uber.com/",
    "https://shopify.engineering/",
    "https://engineering.gusto.com/",
    "https://eng.lyft.com/",
    "https://www.intuit.com/blog/engineering/",
    "https://medium.com/snap-engineering",
    "https://developer.nvidia.com/blog/",
    "https://engineering.tiktok.com/blog",
    "https://engineering.asana.com/",
    "https://blog.cloudflare.com/tag/engineering/"
])


def _abs(base, href):
    if not href:                  # shouldn’t happen because we filter for links
        return base
    if href.startswith("//"):
        href = f"{urlparse(base).scheme}:{href}"
    if not href.startswith("http"):
        href = urljoin(base, href)
    return href

def scrape_headings(url, session=None, limit=None):
    session  = session or requests.Session()
    soup     = BeautifulSoup(session.get(url, timeout=10).content, "html.parser")
    results  = []

    for lvl in range(1, 5):                                # h1‑h4
        for h in soup.find_all(f"h{lvl}"):
            a = h if h.name == "a" else h.find_parent("a") # heading itself or wrapped by <a>
            if not (a and a.get("href")):                  # only keep true links
                continue
            title = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
            if title:
                results.append({"title": title, "link": _abs(url, a["href"])})
                if limit and len(results) >= limit:
                    return results
    return results

def scrape_all(blogs=BLOG_URLS, limit_per_site=20):
    session, articles = requests.Session(), []
    for b in blogs:
        try:
            articles.extend(scrape_headings(b, session, limit_per_site))
        except Exception as e:
            print(f"⚠️  {b}: {e}")
    # dedupe by link
    seen, uniq = set(), []
    for art in articles:
        if art["link"] not in seen:
            seen.add(art["link"]); uniq.append(art)
    return uniq



if __name__ == '__main__':
    # Scrape all blogs
    articles = scrape_all(blogs=BLOG_URLS)

    unique_articles = {a['link']: a for a in articles}.values()

    # Compose email content
    email_subject = "Your Medium Tech Blog Digest"
    email_body = "Here are the latest articles from your favorite Medium blogs:\n\n"

    for idx, article in enumerate(unique_articles, 1):
        email_body += f"{idx}. {article['title']}\n{article['link']}\n\n"

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
