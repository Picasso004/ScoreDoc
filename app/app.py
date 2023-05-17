from . config import Config
import webbrowser
import nltk, os, math
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader

print("Loading...")

nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
@app.route('/')
def hello():
    # This function returns a simple string when the root route is accessed
    return "Hello, World!"

@app.route('/scoredoc')
def serve_scoredoc():
    # This function serves the scoredoc.html template when the route /scoredoc is accessed
    return render_template('scoredoc.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    This function handles the file upload. It first removes all existing txt and pdf files in the upload directory.
    Then it saves the files received from the POST request in the upload directory.
    """
    # Empty upload folder:
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads'):
        if file.endswith("txt") or file.endswith("pdf"):
            f = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads/', file)
            os.remove(f)
    # Receive files
    for i in range(len(request.files)):
        file = request.files[f"file{i}"]
        file.save(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads/' + file.filename)
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/api/data', methods=['POST'])
def receive_data():
    """
    This function receives the keywords from a POST request, processes each file in the upload directory
    by tokenizing, removing stop words, lemmatizing and calculating the score for each keyword in the file.
    It then calculates the TF-IDF score for each file and returns the data as a JSON response.
    """
    # Access the keywords using 'request.form'
    keywords = request.json['keywords']
    processor = TextProcessor()
    data = []
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads'):
        if filename.endswith("txt") or filename.endswith("pdf"):
            f = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads/', filename)
            processor.set_file(f)
            process_result = processor.get_most_relevant_words(keywords)
            data.append({'file': filename, 'len': processor.file_len(), 'data': process_result})
            os.remove(f)

    data = processor.calculate_tf_idf(data)
    return jsonify(data)

class TextProcessor:
    """
    This is the TextProcessor class that is used to perform text processing tasks such as tokenization,
    removal of stop words, lemmatization, and calculating the score for each keyword in a file.
    """
    def __init__(self, file: str = None):
        # This is the constructor method that initializes the text and processed_text attributes.
        self.text = None
        if file:
            self.set_file(file)
        self.processed_text = []

    def set_file(self, file):
        """
        This method sets the file for the TextProcessor object.
        It calls the extract_text, tokenize, and lemmatize methods to perform text processing tasks.
        """
        if os.path.exists(file):
            self.extract_text(file)
            self.tokenize()
            self.lemmatize()

    def file_len(self):
        # This method returns the length of the text attribute.
        return len(self.text)

    def extract_text(self, file: str):
        """
        This method extracts the text from the file.
        If the file is a text file, it reads the text directly.
        If the file is a PDF, it uses the PyPDF2 library to extract the text.
        """
        if not os.path.exists(file):
            return None
        elif file.endswith(".txt"):
            with open(file, 'r') as text_file:
                text = text_file.read()
            self.text = text
        elif file.endswith(".pdf"):
            pdf_file = open(file, 'rb')
            pdf_reader = PdfReader(pdf_file)
            text = ''
            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()
            pdf_file.close()
            self.text = text
        else:
            print("File format not supported")
            self.text = None

    def tokenize(self):
        """
        This method tokenizes the text and removes stop words.
        It uses the nltk library for tokenization and stop word removal.
        """
        if self.text is not None:
            # tokenize words
            result = word_tokenize(self.text)

            # Removal of stop words
            stop_words = set(stopwords.words("english") + ['.', ',', ';', ':', '-', '(', ')', '•'])
            self.processed_text = [word for word in result if word.casefold() not in stop_words]

    def lemmatize(self):
        """
        This method lemmatizes the tokenized text.
        It uses the nltk library for lemmatization.
        """
        # Create WordNetLemmatizer object
        wnl = WordNetLemmatizer()
        pos_tagged_words = nltk.pos_tag(self.processed_text)

        # lemmatize each word based on its part-of-speech tag
        lemmatized_words = []
        for word, pos in pos_tagged_words:
            if pos.startswith('J'):
                lemmatized_word = wnl.lemmatize(word, pos='a')
            elif pos.startswith('V'):
                lemmatized_word = wnl.lemmatize(word, pos='v').lower()
            elif pos.startswith('N'):
                lemmatized_word = wnl.lemmatize(word, pos='n').lower()
            elif pos.startswith('R'):
                lemmatized_word = wnl.lemmatize(word, pos='r').lower()
            else:
                lemmatized_word = word.lower()
            lemmatized_words.append(lemmatized_word)

        self.processed_text = lemmatized_words

    def get_most_relevant_words(self, words):
        """
        This method calculates the score for each keyword in the processed text.
        The score is the number of occurrences of the keyword in the text.
        """
        score = {f'{word.lower()}': 0 for word in words}
        for word in self.processed_text:
            if word.lower() in [w.lower() for w in words]:
                score[word.lower()] += 1

        # Sorting the result in descending order
        result = sorted(score.items(), key=lambda item: item[1], reverse=True)
        result = [{'word': word, 'score': score} for word, score in result]
        return result

    def calculate_tf_idf(self, documents):
        """
        This method calculates the TF-IDF score for each document based on the keywords and scores.
        It calculates the term frequency (TF) and inverse document frequency (IDF) for each keyword,
        then multiplies them to get the TF-IDF score.
        """
        n = len(documents)
        df = {}
        for document in documents:
            for word in document['data']:
                keyword = word['word']
                if keyword not in df.keys():
                    df[keyword] = 0
                if word['score'] != 0:
                    df[keyword] += 1

        # Calculate TF-IDF score for each document
        for document in documents:
            tf_idf_sum = 0
            keywords = document['data']
            for keyword in keywords:
                tf = keyword['score'] / float(document['len'])
                if df[keyword['word']] == 0:
                    idf = 0
                else:
                    idf = math.log(n / float(df[keyword['word']]))
                tf_idf = tf * idf
                tf_idf_sum += tf_idf
            document['tf_idf'] = tf_idf_sum

        return sorted(documents, key=lambda x: x['tf_idf'], reverse=True)


def main():
    """
    This is the main function that starts the Flask application.
    It first opens the web browser with the /scoredoc route and then starts the Flask server.
    """
    url = f"http://{app.config['HOST']}:{app.config['PORT']}/scoredoc"
    webbrowser.open(url)
    app.run(app.config['HOST'], app.config['PORT'])
