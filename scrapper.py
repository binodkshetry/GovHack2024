import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL to scrape
base_url = "https://www.homeaffairs.gov.au/research-and-statistics/research"


# Function to scrape a single page
def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.content, "html.parser")

        # Get page title
        title = soup.find("title").text.strip() if soup.find("title") else "No Title"

        # Get main content
        content = ""
        content_div = soup.find("div", class_="research-content")  # Main content
        if content_div:
            content = content_div.get_text(strip=True)

        # Get sticky menu links
        sticky_menu = soup.find("div", class_="left-menu-sticky")
        sticky_links = []
        if sticky_menu:
            for link in sticky_menu.find_all("a"):
                sticky_links.append((link.text.strip(), urljoin(url, link["href"])))

        # Get level-3 menu links
        level_3_links = []
        level_3_menu = soup.find_all("li", class_="level-3")
        for item in level_3_menu:
            link = item.find("a")
            if link and link.has_attr("href"):
                level_3_links.append((link.text.strip(), urljoin(url, link["href"])))

        return title, url, sticky_links, level_3_links, content
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None, None, [], [], ""


# Function to recursively scrape pages
def scrape_website(start_url):
    to_scrape = [start_url]
    scraped = set()
    all_data = []

    while to_scrape:
        current_url = to_scrape.pop(0)

        if current_url in scraped:
            continue

        title, url, sticky_links, level_3_links, content = scrape_page(current_url)

        if title and url:
            all_data.append((title, url, "Main Content", "", content))
            scraped.add(current_url)

        # Add sticky links to the list of URLs to scrape
        for sticky_item in sticky_links:
            sticky_title, sticky_url = sticky_item
            if sticky_url not in scraped and sticky_url not in to_scrape:
                to_scrape.append(sticky_url)

        # Add level-3 links to the list of URLs to scrape
        for level_3_item in level_3_links:
            level_3_title, level_3_url = level_3_item
            if level_3_url not in scraped and level_3_url not in to_scrape:
                to_scrape.append(level_3_url)

    return all_data


# Start scraping from the base URL
scraped_data = scrape_website(base_url)

# Save data to CSV
with open("home_affairs_research.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Page Title", "URL", "Menu Type", "Menu Link", "Content"])
    writer.writerows(scraped_data)

print("Data saved to home_affairs_research.csv")