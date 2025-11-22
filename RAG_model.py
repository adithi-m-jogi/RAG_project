from langchain.text_splitters import RecursiveCharacterTextSplitter 
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.schema.document import Document 
from get_embedding_function import get_embedding_function
from voice_to_text import record_text
import shutil
from dotenv import load_dotenv

load_dotenv()
CHROMA_PATH="chroma"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
data_path = r"data"
#data_path=r"no_data"

def load_documents():
    document_loader = PyPDFDirectoryLoader(data_path)
    return document_loader.load()

#documents = load_documents()
#print(documents[0])

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def get_vector_store(text_chunks: list[Document]):
    embeddings=get_embedding_function()
    db=Chroma(
        persist_directory=CHROMA_PATH,embedding_function=embeddings)
    
    chunks_with_ids = calculate_chunk_ids(text_chunks)

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks,ids=new_chunk_ids)
    else:
        print("No newdocuments to add")

def calculate_chunk_ids(chunks):

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source =  chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"


        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def get_conversational_chain():
    #make sure to provide all the details
    prompt_template="""
    You are an expert assistant. Provide a detailed answer to the question based on the following context,the context may be a question or a 
    requests to explain the concepts briefly or summerize the answer for the relevent topic
    ,if the answer is not in the provided context just say,
    "Answer is not available in the context",don't provide the wrong answer\n\n
    context:\n{context}?\n
    Question:\n{question}\n

    Answer:
    """

    model=ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.3)

    prompt=PromptTemplate(template=prompt_template,input_variables=["context","question"])
    chain=create_stuff_documents_chain(llm=model, prompt=prompt)
    
    return chain


def user_input(user_question):
    embeddings=get_embedding_function()

    new_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    docs=new_db.similarity_search_with_score(user_question, k=15)

    context_documents=[doc[0] for doc in docs]
    chain=get_conversational_chain()



    response=chain.invoke(
        {"context": context_documents, "question": user_question},
        return_only_outputs=True
    )
    return response

def main():
    clear_database()

    print("Chat With Multiple PDF")
    print("Chat with PDF using Gemini: ")

    # Load documents
    documents = load_documents()

    # If no documents are found, handle it by directly querying Gemini Pro
    if not documents:
        print("No PDFs found, using Gemini Pro for direct answers.")

        input_mode = input("Do you want to use voice input? (y/n): ").lower()

        if input_mode == 'y':
            user_question = record_text()
            print(f"Your question (via voice): {user_question}")
        else:
            user_question = input("Ask a question (without PDF context): ")

        if user_question:
            # Use Gemini Pro directly without document context
            model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
            response = model.invoke(user_question)

            print(response.content)
    else:
        # Documents exist, proceed with processing
        chunks = split_documents(documents)
        get_vector_store(chunks)
        print("PDFs loaded and processed.")

        input_mode = input("Do you want to use voice input? (y/n): ").lower()

        if input_mode == 'y':
            user_question = record_text()
            print(f"Your question (via voice): {user_question}")
        else:
            user_question = input("Ask a question from the PDF Files: ")

        if user_question:
            res = user_input(user_question)
            print(res)


if __name__ == "__main__":
    main()

