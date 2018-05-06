import string
from nltk.corpus import stopwords
from nltk import PorterStemmer

stop_words = set(stopwords.words('english'))


# Lowecase term, filter stop words and stem final token
def filter_word(word):
    word = word.lower()
    # Filter tokens that don't start with letters
    # if not word or not word[0].isalpha():
    #     return None
    if not word:
        return None

    # If word ends with sign, remove it
    while word and word[-1] in string.punctuation:
        word = word[:-1]
    if not word:
        return None

    # Filter stop words
    if word in stop_words:
        return None

    # Apply Porter Stemmer to word and construct and return item
    return str(PorterStemmer().stem(word))
