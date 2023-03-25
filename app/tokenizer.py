import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from PyPDF2 import PdfReader

class Tokenizer:
    """to turn words from text into tokens"""
    def extract_text(self,file : str):
        """to remove stop words from any text file"""
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
        result = self.extract_text(text)
        nltk.download('punkt')
        nltk.download("stopwords")
        stop_words = set(stopwords.words("english"))
        result = word_tokenize(result)
        return [word for word in result if word.casefold() not in stop_words]


tokenizer = Tokenizer()
print(tokenizer.get_tokens("..\Docs samples\pdf-sample.pdf"))
