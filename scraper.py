import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os 

# declare and initialize constants
BASE_URL = 'https://en.wikipedia.org'
START_URL = 'https://en.wikipedia.org/wiki/List_of_Canadian_provinces_and_territories_by_historical_population'
MAX_LINKS = 5 # limit to the first 5 valid article links
EXCLUDED_HEADERS = ["See also", "References", "Bibliography", "Further reading"]
visited_urls = set()

os.makedirs('Scraped_Pages', exist_ok=True)  # create output folder directory if it doesn't exist to store the text files for each scraped and cleaned wikipedia page

# Task 1: Retrieve raw HTML content
def retrieve_html(url):
    """Retrieve raw HTML content from a URL."""
    try:
        print(f"Retrieving HTML from {url}") # print message to console to indicate process to retrieve URL data is taking place
        response = requests.get(url, timeout=10)  # set a timeout to avoid hanging indefinitely
        response.raise_for_status()  # from the previous step, if the server does not repsond within the 10 sec timeout, then the error will be caught here
        return response.text # if no exception is raised, then the HTML content is returned as string
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return None


def clean_html(html):
    """Parse HTML content and return only the relevant content from the page."""
    # Task 2: Parse HTML into a structured Python object
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', {'id': 'mw-content-text'}) # search parsed HTML for the main content div element which often has the ID 'mw-content-text'
    if not content:
        print("No content found in the HTML.")
        return "", []

    # Task 3: Identify and extract the relevant data, excluding unwanted elements
    for tag in content(['table', 'style', 'script', 'nav', 'footer']): # loop through parsed HTML and remove unwanted tags
        tag.decompose() # delete the tag and all its contents from the page

    excluded = [h.lower() for h in EXCLUDED_HEADERS] # convert headings to lowercase just for safe practice

    
    headings = content.find_all(['h2', 'h3', 'h4']) # find all heading tags (h2, h3, h4) in the content
    for header in headings:
        header_text = header.get_text(strip=True).lower() # get the text of the header, stripping leading and trailing whitespace
        if any(ex in header_text for ex in excluded): # check if the header text matches any of the excluded headers
            container = header
            if header.parent and header.parent.name == 'div' and 'mw-heading' in header.parent.get('class', []): # check if the header is wrapped in a div with class 'mw-heading
                container = header.parent # if yes, set the container to the parent div

            # remove all following siblings until the next actual heading. This is to remove all contetn within the heading block
            next_siblings = list(container.next_siblings)
            for sibling in next_siblings:
                if isinstance(sibling, str): # if the sibling is a string (text node), skip it
                    continue
                if sibling.find(['h2', 'h3', 'h4']): # if the sibling contains a new heading (even wrapped), stop
                    break
                if sibling.name in ['h2', 'h3', 'h4']: # stop if the sibling itself is a new heading
                    break
                sibling.decompose() 
            container.decompose()  # lastly, remove the header itself

    # Task 4: Extract all relevant text content from the page and save it
    text = content.get_text(separator=' ', strip=True) # extract the text, ignoring all HTML tags, and join with a space. And remove leading and trailing whitespace.

    # Task 5: Extract first 5 vaild article links
    links = []
    for a in content.find_all('a', href=True): # itterate through all anchor tags with href attributes (hyperlinks)
        href = a['href'] # extrcat the URL from the href attribute
        if href.startswith('/wiki/') and ':' not in href: # check if link is a wikipedia page, exlcuding pages with colons (which are typically not articles)
            full_url = urljoin(BASE_URL, href) # convert the relative path into a full URL using urljoin
            if full_url not in visited_urls and full_url not in links: # if the link has not already been saved
                links.append(full_url) # add the full URL to the links list for further crawling in later steps
        if len(links) >= MAX_LINKS: # stop the loop after collecting 5 valid links
            break

    return text, links # return the extracted and cleaned text, and the list of links to be crawled next


# Task 6 and 7: Recursively scrape pages up to a depth of 3
def scrape_page(url, filename_prefix, depth):
    """Recursively scrape a page and its linked pages up to depth=3."""
    if depth > 3 or url in visited_urls:  # stop if max depth is reached or URL has already been visited
        return
    
    html = retrieve_html(url)  # retrieve the HTML content from the URL
    if not html:  # if HTML retrieval failed, return
        return
    
    text, links = clean_html(html)  # clean the HTML and extract text and links

    # Task 9: Save and organize all relevant textual content systematically
    filename = f'Scraped_Pages/{filename_prefix}_depth_{depth}.txt' # save the cleaned text to the folder we created previously with a unique filename based on the prefix and depth level
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    
    print(f"Saved content from {url} to {filename}") # print message to console to indicate the content has been saved successfully

    # Task 8: Maintain a set of visited URLs to avoid revisiting
    visited_urls.add(url)  # mark the URL as visited to avoid revisiting it

    # recursively scrape each link found on the page
    for i, link in enumerate(links): # enumerate iterates through the links and provides an index (i) for each link
        scrape_page(link, f"{filename_prefix}_link{i+1}", depth + 1) # appends _link1, _link2, etc. to the filename prefix for each link to get a unique filename at that depth level

# start the scraping process from the initial URL
def main():
    print("Starting web scraping...")
    scrape_page(START_URL, "initial_page", 1)  # start scraping from the initial URL with depth 1
    print("Web scraping completed.")


if __name__ == "__main__":
    main()  # run the main function to start the scraping process