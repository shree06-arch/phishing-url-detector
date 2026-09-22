"""
generate_sample_data.py

Generates a synthetic-but-realistic labeled dataset of legitimate and
phishing-style URLs so the project runs end-to-end out of the box,
with NO external downloads required.

This is a bootstrap/demo dataset, not a research-grade one. For real
results, replace data/urls.csv with a public dataset such as:
  - PhishTank (https://phishtank.org/developer_info.php)
  - OpenPhish (https://openphish.com/)
  - UCI Phishing Websites Dataset
  - Kaggle "Phishing Site URLs" dataset
See README.md for how to plug in real data.
"""

import csv
import random

random.seed(42)

LEGIT_DOMAINS = [
    "github.com", "google.com", "wikipedia.org", "amazon.com", "nytimes.com",
    "stackoverflow.com", "reddit.com", "microsoft.com", "apple.com", "bbc.com",
    "python.org", "linkedin.com", "spotify.com", "netflix.com", "dropbox.com",
    "airbnb.com", "yahoo.com", "cnn.com", "espn.com", "twitch.tv",
    "medium.com", "wordpress.com", "shopify.com", "salesforce.com", "adobe.com",
    "paypal.com", "wellsfargo.com", "chase.com", "bankofamerica.com", "instagram.com",
]

LEGIT_PATHS = [
    "/", "/about", "/docs/getting-started", "/blog/2024/updates",
    "/products/laptop", "/user/settings", "/help/faq", "/search?q=weather",
    "/news/world", "/watch?v=abc123", "/article/12345", "/store/checkout",
    "/api/v2/users", "/careers", "/contact-us",
]

PHISH_BRANDS = [
    "paypal", "amazon", "apple", "microsoft", "netflix", "facebook",
    "instagram", "chase", "wellsfargo", "bankofamerica", "google", "ebay",
]

PHISH_KEYWORDS = [
    "login", "verify", "secure", "update", "confirm", "signin",
    "account", "suspended", "unlock", "billing", "recover", "alert",
]

SUSPICIOUS_TLDS = ["tk", "ml", "ga", "cf", "gq", "xyz", "top", "info", "club", "click"]

SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "is.gd", "rb.gy"]


def random_hex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def gen_legit_url():
    domain = random.choice(LEGIT_DOMAINS)
    path = random.choice(LEGIT_PATHS)
    scheme = "https"
    use_www = random.random() < 0.4
    host = f"www.{domain}" if use_www else domain
    if random.random() < 0.15:
        path += f"?ref={random_hex(6)}"
    return f"{scheme}://{host}{path}"


def gen_phishing_url():
    brand = random.choice(PHISH_BRANDS)
    keyword = random.choice(PHISH_KEYWORDS)
    style = random.random()

    if style < 0.25:
        # brand as subdomain of a random-looking domain
        tld = random.choice(SUSPICIOUS_TLDS)
        host = f"{brand}-{keyword}.{random_hex(6)}.{tld}"
        url = f"http://{host}/{keyword}.php?id={random.randint(1000,9999)}"
    elif style < 0.45:
        # IP address host
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        url = f"http://{ip}/{brand}/{keyword}/index.html"
    elif style < 0.65:
        # shortened URL
        short = random.choice(SHORTENERS)
        url = f"http://{short}/{random_hex(7)}"
    elif style < 0.85:
        # long confusing hyphenated host with suspicious tld
        tld = random.choice(SUSPICIOUS_TLDS)
        host = f"{brand}-{keyword}-{random.choice(['secure','online','account'])}.{tld}"
        url = f"https://{host}/{keyword}/{random_hex(4)}?token={random_hex(10)}"
    else:
        # @ symbol trick (browser ignores everything before @)
        fake_host = f"{brand}.com"
        real_host = f"{random_hex(8)}.{random.choice(SUSPICIOUS_TLDS)}"
        url = f"http://{fake_host}@{real_host}/{keyword}"

    return url


def build_dataset(n_legit=600, n_phish=600):
    rows = []
    seen = set()
    while len([r for r in rows if r[1] == 0]) < n_legit:
        u = gen_legit_url()
        if u not in seen:
            seen.add(u)
            rows.append((u, 0))
    while len([r for r in rows if r[1] == 1]) < n_phish:
        u = gen_phishing_url()
        if u not in seen:
            seen.add(u)
            rows.append((u, 1))
    random.shuffle(rows)
    return rows


def main():
    rows = build_dataset()
    out_path = "data/urls.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])  # label: 1 = phishing, 0 = legitimate
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"  legitimate: {sum(1 for r in rows if r[1] == 0)}")
    print(f"  phishing:   {sum(1 for r in rows if r[1] == 1)}")


if __name__ == "__main__":
    main()
