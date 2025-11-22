from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_function():
    embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004")
    return embeddings