# 🎣 Phishing URL Detector

A machine learning project that classifies URLs as **phishing** or
**legitimate** using purely lexical/structural features of the URL string
(no page content is fetched, so it's fast and safe to run on unverified
links).

Includes:
- Feature engineering from raw URLs (25 features)
- A `RandomForestClassifier` trained with scikit-learn
- A CLI tool for one-off checks
- A small Flask web app with a form + JSON API
- Unit tests for the feature extractor

## How it works

For a given URL, `src/features.py` extracts signals commonly associated
with phishing links, such as:

- Presence of an IP address instead of a domain name
- Use of URL shorteners (bit.ly, tinyurl, etc.)
- Suspicious keywords (`login`, `verify`, `secure`, `account`, ...)
- Brand names appearing outside their real domain (e.g. `paypal` in a
  subdomain of a non-PayPal domain)
- `@` symbol tricks, excessive hyphens/digits, missing HTTPS
- Shannon entropy of the hostname/path (randomized-looking strings)
- URL/host/path length, subdomain count, etc.

These features are fed into a Random Forest classifier that outputs a
phishing probability.

## Project structure

```
phishing-url-detector/
├── app.py                    # Flask web demo
├── requirements.txt
├── data/
│   └── urls.csv               # Labeled dataset (url, label)
├── models/
│   └── model.joblib            # Trained model (generated, gitignored)
├── src/
│   ├── features.py             # URL feature extraction
│   ├── generate_sample_data.py # Builds the bundled demo dataset
│   ├── train.py                # Trains + evaluates the model
│   └── predict.py              # CLI prediction tool
├── templates/
│   └── index.html              # Web UI
└── tests/
    └── test_features.py        # Unit tests
```

## Quickstart

```bash
git clone https://github.com/<your-username>/phishing-url-detector.git
cd phishing-url-detector
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt

# 1. Generate the bundled demo dataset (or bring your own, see below)
python src/generate_sample_data.py

# 2. Train the model
python src/train.py

# 3. Check a URL from the command line
python src/predict.py "http://paypal-verify-account.tk/login.php?id=123"

# 4. Or run the web demo
python app.py
# then open http://localhost:5000
```

### API usage

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://secure-login-paypal.xyz/account"}'
```

## ⚠️ About the bundled dataset

`data/urls.csv` is a **synthetically generated demo dataset** (see
`src/generate_sample_data.py`) built from rule-based templates, so the
project runs immediately with no downloads or API keys. Because the
patterns are template-generated, the model scores near-perfect accuracy
on it — that's a property of the synthetic data being cleanly separable,
**not** a claim of real-world performance.

For a real evaluation, swap in an actual labeled dataset, for example:

| Source | Notes |
|---|---|
| [PhishTank](https://phishtank.org/developer_info.php) | Free API, community-verified phishing URLs |
| [OpenPhish](https://openphish.com/) | Free feed of active phishing URLs |
| [UCI Phishing Websites Dataset](https://archive.ics.uci.edu/dataset/327/phishing+websites) | Classic benchmark dataset |
| [Kaggle: Phishing Site URLs](https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls) | Large labeled CSV |

Just replace `data/urls.csv` with a two-column `url,label` file
(`label` = 1 for phishing, 0 for legitimate) and re-run `src/train.py` —
no other code changes needed.

## Extending this project

Ideas if you want to take this further:
- Add WHOIS/domain-age lookups and SSL certificate metadata as features
- Add a browser extension or email-gateway plugin front-end
- Try gradient boosting (XGBoost/LightGBM) or a character-level CNN/LSTM
- Add SHAP explanations to the web UI so predictions are interpretable
- Set up a scheduled job to retrain on a live PhishTank/OpenPhish feed

## Disclaimer

This is an educational/demo project, not a production security product.
Don't rely on it as your only line of defense against phishing.

## License

MIT — see [LICENSE](LICENSE).
