from index_class import Index


def get_title(title):
    if not title:
        return 'No title found'
    return title


def start_search_engine(words, titles, titles_tokenized, urls):
    main_index = Index(words, titles, titles_tokenized, urls)
    print "The search engine was initialized with the following clusters\n"
    for leader, followers in main_index.get_clusters().items():
        print "Leader:", leader, "Followers:", ', '.join(str(x) for x in followers)
    query = str(raw_input("Please input a query (Type 'stop' to quit)\n\n"))
    while query != "stop":
        results = main_index.search(query)
        for index, result in enumerate(results):
            (_, resulting_score, url, title, preview) = result
            print "Result:", index + 1, "Result score:", resulting_score
            print "Url:", url, "Title:", get_title(title)
            print "First 20 words:", " ,".join(preview)
            print "***********************************************************\n"
        query = str(raw_input("Please input a query (Type 'stop' to quit)\n\n"))
