# Import necessary modules
from flask import Flask, render_template, request,json
import difflib
import tokenize
from io import BytesIO

# Create a Flask web application instance
app = Flask(__name__)

# Function to calculate similarity between two code snippets
filenames = []

final_list = []


def calculate_similarity(*codes):
    # Split the code into words for each snippet
    words_list = [code.split() for code in codes]

    # print(f'len of w_l = {len(words_list)} \n w_l = {words_list}')

    # Initialize lists to store diff results for each pair of snippets
    all_diffs = []
    similarity_ratios = {}
    same_words = []
    different_words1 = []
    different_words2 = []
    # Use difflib to compare the words and calculate similarity ratio

    # Iterate through pairs of snippets
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            d = difflib.Differ()
            diff = list(d.compare(words_list[i], words_list[j]))
            # print(f'diff = {diff}')
            all_diffs.append(diff)
            similarity_ratio = 1 - sum(1 for word in diff if word.startswith('- ')
                                       ) / max(len(words_list[i]), len(words_list[j]))

            # dict_name = f'file{i}-file{j}'
            dict_name = f'{filenames[i]} - {filenames[j]}'
            similarity_ratios[dict_name] = similarity_ratio
            # similarity_ratios.append(similarity_ratio)
            same_words.append([word[2:]
                              for word in diff if word.startswith('  ')])
            different_words1.append([word[2:]
                                    for word in diff if word.startswith('- ')])
            different_words2.append([word[2:]
                                    for word in diff if word.startswith('+ ')])

    # print(f"sim_ratio = {similarity_ratios}\n")
    # print(f"same_words = {same_words}\n")
    # print(f"diff_w1 = {different_words1}\n")
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
    shared_tokens_count = {}
    shared_tokens = {}
    # print(f"tokens_list = {tokens_lists}")
    # Iterate through pairs of token lists
    for i in range(len(tokens_lists)):
        for j in range(i + 1, len(tokens_lists)):
            # dict_name = f'file{i}-file{j}'
            dict_name = f"{filenames[i]} - {filenames[j]}"
            shared_tokens[dict_name] = [tok1.string for tok1, tok2 in zip(
                tokens_lists[i], tokens_lists[j]) if tok1.string == tok2.string]
            shared_tokens_count[dict_name] = len(shared_tokens[dict_name])

    # print(f"len of shared_tok = {shared_tokens_count}")
    # print(f"shared_tok = {shared_tokens}")
    return shared_tokens_count, shared_tokens

# Function to format shared tokens as a string


def format_shared_tokens(shared_tokens):
    formated_tokens_count = {}
    for key, val in shared_tokens.items():  # remove ',','\n','\r' and '\r\n' from the list
        shared_tokens[key] = [
            i for i in val if i not in [',', '\r\n', '\n', '\r']]
    # print(f'shared tokens = {shared_tokens}\n')
    formated_tokens = {}
    for key, val in shared_tokens.items():
        formated_tokens[key] = ', '.join(shared_tokens[key])
        formated_tokens_count[key] = len(val)
    # print(f'formated tokens = {formated_tokens}')
    # print(f"\n\nshared_tok by az = {shared_tokens}")
    # print(f"format tok by az= {formated_tokens}\n\n")
    return formated_tokens, formated_tokens_count


# Main function for the final comparison model


def final_model_gr(*codes):
    # Calculate word-based similarity
    word_similarity, _, _, _ = calculate_similarity(*codes)

    # Generate and compare tokens for token-based similarity
    tokens_list = [generate_tokens(code) for code in codes]
    shared_tokens_count, shared_tokens = compare_tokens(*tokens_list)
    formatted_shared_tokens, formated_tokens_count = format_shared_tokens(
        shared_tokens)

    # print("\nToken-Based Comparison:")

    return word_similarity, formated_tokens_count, formatted_shared_tokens

# Route for the home page


@app.route('/')
def index():
    return render_template('data_sheet2.html', final_list=[])


@app.route('/student/<row>/<row2>')
def student_page(row,row2):
    global final_list
    print(f"row = {row} and row2={row2}")
    for i in final_list:
        a1=i[1][0]
        a2 =i[1][3]
        print(f"a1 = {a1} and a2 = {a2}")
        print(f'i = {i}')
        if ((row==a1 and row2==a2) or (row2==a1 and row==a2)):
            print(f"a1 = {a1} and a2 = {a2}")
            print(f"row = {row} and row2={row2}")
            data = i[1]
            print("data = ",data)
            return render_template('index2.html', final_list=data)

    


# @app.route('/abc')
# def index2():
#     return render_template('index2.html', final_list=final_list)

# Route for handling code comparison request


@app.route('/compare_code', methods=['POST'])
def compare_code():
    global final_list, filenames

    try:
        # print("TRY RAN!")
        final_list = []
        filenames = []
        # Get uploaded files from the request
        files = request.files.getlist('files[]')
        # print(f"files = {files}")
        file_contents = {}
        for file in files:
            filenames.append(file.filename)  # global variable
            file_contents[file.filename] = file.read().decode('utf-8')
        # print(f'files = {filenames}')
        # Check if exactly two files are uploaded
        if len(files) < 2:
            raise ValueError("Please upload only two files.")

        codes = []
        for key, val in file_contents.items():
            codes.append(val)
        # # Read code from the files
        # codes = [file.read().decode('utf-8') for file in files]

        # Call the final comparison model function
        word_similarity, token_similarity, shared_tokens = final_model_gr(
            *codes)

        # print(f'word_similarity = {word_similarity}\n')

        # print(f'token_sim = {token_similarity}\n')

        # print(f'shared_tokens = {shared_tokens}')

        # Determine if the similarity indicates plagiarism
        is_plagiarism_dict = {}
        for key, val in word_similarity.items():
            if val > 0.60:
                is_plagiarism_dict[key] = True
            else:
                is_plagiarism_dict[key] = False

        for key, val in word_similarity.items():
            word_similarity[key] = f"{val*100:.2f}%"

        result = {
            'word_similarity': word_similarity,
            'token_similarity': token_similarity,
            'shared_tokens': shared_tokens,
            'is_plagiarism': is_plagiarism_dict
        }
        # print(f"Word_similarity_dict = {word_similarity}")
        # print(f'token_similarity = {token_similarity}')
        # print(f'shared_tokens = {shared_tokens}')
        # print(f'is_plagiarism = {is_plagiarism_dict}')
        myd2={}
        for key, value in word_similarity.items():
            temp_list = []
            a1, a2 = key.split(" - ")
            temp_list.append([
                a1, token_similarity[key], value, a2, shared_tokens[key], is_plagiarism_dict[key], file_contents[a1], file_contents[a2]])
            final_list.extend(temp_list)
        print("final list = ",final_list)
        modified_dict = {}

        for item in final_list:
            key = item[0]
            if key in modified_dict:
                modified_dict[key].append(item)
                myd2[key].append([item[0],item[3],item[1],float(item[2][:-1])])
            else:
                modified_dict[key] = [item]
                myd2[key] = [[item[0],item[3],item[1],float(item[2][:-1])]]
        counter=0
        for key, val_list in modified_dict.items():
            counter2 = 0
            for i in val_list:
                i.append(counter2)
                counter2 += 1
            modified_dict[key] = (counter,val_list)
            counter+=1
        print('mod_d = ',modified_dict)
        # print(modified_dict['db.py'])
        # print("mod dict = ",modified_dict.keys())
        for key,val_list in modified_dict.items():
            print("-----------------------")
            print("Key = ",key)
            print("Row = ",val_list[0])
            for i in val_list[1]:
                print(f"val0={i[0]} - val3={i[3]} - val8={i[8]}")
                
                
                

        final_list = [(index, item) for index, item in enumerate(final_list)]

        json_mod_dict = json.dumps(modified_dict)
        
                        
        print(f"Myd2 = {myd2}")
        myd2_json = json.dumps(myd2)
        print(f"Myd2 json = {myd2_json}")

        myd3 = {}
        for key, value in myd2.items():
            if key in myd3:
                myd3[key].extend(value)
            else:    
                myd3[key] = value
            # Iterate through the original list
            for sublist in value:
                # Create a new list with swapped elements
                new_sublist = [sublist[1], sublist[0], sublist[2], sublist[3]]
                # Append the new list to myd3 under the swapped key
                if sublist[1] not in myd3.keys():
                    myd3[sublist[1]] = []
                myd3[sublist[1]].append(new_sublist)

        print(f'\n\nmyd3 = {myd3}\n\n')
        myd3_json = json.dumps(myd3)
        
        # print(f"\n\n FINA LIST {final_list}")
        # print(f'len of FL = {len(final_list)}')

        # print(f'final list = {final_list}')
        # print(len(final_list))
        # print(f'codes = {codes}')
        # print(f'file = {file_contents}')
        # print(len(file_contents))
        
    except Exception as e:
        # Handle exceptions and store the error message
        # print('went in error and error is ', str(e))
        result = {'error': str(e)}

    # Render the result on the web page
    # print(f'len of FL = {len(final_list)}')
    return render_template('data_sheet3.html', final_list=final_list,modified_dict=modified_dict,json_mod_dict=json_mod_dict,myd2=myd3,myd2_json=myd3_json)


# Run the Flask application if this script is executed
if __name__ == '__main__':
    app.run(debug=True)
