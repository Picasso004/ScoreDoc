from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk,os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader
'''nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')'''


app = Flask("Finder")
CORS(app)

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Receive files
    for i in range(len(request.files)):
        file = request.files[f"file{i}"]
        file.save('media/uploads/' + file.filename)
    #file = request.files['file']
    # Handle the file upload here, e.g., save the file to a directory
    # and return a response to the client
    # Example: saving the file to a directory named 'uploads'
    #file.save('media/uploads/' + file.filename)
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/api/data', methods=['POST'])
def receive_data():
    # Access the keywords using 'request.form'
    keywords = request.json['keywords']
    final_results = []
    for filename in os.listdir("media/uploads"):
        f = os.path.join("media/uploads", filename)
        processor = TextProcessor(f)
        result = processor.get_most_relevant_words(keywords)
        final_results.append({'file': filename, 'value': result})
        os.remove(f)

    return jsonify(final_results)


class TextProcessor:
    def __init__(self,file : str):
        self.extract_text(file)
        self.processed_text = []
        self.tokenize()
        self.lemmatize()

    def extract_text(self,file : str):
        """to extract text any text file"""
        if file.endswith(".txt"):
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
        "stop words removal and tokenization lemmatization"
        if(self.text != None):
            # tokenize words
            result = word_tokenize(self.text)

            # Removal of stop words
            stop_words = set(stopwords.words("english") + ['.',',',';',':','-','(',')','•'])
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

    def get_most_relevant_words(self,words):
        score = {f'{word}': 0 for word in words}
        for word in self.processed_text:
            if word.lower() in [w.lower() for w in words]:
                score[word] += 1

        #Sorting the result in descending order
        result = sorted(score.items(), key=lambda item: item[1], reverse=True)
        result = [{'word': word, 'score': score} for word, score in result]
        return result


if __name__ =="__main__":
    app.run("localhost", 6969)