from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma


# Uncomment the line below to use OpenAIEmbeddings instead of a local model. However, you will need your own API keys to use this model instead, and it won't be completely local.
# from langchain.embeddings import OpenAIEmbeddings

# Comment out/delete the line below if you wish to use OpenAIEmbeddings instead
from sentence_transformers import SentenceTransformer

# Comment out/delete this class if you decide to use OpenAIEmbeddings instead
class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Local model for generating embeddings
    
    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()
    
    def embed_query(self, query):
        return self.model.encode(query).tolist()

# Utility functions to get data from PDF files and Word files in desired directory
def load_pdf_documents(directory_path):
    pdf_loader = PyPDFDirectoryLoader(directory_path)
    return pdf_loader.load()

def load_word_documents(directory_path):
    word_loader = Docx2txtLoader(directory_path)
    return word_loader.load()


# Utility function to split documents to chunks
def split_documents_into_chunks(documents_list: list[Document]):             # Type hint for the document schema
    text_splitter_instance = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=70,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter_instance.split_documents(documents_list)

# Utility function to generate ID's for each chunk, which will be used to tell user which documents were used by the LLM to generate a response
def generate_chunk_ids(doc_chunks:list[Document]):                         # Type hint for the document schema
    last_page = None
    chunk_index = 0

    for doc_chunk in doc_chunks:
        file_source = doc_chunk.metadata.get("source")
        page_number = doc_chunk.metadata.get("page")
        current_page = f"{file_source}:{page_number}"

        # Increment the counter if the page ID is same as last one
        if current_page == last_page:
            chunk_index += 1
        else:
            chunk_index = 0

        chunk_id = f"{current_page}:{chunk_index}"
        last_page = current_page

        # Add the chunk ID to the document's metadata
        doc_chunk.metadata["id"] = chunk_id

    return doc_chunks

# Utility function to populate the Chroma database 
def update_chroma_database(doc_chunks, chroma_directory):
    embedding_model = EmbeddingModel()  # Change to embedding_model = OpenAIEmbeddings() if you decide to use OpenAIEmbeddings

    # Load the existing Chroma database
    chroma_db = Chroma(
        persist_directory=chroma_directory, embedding_function=embedding_model
    )

    # Assign Chunk IDs 
    chunks_with_ids = generate_chunk_ids(doc_chunks)

    # Prevent duplicates by only adding new chunks to the database
    existing_documents = chroma_db.get(include=[])
    existing_document_ids = set(existing_documents["ids"])
    new_documents = []
    
    for doc_chunk in chunks_with_ids:
        if doc_chunk.metadata["id"] not in existing_document_ids:
            new_documents.append(doc_chunk)

    if new_documents:
        print(f"Adding {len(new_documents)} new documents...")
        new_document_ids = [doc.metadata["id"] for doc in new_documents]
        chroma_db.add_documents(new_documents, ids=new_document_ids)
        chroma_db.persist()


def process_directory(directory_path, chroma_directory):
    documents = load_pdf_documents(directory_path) + load_word_documents(directory_path)
    document_chunks = split_documents_into_chunks(documents)
    update_chroma_database(document_chunks, chroma_directory)