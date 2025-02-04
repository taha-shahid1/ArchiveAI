from flask import Flask, request, jsonify
from langchain_chroma import Chroma
import ollama
from langchain_huggingface import HuggingFaceEmbeddings
# Uncomment the line below to use OpenAIEmbeddings instead of a local model. However, you will need your own API keys to use this model instead, and it won't be completely local.
# from langchain.embeddings import OpenAIEmbeddings
from process_docs import process_directory
import datetime

# uncomment the line below to use OpenAIEmbeddings instead of a local model
# from langchain.embeddings import OpenAIEmbeddings
# Comment the line below out if you switch to OpenAIEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")      # Change to embedding_model = OpenAIEmbeddings() if you wish to use OpenAIEmbeddings instead
process_directory("./backend/data", "./backend/ChromaDB")
db = Chroma(persist_directory="./backend/ChromaDB", embedding_function=embedding_model)

chat_history = []
# Model parameter to allow users to choose their preferred LLM
def query_ollama(prompt, model):
    global chat_history
    chat_history.append({"role": "user", "content": prompt})
    response = ollama.chat(model = model, messages = chat_history)
    chat_history.append({"role": "assistant", "content": response["message"]["content"]})
    return response["message"]["content"]



# API
app = Flask(__name__)

@app.route('/start', methods = ['POST'])
def greet():
    current_time = datetime.datetime.now()
    prompt = f"Based on the current time of my system, ignoring the date and only looking at the time in a 24 hour format, construct a greeting message based on the time: {current_time}"
    response = query_ollama(prompt, "llama3.2")
    return jsonify({"response": response})


@app.route('/query', methods = ['POST'])
def handle_query():
    data = request.json
    user_prompt = data.get("prompt")
    
    if not user_prompt:
        return jsonify({"error": "Prompt not provided"}), 400
    
    results = db.similarity_search_with_score(user_prompt, k=3)  # Get top 3 relevant chunks
    # Build context from retrieved documents
    retrieved_text = "\n".join([f"{doc[0].page_content}" for doc in results])
    
    if not retrieved_text:
        retrieved_text = "No relevant documents found."


    # Form the prompt for Ollama
    full_prompt = f"Use the following retrieved documents to answer the question, and if no relevant documents were found, include that in response:\n\n{retrieved_text}\n\nUser: {user_prompt}\nAI:"
    response = query_ollama(full_prompt, "llama3.2")
    return jsonify({"response": response})

    
    
if __name__ == "__main__":
    print("Server running at http://127.0.0.1:3000")  # Print URL
    app.run(host='0.0.0.0', port=3000, debug=True)
