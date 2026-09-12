import streamlit as st

from pubmed import PubMedRetriever
from chroma_manager import ChromaManager
from rag import generate_response


# Create objects
pubmed = PubMedRetriever()
chroma = ChromaManager()

if "search_results" not in st.session_state:
    st.session_state.search_results = []

# if "selected_articles" not in st.session_state:
#     st.session_state.selected_articles = []

def search_pubmed():

    with st.sidebar:

        st.header("🔎 Search PubMed")

        search_term = st.text_input(
            "Enter a research topic"
        )

        max_results = st.slider(
            "Number of articles",
            5,
            20,
            10
        )

        if st.button("Search PubMed"):

            if not search_term.strip():

                st.warning("Please enter a search topic.")

            else:

                with st.spinner("Searching PubMed..."):

                    pmid_list = PubMedRetriever.search_pubmed_articles(
                        search_term,
                        max_results
                    )

                    articles = PubMedRetriever.fetch_pubmed_abstracts(
                        pmid_list
                    )

                    st.session_state.search_results = articles



# -------------------------------
# Display Search Results
# -------------------------------

def display_search_results():

    with st.sidebar:

        if st.session_state.search_results:

            st.divider()

            st.subheader("📚 Search Results")

            for article in st.session_state.search_results:

                st.checkbox(
                    article["title"],
                    key=f"article_{article['pmid']}"
                )

# -------------------------------
# Ingest Articles
# -------------------------------

def ingest_articles():

    with st.sidebar:

        if st.session_state.search_results:

            if st.button(
                "📥 Ingest Selected Articles",
                use_container_width=True
            ):

                selected_articles = []

                # Check which articles were selected
                for article in st.session_state.search_results:

                    selected = st.session_state.get(
                        f"article_{article['pmid']}",
                        False
                    )

                    if selected:
                        selected_articles.append(article)

                # No articles selected
                if not selected_articles:

                    st.warning(
                        "Please select at least one article."
                    )

                    return

                # Ingest selected articles
                progress = st.progress(0)

                for i, article in enumerate(selected_articles):

                    try:

                        chroma.add_article(article)

                    except Exception as e:

                        st.error(
                            f"Error adding article "
                            f"{article['pmid']}: {e}"
                        )

                    progress.progress(
                        (i + 1) / len(selected_articles)
                    )

                st.success(
                    f"{len(selected_articles)} article(s) "
                    "added to the vector store."
                )
def clear_search_results():

    with st.sidebar:

        if st.session_state.search_results:

            if st.button(
                "🗑️ Clear Search Results",
                use_container_width=True
            ):

                st.session_state.search_results = []
                # st.session_state.selected_articles = []

                st.rerun()
# -------------------------------
# Ask Question
# -------------------------------

def ask_question():

    st.header("💬 Ask a Research Question")

    query = st.text_input(
        "Enter your question",
        placeholder="e.g. Can intermittent fasting improve type 2 diabetes?"
    )

    if st.button(
        "Ask MediAssist AI",
        type="primary"
    ):

        if not query.strip():

            st.warning(
                "Please enter a question."
            )

            return

        # Check whether documents exist
        if chroma.count_articles() == 0:

            st.warning(
                "No articles are available in the vector store. "
                "Please search PubMed and ingest articles first."
            )

            return

        try:

            # ------------------------------------------
            # Retrieve relevant documents from ChromaDB
            # ------------------------------------------

            with st.spinner(
                "Retrieving relevant research..."
            ):

                results = chroma.retrieve_article(
                    query,
                    n_results=3
                )

            documents = results["documents"][0]

            metadata = results["metadatas"][0]

            ids = results["ids"][0]


            # ------------------------------------------
            # Create context
            # ------------------------------------------

            context = "\n\n".join(documents)


            # ------------------------------------------
            # Generate answer using Groq
            # ------------------------------------------

            with st.spinner(
                "Generating answer..."
            ):

                answer = generate_response(
                    context,
                    query
                )


            # ------------------------------------------
            # Display answer
            # ------------------------------------------

            st.subheader("🤖 MediAssist AI Answer")

            st.write(answer)


            # ------------------------------------------
            # Display sources
            # ------------------------------------------

            st.subheader("📚 Retrieved Sources")

            for i in range(len(documents)):

                with st.expander(
                    f"Source {i + 1}: "
                    f"{metadata[i]['title']}"
                ):

                    st.write(
                        f"**PMID:** {ids[i]}"
                    )

                    st.write(
                        f"**Journal:** "
                        f"{metadata[i]['journal']}"
                    )

                    st.write(
                        f"**Publication Year:** "
                        f"{metadata[i]['publication_date']}"
                    )

                    st.write(
                        f"**Authors:** "
                        f"{metadata[i]['authors']}"
                    )

                    st.write(
                        "**Retrieved Abstract:**"
                    )

                    st.write(
                        documents[i]
                    )

        except Exception as e:

            st.error(
                f"Error while generating response: {e}"
            )


def main():
    st.set_page_config(
        page_title="MediAssist AI",
        page_icon="🩺",
        layout="wide"
    )

    st.title("🩺 MediAssist AI")

    st.write(
        "Search PubMed research, ingest relevant articles "
        "into the vector store, and ask questions based "
        "on the retrieved evidence."
    )

    # Sidebar
    search_pubmed()
    display_search_results()
    ingest_articles()
    clear_search_results()

    # Main area
    ask_question()

if __name__ == "__main__":
    main()