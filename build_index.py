import os
import re
import nltk
import json
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

# set path to folder containing scraped text files
SCRAPED_FOLDER = "Scraped_Pages"

# preprocessing function
def preprocess_text(text):
    # Step 1: Lowercase
    text = text.lower()
    # Step 2: Tokenize
    tokens = word_tokenize(text)
    # Step 3: Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    # Step 4: Remove non-alphanumeric characters
    tokens = [re.sub(r'\W+', '', token) for token in tokens]
    tokens = [token for token in tokens if token]  # remove empty strings
    # Step 5: Eliminate singly occurring characters
    tokens = [token for token in tokens if len(token) > 1]
    return tokens

# Step 6: Build inverted index
def build_inverted_index(folder_path):
    inverted_index = defaultdict(set) # initialize a dictionary to hold the inverted index, set the default value of each term/token to an empty set. This way we can map a term/token to a set of filenames where it appears.
    for filename in os.listdir(folder_path): # iterate through all files in the folder
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename) # get the full path of the file
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_text = file.read()
                tokens = preprocess_text(raw_text) # get the preprocessed terms/tokens from the text
                # for each term/token add the filename to the set in the inverted index pertaining to that token. Beacuse that token appears in that file.
                for token in set(tokens):
                    inverted_index[token].add(filename)
    return inverted_index

inverted_index = build_inverted_index(SCRAPED_FOLDER) # call method to build the inverted index from the scraped text files

# save the inverted index to a JSON file
with open("inverted_index.json", "w", encoding="utf-8") as f:
    json.dump({k: list(v) for k, v in inverted_index.items()}, f, indent=2)
