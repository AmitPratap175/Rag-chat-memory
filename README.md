# Rag-chat-memory

This project is a chat application with memory capabilities, utilizing a RAG (Retrieval-Augmented Generation) architecture. It supports multiple interfaces, including Chainlit, Streamit and React Frontend, and uses a Qdrant vector database for long-term memory as well as the vector store for RAG applications.

## Project Structure

The project is structured with a backend Python application and a React frontend. The backend handles the core logic of the chat application, including the AI companion, memory management, and integrations with services like WhatsApp. The frontend provides a user interface for interacting with the chatbot.

## Features

- **Conversational AI:** A chatbot powered by a large language model.
- **Long-Term Memory:** Utilizes a Qdrant vector database to provide the chatbot with long-term memory.
- **Multi-Interface Support:** Can be accessed through Chainlit, and a WhatsApp integration is provided.
- **RAG Architecture:** Enhances the chatbot's responses by retrieving relevant information from a knowledge base.
- **Speech-to-Text and Text-to-Speech:** Includes modules for converting speech to text and vice-versa.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js and npm
- Docker and Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AmitPratap175/Rag-chat-memory.git
    cd Rag-chat-memory
    ```

2.  **Install Python dependencies:**
    ```bash
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file by copying the `.env.example` and fill in the required values.
    ```bash
    cp .env.example .env
    ```

4.  **Set up the Qdrant loacl database:**
    Run the following commands in an independent shell to set up the Qdrant local database. Note if you change the default ports, they should be accordingly changed in the `vector_store.py` file
    ```bash
    podman pull docker.io/qdrant/qdrant
    podman run --rm --network=host docker.io/qdrant/qdrant
    ```

### Running the Application

The application can be started using the provided shell script `start-local.sh`. This script can start the backend and frontend separately.

**To start the backend:**

This command will also build the frontend static files.

```bash
chmod +x start-local.sh
./start-local.sh --backend
```

If you want to start the backend without building the frontend, use the `--nobuild` flag:

```bash
./start-local.sh --backend --nobuild
```

**To start the frontend:**

```bash
./start-local.sh --frontend
```

You can also specify the ports for the frontend and backend using the `--frontend-port` and `--backend-port` flags.


