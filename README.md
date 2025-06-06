# wikipedia_crawler_and_search
A Python-based mini search engine that performs Wikipedia web scraping, inverted index construction, and Boolean query evaluation. Built as part of a course project for CP423 – Text Retrieval &amp; Search Engine.

Overview
This project implements a small-scale text-based search engine that supports Boolean queries (AND, OR, NOT). It consists of three stages:
1. Web Scraping: Collects and cleans Wikipedia pages.
2. Indexing: Builds an inverted index from the collected text.
3. Query Engine: Supports and evaluates Boolean queries over the indexed documents.

Contents
- scraper.py: Recursively scrapes and extracts clean text from Wikipedia.
- build_index.py: Processes the text and constructs an inverted index.
- query_engine.py: Supports user queries and evaluates Boolean logic over the index.
- Scraped_Pages/: Folder containing all the extracted and cleaned .txt pages.
- inverted_index.json: The inverted index saved in JSON format.

Dependencies
- Python 3.x
- nltk
- requests
- beautifulsoup4
To install dependencies:
pip install nltk requests beautifulsoup4
Note: If you run into an issue running the project due to NLTK imports, ensure you are using the correct Python version (preferably Python 3.8–3.11).
NLTK data requirements (downloaded automatically in scripts):
- punkt
- stopwords

Execution Instructions
Step 1: Scrape Wikipedia Pages
python scraper.py
- Starts from the historical population page of Canadian provinces.
- Recursively visits up to 3 levels deep (with a limit of 5 links per page).
- Saves cleaned text into Scraped_Pages/.
Step 2: Build Inverted Index
python build_index.py
- Reads all .txt files from Scraped_Pages/.
- Applies preprocessing (lowercasing, stopword removal, etc.).
- Saves inverted_index.json.
Step 3: Run the Query Engine
python query_engine.py
- Loads the inverted index.
- Accepts queries such as:
- ontario AND quebec
- canada OR NOT alberta
- Displays:
- Number of matching documents
- Minimum number of comparisons performed
- Matching filenames
Type 'exit' to quit the search engine.

Preprocessing Steps
Each document and query term goes through the following:
1. Lowercasing
2. Tokenization using nltk.word_tokenize
3. Stop word removal using NLTK's English stopword list
4. Removal of non-alphanumeric characters
5. Removal of tokens with 1 or less characters

Evaluation Metrics
- Documents Matched: Number of .txt files satisfying the Boolean query.
- Minimum Comparisons: Approximate number of set operations performed during query evaluation (used for performance insight).

Assumptions
- Wikipedia pages are considered relevant if their URL matches /wiki/ and does not contain a colon : (to exclude meta/content pages).
- Only the first 5 valid article links per page are followed to control scraping scope.
- Redundant link revisits are avoided using a visited_urls set.
- An assumption I made from the Question 1 requirements is that Step 7 ("apply the same filtering and limit") means to limit the hyperlinks extracted from internal pages to 5 links as well.

Notes
- Ensure that Scraped_Pages/ contains files before building the index.
- If inverted_index.json is missing, the query engine will prompt you to run the index builder first.
- Scripts are modular and can be extended to support parentheses or query optimization.
