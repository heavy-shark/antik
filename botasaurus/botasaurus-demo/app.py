"""
Botasaurus Server with Web UI

This script launches a web interface at http://localhost:3000
where you can:
- Run scrapers with different inputs
- View results in a nice table
- Manage browser profiles
- Export data to CSV/JSON/Excel
"""

from botasaurus_server import Server
from scraper import scrape_heading, scrape_simple

# Create the server
Server.configure(
    title="My Scraper Dashboard",
    header_title="Web Scraping Dashboard",
    description="Scrape websites with browser profiles and caching",
    right_header={
        "text": "Powered by Botasaurus",
        "link": "https://github.com/omkarcloud/botasaurus"
    }
)

# Add your scrapers to the server
Server.add_scraper(scrape_heading)
Server.add_scraper(scrape_simple)

# Start the server - opens browser automatically
if __name__ == "__main__":
    from botasaurus_server.run import run
    run()
