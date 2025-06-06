# modules for file handling, JSON parsing, and text processing
import os
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt') # download for the use of word_tokenize
nltk.download('stopwords') # download for the use of the standard list of stopwords

# declare and initialize constants
SCRAPED_FOLDER = "Scraped_Pages"
INDEX_FILE = "inverted_index.json"

comparison_count = 0 # perfromance analysis: global counter to keep track of the number of comparisons made during query evaluation

# helper function to preprocess the query text the same as the text files to ensure matching with the index occurs
def preprocess_query(text):
    text = text.lower() # convert the text to lowercase
    tokens = word_tokenize(text) # split the text into individual words/tokens
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words] # remove common words (stopwords) that do not add much meaning. Like 'i', 'the', 'and', etc.
    tokens = [re.sub(r'\W+', '', t) for t in tokens if t] # uses regular expression substitution to remove any non-word characters from the tokens. Replaces the character with an empty string.
    tokens = [t for t in tokens if len(t) > 1] # filters out any tokens that are 1 char long or shorter, as they are likely not meaningful for search purposes
    return tokens

# load the inverted index. If the file doesn't exist, prompt the user to run the index building script first
def load_index():
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(f"Missing index file: {INDEX_FILE}. Run build_index first to build it.")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# helper function for the search engine which applies the boolean logic specified in the user query and keeps track of the number of comparisons made
def apply_operator(op, a, b=None): # takes a  representing the operator ('AND', 'OR', 'NOT'), a set of document names (results from a search term) or two sets of document names (results from two search terms for AND/OR operations)
    global comparison_count
    if op in {'AND', 'and'}:
        comparison_count += len(a) * len(b)
        return a & b
    elif op in {'OR', 'or'}:
        comparison_count += len(a) + len(b)
        return a | b
    elif op in {'NOT', 'not'}:
        comparison_count += len(a)
        return all_docs - a

# The main function that evaluates the user query against the inverted index
def evaluate_query(query, index):
    global comparison_count, all_docs
    comparison_count = 0 # reset comparison count to 0 for each new query
    tokens = query.split() # splits the query into individual tokens (words). Including the search terms and operators 'AND', 'OR', 'NOT'
    result_stack = [] # will hold the set of document names that match the query
    operator_stack = [] # will hold the operators ('AND', 'OR', 'NOT') as they are encountered in the query

    # get every docuemnt name that is in the inverted index, so we can use it for NOT operations in queries
    all_docs = set()
    for doclist in index.values(): # iterate through all the lists of documents for each term in the index
        all_docs.update(doclist) # update the set of all documents with the documents from the current term

    i = 0
    while i < len(tokens): # loop through each token/word in the query
        token = tokens[i].upper() # convert the token to uppercase to handle case insensitivity
        
        if token in {'AND', 'OR'}:  # if the token is an operator, push it onto the operator stack
            operator_stack.append(token)
        elif token == 'NOT':
            i += 1 # we want to point to the term after NOT since that's the term to negate
            next_token = tokens[i] # get the term to negate
            processed = preprocess_query(next_token) # process the term to ensure it matches the index format
            if processed: # ensure term is not empty after having been processed
                # look up the processed term in the inverted index, convert the document list where that term exists to a set to perform set operations
                # apply the NOT operator to the term to get returned the documents that do NOT have the term
                # lastly, push the resulting document set to the result stack
                result_stack.append(apply_operator('NOT', set(index.get(processed[0], []))))
        else: # the token/word is not an operator but a search term
            processed = preprocess_query(token) # process the search term to ensure it matches the index format
            if processed: # ensure term is not empty after having been processed
                # look up the processed term in the inverted index, convert the document list where that term exists to a set to perform set operations
                # push the document set onto the result stack
                result_stack.append(set(index.get(processed[0], [])))
        i += 1 # move to next term in the query

        # apply the operators ('AND', 'OR') if we have two operands and one operator
        while len(result_stack) >= 2 and operator_stack: # run while there are at least two terms and at least one operator
            b = result_stack.pop()
            a = result_stack.pop()
            op = operator_stack.pop()
            result_stack.append(apply_operator(op, a, b)) # apply the operator to the two terms and push the resulting set of documents back onto the result stack

    return result_stack[0] if result_stack else set() # returns the set of documents that match the query, or an empty set if no matches were found

def main():
    # get the inverted index from the file
    try:
        index = load_index()
    except FileNotFoundError as e:
        print(e)
        return

    print("Search Engine Ready. Type 'exit' to quit.")
    # infinite loop for the user to repeatedly enter search queries
    while True:
        query = input("\nQuery: ").strip() # get the user input and remove leading and trailing whitespace
        if query.lower() == 'exit': # if the user types 'exit', break the loop and exit the program
            print("Exiting.")
            break
        results = evaluate_query(query, index) # evaluate the query against the inverted index
        print(f"Documents matched: {len(results)}")
        print(f"Minimum comparisons performed: {comparison_count}")
        if results: # print the matching documents if any were found
            print("Matched Files:")
            for doc in sorted(results):
                print("-", doc)
        else:
            print("No matching documents found.")

if __name__ == "__main__":
    main()
