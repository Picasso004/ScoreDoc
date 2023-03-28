import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader
nltk.download('punkt')
nltk.download("stopwords")
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

class Tokenizer:
    """to turn words from text into tokens"""
    def extract_text(self,file : str):
        """to extract text any text file"""
        if file.endswith(".txt"):
            with open(file, 'r') as text_file:
                text = text_file.read()
            return text
        elif file.endswith(".pdf"):
            pdf_file = open(file, 'rb')
            pdf_reader = PdfReader(pdf_file)
            text = ''
            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()
            pdf_file.close()
            return text
        else:
            print("File format not supported")
            return None

    def get_tokens(self,text : str):
        "stop words removal and lemmatization"
        #Extracting text
        text = self.extract_text(text)
        if(text):
            # tokenize words
            result = word_tokenize(text)

            # Removal of stop words
            stop_words = set(stopwords.words("english"))
            tokenized_words = [word for word in result if word.casefold() not in stop_words]

            # Create WordNetLemmatizer object
            wnl = WordNetLemmatizer()
            pos_tagged_words = nltk.pos_tag(tokenized_words)


            # lemmatize each word based on its part-of-speech tag
            lemmatized_words = []
            for word, pos in pos_tagged_words:
                if pos.startswith('J'):
                    lemmatized_word = wnl.lemmatize(word, pos='a')
                elif pos.startswith('V'):
                    lemmatized_word = wnl.lemmatize(word, pos='v')
                elif pos.startswith('N'):
                    lemmatized_word = wnl.lemmatize(word, pos='n')
                elif pos.startswith('R'):
                    lemmatized_word = wnl.lemmatize(word, pos='r')
                else:
                    lemmatized_word = word
                lemmatized_words.append(lemmatized_word)
            for i in range(len(tokenized_words)):
                print(tokenized_words[i] + "-->" + lemmatized_words[i])
            return None



tokenizer = Tokenizer()
print(tokenizer.get_tokens("..\Docs samples\Sample Text.pdf"))
