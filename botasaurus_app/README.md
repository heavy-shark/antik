# Botasaurus Desktop App

A standalone desktop application for browser automation with visual profile management.

## Features

### 🎯 Profile Management
- Create multiple browser profiles
- Each profile maintains:
  - Cookies and sessions
  - Login states
  - Browser fingerprints
  - localStorage/sessionStorage
- Delete profiles when no longer needed
- View profile details and statistics

### 🚀 Web Scraping
- Scrape any website using Chrome automation
- Choose visible or headless mode
- Real-time log output
- Anti-bot detection built-in

### 📊 Results Viewer
- View all scraped data in a table
- Export results to JSON
- Clear results when needed

## How to Run

```bash
cd C:\Users\daniel\Desktop\hysk.pro\antik\botasaurus_app
python app.py
```

## Requirements

Already installed in your environment:
- Python 3.12
- PySide6
- Botasaurus
- botasaurus-driver

## Usage Guide

### Step 1: Create a Profile

1. Go to "Profiles" tab
2. Click "➕ Create New Profile"
3. Enter a profile name (e.g., "google-account", "facebook-profile")
4. Add optional description
5. Click OK

### Step 2: Run Scraper

1. Go to "Run Scraper" tab
2. Select your profile from dropdown
3. Enter target URL
4. Choose browser mode (Visible/Headless)
5. Click "▶️ Run Scraper"

### Step 3: View Results

1. Results automatically appear in "Results" tab
2. View scraped data in table format
3. Export to JSON if needed

## Profile Storage

Profiles are stored in:
```
%USERPROFILE%\.botasaurus\profiles\
```

Each profile has its own isolated browser environment.

## Tips

- **Staying logged in**: Run scraper in visible mode, manually log into the website, and the profile will remember your session
- **Multiple accounts**: Create separate profiles for different accounts
- **Testing**: Use visible mode to see what the browser is doing
- **Production**: Use headless mode for faster scraping

## NO LOCALHOST REQUIRED

This is a **standalone desktop application** - no web servers, no localhost, no port 3000. Just run and use!
