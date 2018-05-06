import math
from collections import defaultdict, Counter
from utils import filter_word


# Singleton class to hold an word index to apply query searches
class Index(object):
    def __init__(self, docs):
        self.docs = docs
        # Counter of doc frequencies of each word
        self.doc_frequencies = self.create_doc_frequencies(self.docs)
        self.idf = self.create_idf(self.docs, self.doc_frequencies)
        self.index = self.create_normalized_index(self.docs)

    # Create a list of document frequency of each word
    def create_doc_frequencies(self, docs):
        docs_unique = []
        word_count = Counter()
        # Create a list of all unique words in each document
        for doc_words in docs:
            docs_unique += set(doc_words)
        # Count each word as it represent the apparence in one document
        for word in docs_unique:
            word_count[word] += 1
        return word_count

    def create_idf(self, docs, doc_frequencies):
        idf = defaultdict(int)
        total_docs = float(len(docs))

        # Create idf for each term
        for word in doc_frequencies.keys():
            idf[word] = math.log((total_docs / doc_frequencies[word]), 10)

        return idf

    # Create an index, where each term contains a list of [doc_id, normalized]
    # Ex: {'cse': [[0, 0.123], [1, 0.051], [2, 0.103], [5, 0.107], [6, 0.099], [8, 0.111], [12, 0.140], [16, 0.167]]}
    def create_normalized_index(self, docs):
        final_index = defaultdict(list)

        # Iterate over each doc
        for i in range(0, len(docs)):
            srqt_sum = float(0)
            # Get unique words by document and iterate them
            doc_tf_idf_weights = dict(Counter(docs[i]))
            for word in doc_tf_idf_weights.keys():
                # Get logarithmic td and the multiply by idf to get weight
                curr_word_weight_tf_idf = (
                    1 + math.log(doc_tf_idf_weights[word], 10)) * self.idf[word]
                doc_tf_idf_weights[word] = curr_word_weight_tf_idf
                srqt_sum += curr_word_weight_tf_idf ** 2

            # Get sqrt of sum of weights to calculate cosine normalization
            srqt_sum = math.sqrt(srqt_sum)

            # Create the final index
            for key in doc_tf_idf_weights.keys():
                final_index[key].append(
                    [i, doc_tf_idf_weights[key] / srqt_sum])
        return final_index

    def search(self, query):
        query_tokens = []
        for word in query.split():
            new_token = filter_word(word)
            if new_token:
                query_tokens.append(new_token)
        return query_tokens

    def get_doc_frequencies(self):
        return self.doc_frequencies

    def get_index(self):
        return self.index