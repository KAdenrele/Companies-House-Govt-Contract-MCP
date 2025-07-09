from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.file_reader import read_pdf_to_text
import asyncio


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def convert_dict_to_langchain_doc(dictionary: dict) -> list:
    documents = []
    for file_name in dictionary:
        for page, text in dictionary[file_name].items():
            doc = Document(page_content=text, metadata={
                                                        "source": file_name,
                                                        "page": page + 1
                                                        }
            )
            documents.append(doc)
    return documents

def read_pdf_to_langchain_document(file_name, directory:Path):
    text_dictionary = read_pdf_to_text(DATA_DIR=directory, file=file_name)
    text_doc_list = convert_dict_to_langchain_doc(text_dictionary)
    return text_doc_list

def store_doc_in_new_vector_store(doc_list:list):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents=doc_list)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

async def all_docs_to_new_vector_store_async(docs_directory: Path) -> FAISS:
    """
    Asynchronously reads all PDFs, creates embeddings, and saves them to a new vector store.
    """
    file_name_list = [p.name for p in docs_directory.glob('*.pdf')]
    documents = []

    # This part remains synchronous, but could be parallelized with asyncio.gather
    for file_name in file_name_list:
        text_dict_for_file = read_pdf_to_text(DATA_DIR=docs_directory, file=file_name)
        if file_name in text_dict_for_file:
            for page, text in text_dict_for_file[file_name].items():
                doc = Document(
                    page_content=text,
                    metadata={"source": file_name, "page": page + 1}
                )
                documents.append(doc)

    print(f"Processing {len(documents)} pages into a new knowledge base...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
    chunks = text_splitter.split_documents(documents=documents)
    
    # Extract the text content from the Document chunks
    chunk_texts = [chunk.page_content for chunk in chunks]

    print("Creating embeddings asynchronously...")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Asynchronously create embeddings for all the chunk texts
    vector_embeddings = await embeddings_model.aembed_documents(chunk_texts)

    # Combine the texts and their corresponding vector embeddings
    text_embedding_pairs = list(zip(chunk_texts, vector_embeddings))

    # Get the metadata from the original chunks
    metadatas = [chunk.metadata for chunk in chunks]
    
    # Create the FAISS index from embeddings, letting the constructor handle the docstore
    vector_store = FAISS.from_embeddings(
        text_embeddings=text_embedding_pairs, 
        embedding=embeddings_model,
        metadatas=metadatas
    )

    print("Saving new knowledge base...")
    # NOTE: save_local is a synchronous operation
    vector_store.save_local("faiss_index")
    print("New knowledge base created and saved as 'faiss_index'")

    return vector_store

class KnowledgeBaseTool(): 
    def __init__(self,index_directory, index_file):
        self.index_dir = index_directory
        self.index_file = index_file
        self.index_path = os.path.join(self.index_dir, self.index_file)

        """
        Initializes the RAG retriever by loading the vector store.
        """
        if not os.path.exists(self.index_path):
            print("Loading PDFs into knowledge base for the first time. This may take a few minutes.")
            asyncio.run(all_docs_to_new_vector_store_async(docs_directory=DATA_DIR))
        
        # Ensure you use the same embedding model as during indexing
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Load the vector store
        self.vector_store = FAISS.load_local(
            self.index_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        

        
        # Create a retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        print("Knowledge Base Tool initialized successfully.")

    def search(self, query: str) -> str:
        """
        Searches the knowledge base for relevant documents and returns them as a string.
        This is the function that will be exposed as a tool.
        """
        print(f"Searching for: {query}")
        retrieved_docs = self.retriever.invoke(query)
        
        # Format the retrieved documents into a single string
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        return context






