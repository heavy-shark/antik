from botasaurus.browser import browser, Driver
from botasaurus.request import request, Request

@browser(
    profile="my-profile",  # Creates a persistent browser profile
    cache=True
)
def scrape_heading(driver: Driver, data):
    """
    Scrapes the main heading from a given URL using a browser.
    This function uses browser profiles which save cookies, localStorage, etc.
    """
    driver.get(data)

    # Wait for page to load
    driver.sleep(2)

    heading = driver.get_text("h1")

    return {
        "url": data,
        "heading": heading,
        "title": driver.title
    }


@request(cache=True)
def scrape_simple(request: Request, data):
    """
    A simpler HTTP request-based scraper.
    Use this for APIs or simple pages without JavaScript.
    """
    response = request.get(data)
    soup = response.soup

    heading = soup.find("h1")
    title = soup.find("title")

    return {
        "url": data,
        "heading": heading.text if heading else "No heading found",
        "title": title.text if title else "No title found"
    }


if __name__ == "__main__":
    # Test the scraper
    result = scrape_heading("https://www.omkar.cloud/")
    print(result)
