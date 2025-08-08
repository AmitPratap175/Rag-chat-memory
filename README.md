# AI Programming Tutor

This project is an AI-powered programming tutor. You can upload a programming book, and the application will generate a study plan, provide chat-based tutoring, and help you with coding exercises.

## Project Structure

The project is divided into a Python backend and a frontend application.
- `backend/`: Contains the core logic for the application, including ingestion, RAG, memory, study plans, and code execution.
- `frontend/`: Contains the user interface.
- `data/`: Stores uploaded books, the vector store, and user memory.

## Features

- **Book Ingestion:** Upload programming books in PDF, TXT, or MD format.
- **Study Plan Generation:** Automatically generates a study plan based on the book's content.
- **Interactive Chat:** Chat with the tutor to get explanations and help.
- **Inline Code Execution:** Run Python code and get feedback.

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python backend/app.py
```


