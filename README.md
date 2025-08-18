# WhatsApp Chatbot

This project is a WhatsApp chatbot with memory capabilities, utilizing a RAG (Retrieval-Augmented Generation) architecture. It uses a Qdrant vector database for long-term memory as well as the vector store for RAG applications.

## Project Structure

The project is a backend Python application that handles the core logic of the WhatsApp chatbot, including the AI companion, memory management, and integrations with the WhatsApp Business API.

## Features

- **Conversational AI:** A chatbot powered by a large language model, accessible via WhatsApp.
- **Long-Term Memory:** Utilizes a Qdrant vector database to provide the chatbot with long-term memory.
- **RAG Architecture:** Enhances the chatbot's responses by retrieving relevant information from a knowledge base.
- **Speech-to-Text and Text-to-Speech:** Includes modules for converting speech to text and vice-versa, allowing for voice-based interactions on WhatsApp.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [the-gitlab-link-here]
    cd whatsapp-bot
    ```

2.  **Install Python dependencies:**
    ```bash
    uv venv .venv
    . .venv/bin/activate 
    uv pip install -e .
    ```

3.  **Set up environment variables:**
    Create a `.env` file by copying the `.env.example` and fill in the required values.
    ```bash
    cp .env.example .env
    ```

4.  **Set up the Qdrant local database:**
    Run the following commands in an independent shell to set up the Qdrant local database. Note if you change the default ports, they should be accordingly changed in the `vector_store.py` file
    ```bash
    podman pull docker.io/qdrant/qdrant
    podman run --rm --network=host docker.io/qdrant/qdrant
    ```

### Running the Application

To run the application, use the following command:

```bash
fastapi run src/chatbot/interfaces/whatsapp/webhook_endpoint.py --port 3000
```


## Building with Docker or Podman

To build the image, use one of the following commands.

### Docker
```bash
docker build -t whatsapp-bot .
```

### Podman
```bash
podman build -t whatsapp-bot .
```


