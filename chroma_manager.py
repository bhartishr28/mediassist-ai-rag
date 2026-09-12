import chromadb

class ChromaManager:
    def __init__(self):

        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.client.get_or_create_collection(name="pubmed_articles")
        #print("Collection created successfully")

    def add_article(self, article):

        abstract_text = ""
        for section,text in article['abstract'].items():
            abstract_text += f"{section}: {text}\n"

    # store articles in chromadb
        self.collection.upsert(
        ids=[article["pmid"]],
        documents=[abstract_text],
        metadatas =[{"title": article['title'],
                     "journal": article["journal"],
                     "authors": article["authors"],
                     "publication_date": article["publication_date"]}]

    )

    def count_articles(self):
        return self.collection.count()

    def retrieve_article(self, query,n_results=3):
        results = self.collection.query(query_texts=query, n_results=n_results)
        return results