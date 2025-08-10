# Rag-chat-memory

This project is a chat application with memory capabilities, utilizing a RAG (Retrieval-Augmented Generation) architecture. It supports multiple interfaces, including Chainlit, Streamlit and React Frontend, and uses a Qdrant vector database for long-term memory as well as the vector store for RAG applications.

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
    uv venv .venv
    . .venv/bin/activate 
    uv pip install -e .
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

## How to Run the VARC Quiz Application

1.  **Start the backend:**
    ```bash
    ./start-local.sh --backend
    ```
2.  **Start the frontend:**
    ```bash
    ./start-local.sh --frontend
    ```
3.  **Open the application:**
    Open your web browser and navigate to `http://localhost:3000` (or the port you specified for the frontend).

### Interacting with the Application

-   **Dashboard:** The dashboard provides a summary of the application's data, including the total number of passages and questions.
-   **Add URL:** You can add new URLs to be crawled on this page. The application will automatically scrape the content, generate questions, and store them in the database.
-   **Crawl Management:** This page is not yet implemented.
-   **Question Bank:** You can view all the generated questions on this page. You can also edit or delete questions.
-   **Quiz Player:** You can play a quiz on this page. The quiz will consist of a random selection of questions from the question bank.
-   **Chat:** You can interact with the chatbot on this page. You can also upload files to be processed and have questions generated from them.

## VARC Quiz Application

This project also includes a VARC (Verbal Ability and Reading Comprehension) quiz application. This application allows you to scrape articles from the web, generate questions from them using an LLM, and then play a quiz.

### How to add a new Editorial link

1.  Navigate to the "Add URL" page in the frontend.
2.  Enter the URL of the article you want to scrape in the text area. You can add multiple URLs, each on a new line.
3.  Click the "Crawl URLs" button to start the scraping process.

### How to run a crawl

The crawling process is started automatically when you add a new URL. The backend will scrape the content, segment it into passages, and generate questions for each passage.

### How to curate questions

1.  Navigate to the "Question Bank" page.
2.  Here you will see a list of all the generated questions.
3.  You can edit or delete questions using the buttons in the "Actions" column.

### API Reference

The application exposes the following API endpoints:

-   `POST /api/crawl`: To crawl a list of URLs.
-   `GET /api/questions`: To get a list of all questions.
-   `PUT /api/questions/{question_id}`: To update a question.
-   `DELETE /api/questions/{question_id}`: To delete a question.
-   `GET /api/quiz/new`: To get a new quiz.
-   `POST /api/quiz/answer`: To submit an answer to a quiz question.

