import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader
'''nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')'''

class TextProcessor:
    """to turn words from text into tokens"""
    def __init__(self):
        self.text = ""
        self.processed_text = []
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
        print(self.processed_text)
    def get_most_relevant_words(self,words):
        score = dict()
        for word in self.processed_text:
            if word.lower() in [w.lower() for w in words]:
                if word in score.keys():
                    score[word] += 1
                else:
                    score[word] = 1
        #Sorting the result in descending order
        score = dict(sorted(score.items(), key=lambda item: item[1], reverse=True))
        return score



test = TextProcessor()
test.extract_text("..\Docs samples\who-rights-roles-respon-hw-covid-19.pdf")
test.tokenize()
test.lemmatize()
print(test.get_most_relevant_words(['covid','disease','rights']))

