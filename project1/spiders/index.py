import math
from collections import defaultdict, Counter
from utils import filter_word


# Singleton class to hold an word index to apply query searches
# Weighting is done using: ltc.ltc
class Index(object):
    def __init__(self, docs, titles, titles_tokenized, urls):
        self.docs = docs
        self.titles = titles
        self.titles_tokenized = titles_tokenized
        self.urls = urls
        # Counter of doc frequencies of each word
        self.doc_frequencies = self.create_doc_frequencies(self.docs)
        self.idf = self.create_idf(self.docs, self.doc_frequencies)
        self.index = self.create_normalized_index(self.docs)
        # Thesaurus used for query expansion
        self.thesaurus = {
            'beautiful': ['nice', 'fancy'],
            'chapter': ['chpt'],
            'chpt': ['chapter'],
            'responsible': ['owner', 'accountable'],
            'freemanmoore': ['freeman', 'moore'],
            'dept': ['department'],
            'brown': ['beige',	'tan', 'auburn'],
            'tues': ['Tuesday'],
            'sole': ['owner', 'single', 'shoe', 'boot'],
            'homework': ['hmwk', 'home', 'work'],
            'novel': ['book', 'unique'],
            'computer': ['cse'],
            'story': ['novel', 'book'],
            'hocuspocus': ['magic',	'abracadabra'],
            'thisworks': ['this', 'work'],
        }

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

    def get_logarithmic_tf(self, original_tf):
        return 1 + math.log(original_tf, 10)

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
                # Get logarithmic tf and the multiply by idf to get weight
                curr_word_weight_tf_idf = self.get_logarithmic_tf(
                    doc_tf_idf_weights[word]) * self.idf[word]
                doc_tf_idf_weights[word] = curr_word_weight_tf_idf
                srqt_sum += curr_word_weight_tf_idf ** 2

            # Get sqrt of sum of weights to calculate cosine normalization
            srqt_sum = math.sqrt(srqt_sum)

            # Create the final index
            for word in doc_tf_idf_weights.keys():
                final_index[word].append(
                    [i, doc_tf_idf_weights[word] / srqt_sum])
        return final_index

    # Create normalized vector of query terms
    def create_query_vector(self, query):
        final_vector = {}
        srqt_sum = float(0)
        # Get unique words by document and iterate them
        query_tf_idf_weights = dict(Counter(query))
        for word in query_tf_idf_weights.keys():
            # Get logarithmic tf and the multiply by idf to get weight
            curr_word_weight_tf_idf = self.get_logarithmic_tf(
                query_tf_idf_weights[word]) * self.idf[word]
            query_tf_idf_weights[word] = curr_word_weight_tf_idf
            srqt_sum += curr_word_weight_tf_idf ** 2

        # Get sqrt of sum of weights to calculate cosine normalization
        srqt_sum = math.sqrt(srqt_sum)

        # Create the final index
        for word in query_tf_idf_weights.keys():
            # Prevent a division by zero when word doesn't exist
            if query_tf_idf_weights[word] <= 0:
                continue
            final_vector[word] = query_tf_idf_weights[word] / srqt_sum

        return final_vector

    def create_query_tokens(self, query):
        query_tokens = []
        for word in query.split():
            new_token = filter_word(word)
            if new_token:
                query_tokens.append(new_token)
        return query_tokens

    def get_query_similarities(self, query_vector, index, titles_tokenized):
        scores = defaultdict(int)
        touched_docs = []
        for query_term, query_weight in query_vector.items():
            for doc_id, doc_weight in index[query_term]:
                final_sum = query_weight * doc_weight
                # Add .25 whenever a query token appears on it's title, but only once per document
                if query_term in titles_tokenized[doc_id] and not doc_id in touched_docs:
                    final_sum += 0.25
                    touched_docs.append(doc_id)
                # Add sum to document's count
                scores[doc_id] += final_sum
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def search(self, query):
        # This list will hold the final results
        formatted_results = []
        # Top k results to be returned as result
        top_k = 6
        # Get tokenized version of query
        query_tokens = self.create_query_tokens(query)
        # Obtain a vector from query to compare with docs
        query_vector = self.create_query_vector(query_tokens)
        # Apply cosine similarity between query and docs
        results = self.get_query_similarities(
            query_vector, self.index, self.titles_tokenized)
        # If few results are returned, rerun query with query expansion
        if len(results) < top_k / 2:
            print 'init', results
            for word in query.split():
                # Verify if lowercase query term exists in our thesaurus
                if word.lower() in self.thesaurus:
                    # Add each synonim with the correct format to possibly match other terms
                    for thesaurus_term in self.thesaurus[word.lower()]:
                        query_tokens.append(filter_word(thesaurus_term))
            # Re-obtain query vector and apply similarities again
            query_vector = self.create_query_vector(query_tokens)
            results = self.get_query_similarities(
                query_vector, self.index, self.titles_tokenized)
        for result in results[:top_k]:
            [curr_doc_id, curr_result] = result
            formatted_results.append(
                (curr_doc_id, curr_result, self.urls[curr_doc_id], self.titles[curr_doc_id], self.docs[curr_doc_id][:20]))
        return formatted_results

    def get_doc_frequencies(self):
        return self.doc_frequencies

    def get_index(self):
        return self.index
