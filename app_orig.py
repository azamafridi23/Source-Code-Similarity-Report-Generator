# Import necessary modules
from flask import Flask, render_template, request
import difflib
import tokenize
from io import BytesIO

# Create a Flask web application instance
app = Flask(__name__)

# Function to calculate similarity between two code snippets


def calculate_similarity(code1, code2):
    # Split the code into words
    words1 = code1.split()
    words2 = code2.split()

    # Use difflib to compare the words and calculate similarity ratio
    d = difflib.Differ()
    diff = list(d.compare(words1, words2))
    print(f'diff = {diff}')
    similarity_ratio = 1 - \
        sum(1 for word in diff if word.startswith(
            '- ')) / max(len(words1), len(words2))

    # Extract same, different words for analysis
    same_words = [word[2:] for word in diff if word.startswith('  ')]
    different_words1 = [word[2:] for word in diff if word.startswith('- ')]
    different_words2 = [word[2:] for word in diff if word.startswith('+ ')]

    print(f"sim_ratio = {similarity_ratio}\n")
    print(f"same_words = {same_words}\n")
    print(f"diff_w1 = {different_words1}\n")
    return similarity_ratio, same_words, different_words1, different_words2

# Function to generate tokens from code


def generate_tokens(code):
    tokens = []
    # Tokenize the code excluding string tokens
    for tok in tokenize.tokenize(BytesIO(code.encode('utf-8')).readline):
        if tok.type != tokenize.STRING:
            tokens.append(tok)
    return tokens

# Function to compare tokens and count shared tokens


def compare_tokens(tokens1, tokens2):
    shared_tokens = [tok1.string for tok1, tok2 in zip(
        tokens1, tokens2) if tok1.string == tok2.string]

    print(f"len of shared_tok = {len(shared_tokens)}")
    print(f"shared_tok = {shared_tokens}")
    return len(shared_tokens), shared_tokens

# Function to format shared tokens as a string


def format_shared_tokens(shared_tokens):
    return '---'.join(shared_tokens)

# Main function for the final comparison model


def final_model_gr(*codes):
    # Calculate word-based similarity
    word_similarity, _, _, _ = calculate_similarity(*codes)

    # Generate and compare tokens for token-based similarity
    tokens_list = [generate_tokens(code) for code in codes]
    shared_tokens_count, shared_tokens = compare_tokens(*tokens_list)
    formatted_shared_tokens = format_shared_tokens(shared_tokens)

    print("\nToken-Based Comparison:")

    return word_similarity, shared_tokens_count, formatted_shared_tokens

# Route for the home page


@app.route('/')
def index():
    return render_template('index.html', result=None)

# Route for handling code comparison request


@app.route('/compare_code', methods=['POST'])
def compare_code():
    try:
        # Get uploaded files from the request
        files = request.files.getlist('files[]')

        # Check if exactly two files are uploaded
        if len(files) != 2:
            raise ValueError("Please upload only two files.")

        # Read code from the files
        codes = [file.read().decode('utf-8') for file in files]

        # Call the final comparison model function
        word_similarity, token_similarity, shared_tokens = final_model_gr(
            *codes)

        # Determine if the similarity indicates plagiarism
        is_plagiarism = word_similarity > 0.60

        result = {
            'word_similarity': f'{word_similarity*100:.2f}%',
            'token_similarity': token_similarity,
            'shared_tokens': shared_tokens,
            'is_plagiarism': is_plagiarism
        }
    except Exception as e:
        # Handle exceptions and store the error message
        result = {'error': str(e)}

    # Render the result on the web page
    return render_template('index.html', result=result)


# Run the Flask application if this script is executed
if __name__ == '__main__':
    app.run(debug=True)


"""
diff = ["+ '''", '+ for', '+ Postgre', "+ sql'''", '  import', '- sqlite3', '+ psycopg2', '  conn', '  =', 


len of shared_tok = 4
shared_tok = ['utf-8', '\r\n', ')', '\r\n']

"""
