from defaults import words, titles, titles_tokenized, info, urls
from index import Index

main_index = Index(words, titles, titles_tokenized, urls)
print main_index.search('CSE team Freeman Moore')
