from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename                   # For file uploads
from langchain_chroma import Chroma
import ollama
import os
from langchain_huggingface import HuggingFaceEmbeddings
# Uncomment the line below to use OpenAIEmbeddings instead of a local model. However, you will need your own API keys to use this model instead, and it won't be completely local.
# from langchain.embeddings import OpenAIEmbeddings
from process_docs import process_directory, handle_single
import datetime
from flask_cors import CORS
# uncomment the line below to use OpenAIEmbeddings instead of a local model
# from langchain.embeddings import OpenAIEmbeddings
# Comment the line below out if you switch to OpenAIEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")      # Change to embedding_model = OpenAIEmbeddings() if you wish to use OpenAIEmbeddings instead
archive_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_dir = os.path.join(archive_dir, 'backend', 'data')
chroma_dir = os.path.join(archive_dir, 'backend', 'ChromaDB')
process_directory(data_dir, chroma_dir)
db = Chroma(persist_directory=chroma_dir, embedding_function=embedding_model)

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
upload_folder = data_dir
app.config['UPLOAD_FOLDER'] = upload_folder
CORS(app)

@app.route('/start', methods=['GET'])
def greet():
    current_time = datetime.datetime.now()
    prompt = f"Based on the current time of my system, ignoring the date and only looking at the time in a 24 hour format, greet me in a human way, but dont mention the exact time, base your greeting message on it: {current_time}. Also, instruct me to use the /followup command by including it as the first word of my message if I have a follow-up question which does not require searching through documents (as this is an application to chat with an LLM about your documents)"
    response = query_ollama(prompt, "llama3.2")
    return jsonify({"response": response})

@app.route('/send', methods = ['POST'])
def handle_file_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"})
    file = request.files['file']
    if file and file.filename.lower().endswith('.pdf'):           # Only allow PDF's
        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(uploaded_path)
        handle_single(uploaded_path, chroma_dir)
        return jsonify({"message": "Success!"})
        
        
@app.route('/query', methods = ['POST'])
def handle_query():
    data = request.json
    user_prompt = data.get("prompt")
    
    if not user_prompt:
        return jsonify({"error": "Prompt not provided"}), 400
    
    first_word = user_prompt.split()[0] if user_prompt else ""
    if first_word == "/followup":
        prompt = f"Use the chat history to answer the following prompt to the best of your abilities. You are not limited to the chat history alone to form a response, and you can use external knowledge to help the user. Do not talk about the /followup command in your response. \nUser: {user_prompt}\nAI"
        response = query_ollama(prompt, "llama3.2")
        return jsonify({"response": response})
    
    results = db.similarity_search_with_score(user_prompt, k=3)  # Get top 3 relevant chunks
    # Build context from retrieved documents
    retrieved_text = "\n".join([f"{doc[0].page_content}" for doc in results])
    
    if not retrieved_text:
        retrieved_text = "No relevant documents found."


    # Form the prompt for Ollama
    full_prompt = f"Use the following retrieved documents to answer the question, and if no relevant documents were found, try to answer it as best as you can, while also acknowledging in response that no relevant documents were found:\n\n{retrieved_text}\n\nUser: {user_prompt}\nAI:"
    response = query_ollama(full_prompt, "llama3.2")
    return jsonify({"response": response})

    
    
if __name__ == "__main__":
    print("Server running at http://127.0.0.1:3000")  # Print URL
    app.run(host='0.0.0.0', port=3000, debug=True)
