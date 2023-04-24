import webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import nltk, os, math
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader

print("Loading...")

nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

app = Flask("Finder")
CORS(app)
@app.route('/')
def hello():
    return "Hello, World!"


@app.route('/finder')
def serve_finder():
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))
    return send_from_directory(frontend_dir, 'finder.html')


# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Receive files
    for i in range(len(request.files)):
        file = request.files[f"file{i}"]
        file.save(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads/' + file.filename)
    return jsonify({'message': 'File uploaded successfully'})


@app.route('/api/data', methods=['POST'])
def receive_data():
    # Access the keywords using 'request.form'
    keywords = request.json['keywords']
    processor = TextProcessor()
    data = []
    print(os.curdir)
    for filename in os.listdir(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads'):
        f = os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/media/uploads/', filename)
        processor.set_file(f)
        process_result = processor.get_most_relevant_words(keywords)
        data.append({'file': filename, 'len': processor.file_len(), 'data': process_result})
        os.remove(f)

    data = processor.calculate_tf_idf(data)
    return jsonify(data)


class TextProcessor:
    def __init__(self, file: str = None):
        self.text = None
        if file:
            self.set_file(file)
        self.processed_text = []

    def set_file(self, file):
        if os.path.exists(file):
            self.extract_text(file)
            self.tokenize()
            self.lemmatize()

    def file_len(self):
        return len(self.text)

    def extract_text(self, file: str):
        """to extract text any text file"""
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
        """stop words removal and tokenization lemmatization"""
        if self.text is not None:
            # tokenize words
            result = word_tokenize(self.text)

            # Removal of stop words
            stop_words = set(stopwords.words("english") + ['.', ',', ';', ':', '-', '(', ')', '•'])
            self.processed_text = [word for word in result if word.casefold() not in stop_words]

    def lemmatize(self):
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
        Calculates TF-IDF score for each document based on the keywords and scores provided.

        Args:
        - documents (list): List of dictionaries representing documents, with 'file' and 'data' keys.
                           'file' (str): File name of the document.
                           'data' (list): List of dictionaries representing keywords and scores.
                                         'word' (str): Keyword.
                                         'score' (int): Score for the keyword.

        Returns:
        - list: List of dictionaries representing documents with additional 'tf_idf' key containing TF-IDF score.
               'file' (str): File name of the document.
               'data' (list): List of dictionaries representing keywords and scores.
                             'word' (str): Keyword.
                             'score' (int): Score for the keyword.
               'tf_idf' (float): TF-IDF score for the document.
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
    url = "http://localhost:6969/finder"
    webbrowser.open(url)
    app.run("localhost", 6969)


if __name__ == "__main__":
    main()
