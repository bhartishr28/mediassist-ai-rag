from pubmed import PubMedRetriever
from chroma_manager import ChromaManager

pmids = PubMedRetriever.search_pubmed_articles(
    "intermittent fasting obesity",
    max_results=10
)

print("PMIDs:")
print(pmids)

print("Number of PMIDs:", len(pmids))

# Get article details
articles = PubMedRetriever.fetch_pubmed_abstracts(pmids)

print("\nNumber of articles:", len(articles))

# Print the first article
# print("\nFirst article:")
# print(articles[0])

manager = ChromaManager()

for article in articles:
    manager.add_article(article)
    print("Added article:", article["pmid"])

print("\nTotal number of articles in ChromaDb:", manager.count_articles())

results = manager.retrieve_article("effects of intermittent fasting on obesity", n_results=3)

print("\nRetrieved articles:")
print(results)