from groq import Groq
import os
from dotenv import load_dotenv
from chroma_manager import ChromaManager

load_dotenv()

chroma=ChromaManager()

# Get Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError( "GROQ_API_KEY is not configured. " "Add it to your .env file locally or " "to Streamlit Cloud Secrets when deployed." )

client = Groq(api_key=groq_api_key)

def generate_response(context,query):
    prompt = f""" 
    You are MediAssit AI, a healthcare research assistant.
Use the context below to answer the user's question.

Context: 
    {context}
Question:   
    {query}

Instructions: 
- Answer based on the provided context.
- Do not make up information.
- If the context does not contain enough information,
  say that there is not enough evidence in the retrieved
  documents.
- Give a clear and concise answer.
Answer:
"""

    response = client.chat.completions.create(
        model= "openai/gpt-oss-120b",temperature=0.2,
        messages = [{
            "role":"user",
            "content": prompt,
        }]
    )
    return response.choices[0].message.content



# # Test data
# context = """
# A systematic review examined intermittent fasting and metabolic health.
# The review found that intermittent fasting may improve some metabolic
# outcomes, but the effects can vary depending on the fasting method and
# individual characteristics.
# """
if __name__ == "__main__":
    query = "Can intermittent fasting improve metabolic health?"

    # Query ChromaDB
    results = chroma.retrieve_article(query, n_results=3)

    # Extract retrieved documents
    documents = results["documents"][0]

    # Create context
    context = "\n\n".join(documents)

    # Generate answer using Groq
    answer = generate_response(context, query)

    # Display answer
    print("\nDisplay Answer:\n", answer)
