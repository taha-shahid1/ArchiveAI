# ArchiveAI

ArchiveAI allows you to chat with your documents using LLMs while keeping your information private and local.

## Prerequisites

Before getting started, ensure you have Python 3.9.12, the latest version of Node and [Ollama](https://ollama.com/download) installed to run a local LLM.

Once installed, run llama3.2 by running the following command in your terminal:

```sh
ollama run llama3.2
```

Keep llama3.2 running in the background. When you are done using ArchiveAI, stop llama3.2 by typing in the /bye command.

## Installation & Setup

### 1. Clone the Repository

Open a new terminal window and run the following commands:

```sh
cd
git clone https://github.com/taha-shahid1/ArchiveAI.git
cd ArchiveAI
```

### 2. Install Backend Dependencies
Ensure you have Python 3.9.12 installed before running the following command:
```sh
pip3 install -r requirements.txt
```

### 3. Install Frontend Dependencies
Ensure you have the latest version of Node installed before running the following commands:

```sh
cd frontend
npm install
cd ..
```

## Running the Project

### 1. Adding Documents
To make documents available for the LLM:

1. When the Flask server isnt running:

Add your PDFs to the `data` folder inside the `backend` folder.

2. While the Flask server is running:

Use the UI in the frontend to upload your PDFs. (Instructions on starting the frontend are provided later in this README.)

### 2. Start the Backend
To start the backend, run the `app.py` file. You can do this by either running the `app.py` file using an IDE of your choice, or by executing the following commands in a terminal window:

```sh
cd 
cd ArchiveAI
python3 -u backend/app.py
```

This will start the local Flask server.

### 3. Start the Frontend
Open a new terminal window and type in these commands:

```sh
cd
cd ArchiveAI
cd frontend
npm run dev
```

The React frontend will start, and a URL will be displayed in the terminal. Open the URL in your browser to start using ArchiveAI!

### Closing ArchiveAI
To stop the backend, go to the terminal window where the backend is running, and press:

```sh
CTRL + C
```

To stop the frontend, go to the terminal window where the frontend is running, and press:

```sh
CTRL + C
```

To stop llama3.2, go to the terminal window where llama3.2 is running, and type in the following command:

```sh
/bye
```
