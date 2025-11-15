# Botasaurus Web Scraper Demo

A simple web scraping dashboard with browser profile management.

## Features

- **Browser Profile Management**: Automatically saves cookies, localStorage, and sessions
- **Web UI Dashboard**: Beautiful interface to run scrapers
- **Caching**: Avoid re-scraping the same data
- **Export**: Download results as CSV, JSON, or Excel

## How to Run

1. Install botasaurus-server:
```bash
python -m pip install botasaurus-server
```

2. Run the app:
```bash
python app.py
```

3. Open your browser at: http://localhost:3000

## What are Profiles?

Browser profiles in Botasaurus save:
- Cookies and sessions
- localStorage and sessionStorage
- Browser fingerprint
- Login states

This is useful for:
- Staying logged into websites
- Avoiding repeated CAPTCHAs
- Maintaining consistent browser fingerprints
