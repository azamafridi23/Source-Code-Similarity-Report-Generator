# Import necessary modules
from flask import Flask, render_template, request
import difflib
import tokenize
from io import BytesIO

# Create a Flask web application instance
app = Flask(__name__)

# Function to calculate similarity between two code snippets


def calculate_similarity(*codes):
    # Split the code into words for each snippet
    words_list = [code.split() for code in codes]

    print(f'len of w_l = {len(words_list)} \n w_l = {words_list}')

    # Initialize lists to store diff results for each pair of snippets
    all_diffs = []
    similarity_ratios = []
    same_words = []
    different_words1 = []
    different_words2 = []
    # Use difflib to compare the words and calculate similarity ratio

    # Iterate through pairs of snippets
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            d = difflib.Differ()
            diff = list(d.compare(words_list[i], words_list[j]))
            print(f'diff = {diff}')
            all_diffs.append(diff)
            similarity_ratio = 1 - sum(1 for word in diff if word.startswith('- ')
                                       ) / max(len(words_list[i]), len(words_list[j]))
            similarity_ratios.append(similarity_ratio)
            same_words.append([word[2:]
                              for word in diff if word.startswith('  ')])
            different_words1.append([word[2:]
                                    for word in diff if word.startswith('- ')])
            different_words2.append([word[2:]
                                    for word in diff if word.startswith('+ ')])

    print(f"sim_ratio = {similarity_ratios}\n")
    print(f"same_words = {same_words}\n")
    print(f"diff_w1 = {different_words1}\n")
    return similarity_ratios, same_words, different_words1, different_words2

# Function to generate tokens from code


def generate_tokens(code):
    tokens = []
    # Tokenize the code excluding string tokens
    for tok in tokenize.tokenize(BytesIO(code.encode('utf-8')).readline):
        if tok.type != tokenize.STRING:
            tokens.append(tok)
    return tokens

# Function to compare tokens and count shared tokens


def compare_tokens(*tokens_lists):
    shared_tokens_count = 0
    shared_tokens = []
    # Iterate through pairs of token lists
    for i in range(len(tokens_lists)):
        for j in range(i + 1, len(tokens_lists)):
            # Compare tokens for each pair
            shared_tokens.extend([tok1.string for tok1, tok2 in zip(
                tokens_lists[i], tokens_lists[j]) if tok1.string == tok2.string])
    shared_tokens_count = len(shared_tokens)
    print(f"len of shared_tok = {shared_tokens_count}")
    print(f"shared_tok = {shared_tokens}")
    return shared_tokens_count, shared_tokens

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
        if len(files) < 2:
            raise ValueError("Please upload only two files.")

        # Read code from the files
        codes = [file.read().decode('utf-8') for file in files]

        # Call the final comparison model function
        word_similarity, token_similarity, shared_tokens = final_model_gr(
            *codes)

        print(f'word_similarity = {word_similarity}\n')

        print(f'token_sim = {token_similarity}\n')

        print(f'shared_tokens = {shared_tokens}')

        # Determine if the similarity indicates plagiarism
        # is_plagiarism = word_similarity > 0.60

        formated_word_sim_for_print = [
            f'{word*100:.2f}%' for word in word_similarity]
        result = {
            'word_similarity': formated_word_sim_for_print,
            'token_similarity': token_similarity,
            'shared_tokens': shared_tokens,
            'is_plagiarism': True
        }

        print("noooo")
    except Exception as e:
        # Handle exceptions and store the error message
        print('went in error')
        result = {'error': str(e)}

    # Render the result on the web page
    return render_template('index.html', result=result)


# Run the Flask application if this script is executed
if __name__ == '__main__':
    app.run(debug=True)