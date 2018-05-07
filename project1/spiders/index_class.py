import math
from copy import deepcopy
from random import randint
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
        # Create leader follower clusters
        self.k_leaders = 5
        self.leader_follower_cluster = self.create_leader_follower_cluster(
            self.docs, self.index, len(self.docs), self.k_leaders)
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

    def get_random_leaders(self, docs, docs_number, k_leaders):
        # Randomly get k leaders indexes and their content
        leader_indexes = []
        for _ in range(0, k_leaders):
            curr_rand = randint(0, docs_number - 1)
            while curr_rand in leader_indexes:
                curr_rand = randint(0, docs_number - 1)
            leader_indexes.append(curr_rand)
        return leader_indexes

    def get_vector_by_doc_id(self, index, doc_id, doc_words):
        result_vector = {}
        for word in doc_words:
            for curr_doc_id, curr_doc_weight in index[word]:
                if curr_doc_id == doc_id:
                    result_vector[word] = curr_doc_weight
        return result_vector

    def update_follwers_similarities(self, index, leader_id, leader_vector, followers_list, leader_indexes):
        # Iterate over each term of leader's doc
        for leader_term, leader_weight in leader_vector.items():
            # Iterate over each document that contains current word
            for doc_id, doc_weight in index[leader_term]:
                # Filter other leaders
                if doc_id in leader_indexes:
                    continue
                # Increase similarity between this document and the current leader
                followers_list[doc_id][leader_id] += leader_weight * doc_weight
        # Return modified list of follwers's similarities
        return followers_list

    def get_followers(self, leader_indexes, docs_number):
        followers_list = []
        for i in range(0, docs_number):
            if not i in leader_indexes:
                followers_list.append(i)
        return followers_list

    def add_follower_to_leader_cluster(self, follower_id, assigned_leader_id, final_clusters, leaders_followers_count, available_leaders, cluster_capacity):
        final_clusters[assigned_leader_id].append(follower_id)
        leaders_followers_count[assigned_leader_id] += 1
        if leaders_followers_count[assigned_leader_id] == cluster_capacity:
            available_leaders.remove(assigned_leader_id)

    def add_unassigned_follower_to_random_leader(self, follower_id, final_clusters, leaders_followers_count, available_leaders, cluster_capacity, leader_indexes):
        # If there are available leaders, add current follower to first available
        if len(available_leaders):
            self.add_follower_to_leader_cluster(
                follower_id, available_leaders[0], final_clusters, leaders_followers_count, available_leaders, cluster_capacity)
        # If all clusters are full (because k-leaders is not multiple of number of docs), randomly assign a leader
        else:
            final_clusters[leader_indexes[randint(
                0, len(leader_indexes) - 1)]].append(follower_id)

    def get_final_clusters(self, followers_list, leader_indexes, docs_number, k_leaders):
        final_clusters = defaultdict(list)
        pending_followers = self.get_followers(leader_indexes, docs_number)
        # Dictionary to hold how many followers each leader has
        leaders_followers_count = defaultdict(int)
        # List leaders that are still accepting followers
        available_leaders = deepcopy(leader_indexes)
        # Cluster capacity based on document number and number of leaders
        cluster_capacity = (docs_number - k_leaders) / k_leaders
        # Iterate over each follower
        for follower_id, follower_leaders in followers_list.items():
            # Sort follower leader's in descending order
            closest_leaders = sorted(
                follower_leaders.items(), key=lambda x: x[1], reverse=True)
            assigned = False
            # Iterate over each leader to see if he still accepts follwers
            for assigned_leader_id, _ in closest_leaders:
                # Verify if leader still accepts followers
                if assigned_leader_id in available_leaders:
                    self.add_follower_to_leader_cluster(
                        follower_id, assigned_leader_id, final_clusters, leaders_followers_count, available_leaders, cluster_capacity)
                    assigned = True
                    break
            # The following applies if follower didn't find any leader
            if not assigned:
                self.add_unassigned_follower_to_random_leader(
                    follower_id, final_clusters, leaders_followers_count, available_leaders, cluster_capacity, leader_indexes)
            pending_followers.remove(follower_id)
        # If any document has 0 similarity with all leaders, we need to assign it somewhere
        for follower_id in pending_followers:
            self.add_unassigned_follower_to_random_leader(
                follower_id, final_clusters, leaders_followers_count, available_leaders, cluster_capacity, leader_indexes)

        return final_clusters

    def create_leader_follower_cluster(self, docs, index, docs_number, k_leaders):
        leader_indexes = self.get_random_leaders(
            docs, docs_number, k_leaders)
        # This will hold the similarity between each follwer with all the leaders
        followers_list = defaultdict(lambda: defaultdict(int))
        for leader_id in leader_indexes:
            curr_leader_vector = self.get_vector_by_doc_id(
                index, leader_id, docs[leader_id])
            followers_list = self.update_follwers_similarities(
                index, leader_id, curr_leader_vector, followers_list, leader_indexes)
        final_clusters = self.get_final_clusters(
            followers_list, leader_indexes, docs_number, k_leaders)
        return final_clusters

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

    def get_clusters(self):
        return self.leader_follower_cluster
