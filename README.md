# 🎥 Video RAG AI: An AI-Powered Video Summarization and Question-Answering System

## 📌 Project Overview

Video RAG AI is an AI-powered application that allows users to process videos, generate summaries, and ask questions about video content.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from video transcripts and generate context-aware answers. It combines speech transcription, text embeddings, vector search, and Large Language Models (LLMs) to make video content easier to understand.

The project includes a **Streamlit frontend** and a **FastAPI backend**, with MySQL for structured data storage and ChromaDB for vector-based semantic search.

## ✨ Key Features

- **Video Processing:** Process videos using a video URL.
- **Speech Transcription:** Convert spoken content into text using OpenAI Whisper.
- **AI Summarization:** Generate concise summaries of video content.
- **Key Insights:** Extract important points, action items, key decisions, and open questions.
- **RAG-Based Question Answering:** Ask questions about a processed video and receive answers based on its transcript.
- **Semantic Search:** Retrieve relevant transcript chunks using vector embeddings.
- **AI Chatbot:** Interact with video content through a conversational interface.
- **User Authentication:** Register and log in securely.
- **JWT Authorization:** Protect API endpoints and restrict access to user-owned videos and chats.
- **Chat History:** Store and retrieve conversations.
- **Database Integration:** Use MySQL for structured application data.
- **Vector Database:** Use ChromaDB to store and search transcript embeddings.
- **REST APIs:** Build backend endpoints using FastAPI.
- **Interactive Interface:** Provide a user-friendly interface using Streamlit.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI |
| API Server | Uvicorn |
| Database | MySQL |
| ORM | SQLAlchemy |
| Authentication | JWT, password hashing |
| Speech Transcription | OpenAI Whisper |
| LLM Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Gemini Embeddings |
| Large Language Model | Groq LLM |
| Video Processing | yt-dlp and FFmpeg, if configured |
| API Documentation | Swagger UI, ReDoc |

## 🔄 How the Project Works

### 1. Video Processing

1. The user logs in and submits a video URL.
2. The backend receives and validates the request.
3. The video processing pipeline extracts the audio when required.
4. OpenAI Whisper converts the speech into text.
5. The transcript is divided into smaller chunks.
6. Gemini Embeddings converts the transcript chunks into vector representations.
7. The embeddings and associated metadata are stored in ChromaDB.
8. The generated summary and video metadata are saved in MySQL.

### 2. Video Summarization

The transcript is processed using a Groq-powered LLM to generate useful information, such as:

- Video summary
- Key insights
- Important points
- Action items
- Key decisions
- Open questions

This helps users understand the main content without watching the entire video.

### 3. Question Answering Using RAG

1. The user selects a processed video and asks a question.
2. The backend verifies the user's authentication and resource access.
3. The question is used to retrieve semantically relevant transcript chunks from ChromaDB.
4. Retrieval is restricted to the selected video's content.
5. The relevant chunks are added to the prompt sent to the Groq LLM.
6. The LLM generates an answer based on the retrieved context.
7. The answer and conversation history are stored in MySQL.
8. The answer is displayed to the user through the Streamlit interface.

## 🧠 What Is Retrieval-Augmented Generation (RAG)?

Retrieval-Augmented Generation is a technique that combines information retrieval with Large Language Models.

Instead of asking an LLM to answer a question using only its general knowledge, the system first retrieves relevant information from a knowledge source and then uses that information to generate an answer.

In this project:

- **Retrieval:** ChromaDB searches for relevant transcript chunks.
- **Augmentation:** The retrieved text is added to the LLM prompt.
- **Generation:** The Groq LLM generates a context-aware response.

This approach helps the chatbot answer questions using the content of the selected video.

## 🔐 Authentication and Authorization

The application uses JSON Web Tokens (JWT) to authenticate users and protect private resources.

### Authentication Flow

1. A user registers with the application.
2. The password is hashed before being stored.
3. The user logs in with their credentials.
4. The backend verifies the credentials and generates an access token.
5. The client sends the token with requests to protected endpoints.
6. The backend validates the token and identifies the current user.

### Authorization

The backend checks resource ownership before allowing access to videos and chats. This prevents users from accessing another user's private resources through protected API endpoints.

Protected requests use the following HTTP header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 🔌 API Endpoints

The backend provides REST APIs for authentication, video processing, and chat management.

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Public |
| POST | `/auth/login` | Log in and receive an access token | Public |
| POST | `/videos/process-url` | Process a video URL | Protected |
| POST | `/videos/{video_id}/chats` | Create a chat for a video | Protected |
| GET | `/videos/{video_id}/chats` | List chats for a video | Protected |
| GET | `/chats/{chat_id}` | Retrieve a chat | Protected |
| POST | `/chats/{chat_id}/messages` | Ask a question in a chat | Protected |
| DELETE | `/chats/{chat_id}` | Delete a chat | Protected |

Interactive API documentation is available through Swagger UI and ReDoc when the backend is running.

## 🗄️ Database Design

### MySQL

MySQL stores structured application data, including:

- User information
- Video metadata
- Video processing status
- Generated summaries and related information
- Chat sessions
- Chat messages and conversation history

SQLAlchemy is used to interact with the relational database.

### ChromaDB

ChromaDB stores vector embeddings generated from transcript chunks, along with relevant metadata.

It supports semantic retrieval so that the system can identify transcript sections related to a user's question.

The retrieved chunks are filtered by video ID to keep question-answering focused on the selected video.

## 📁 Project Structure

```text
video-rag-ai-agent/
│
├── backend/
│   ├── api/
│   │   ├── auth_api.py
│   │   ├── video_api.py
│   │   └── chat_api.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── base.py
│   │
│   ├── dependencies/
│   │   └── auth.py
│   │
│   ├── models/
│   │   ├── user_model.py
│   │   ├── video_model.py
│   │   ├── chat_model.py
│   │   └── chat_message_model.py
│   │
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── video_schema.py
│   │   └── chat_schema.py
│   │
│   ├── services/
│   │   ├── auth_services.py
│   │   ├── video_service.py
│   │   ├── chat_service.py
│   │   ├── vectore_store.py
│   │   └── summarize.py
│   │
│   └── main.py
│
├── frontend/
├── uploads/
├── downloads/
├── vector_db/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── Dockerfile
```

*Note: Confirm the frontend entry-point filename and other file names against your actual project before publishing.*

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.12 or a compatible version
- MySQL Server
- Git
- Gemini API key
- Groq API key
- FFmpeg, if required by your video-processing implementation

### Step 1: Clone the Repository

Replace `YOUR_USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR_USERNAME/video-rag-ai-agent.git
cd video-rag-ai-agent
```

### Step 2: Create a Virtual Environment

```bash
python -m venv myenv
```

Activate it on Windows:

```bash
myenv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create the MySQL Database

Open MySQL Workbench or your MySQL client and execute:

```sql
CREATE DATABASE video_rag_db;
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root and configure the variables required by your application.

Example:

```env
DATABASE_URL=mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost/video_rag_db

GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

JWT_SECRET_KEY=your_generated_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the placeholder values with your actual configuration. Ensure that the variable names match those used in your code.

**Security note:** Never upload your `.env` file, API keys, database passwords, or JWT secret to GitHub. Add `.env` to `.gitignore`.

### Step 6: Start the FastAPI Backend

From the project root, run:

```bash
uvicorn backend.main:app --reload
```

Open the following URL to access the API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

### Step 7: Start the Streamlit Frontend

Open another terminal, activate the same virtual environment, and run the actual Streamlit entry-point file.

For example, if your entry point is `frontend/app.py`:

```bash
streamlit run frontend/app.py
```

If your file has a different name, replace the path accordingly.

## 🧪 Testing

Test the application using the following scenarios:

- Register a new user.
- Log in and obtain an access token.
- Process a valid video URL.
- Verify that the transcript and summary are generated.
- Ask questions about the processed video.
- Check that answers are based on relevant transcript content.
- Verify that chat history is stored and retrieved correctly.
- Confirm that requests without valid authentication are rejected.
- Confirm that users cannot access videos or chats owned by other users.

## 🔒 Security Considerations

- Hash passwords before storing them.
- Protect private endpoints with JWT authentication.
- Validate access tokens and their expiration.
- Check video and chat ownership for protected operations.
- Store API keys and secrets in environment variables.
- Never commit credentials or sensitive configuration files to version control.
- Validate user input and handle processing errors appropriately.

## 🚀 Future Improvements

Possible enhancements include:

- Support for uploading local video files.
- Support for additional video platforms.
- Improved transcription and language support.
- Timestamp-based answers with transcript references.
- Background processing for long videos.
- Progress tracking for video processing.
- Better error handling and retry mechanisms.
- Automated tests for APIs and RAG retrieval.
- Docker-based deployment.
- Cloud deployment and scalable storage.

## 🎯 Project Objectives

The main objectives of this project are to:

1. Automate video transcription and summarization.
2. Make video content searchable through semantic retrieval.
3. Enable users to ask questions about video content.
4. Generate context-aware answers using RAG.
5. Store application data and chat history reliably.
6. Protect user resources through authentication and authorization.
7. Provide a simple interface for interacting with video content.

## 👨‍💻 Author

**Vitthal Kharole**

GitHub: [YOUR_GITHUB_PROFILE](https://github.com/YOUR_USERNAME)

LinkedIn: [YOUR_LINKEDIN_PROFILE](YOUR_LINKEDIN_URL)

## 📄 License

Choose a license that matches how you want others to use your project. If you intend to make the repository open source, consider adding a `LICENSE` file with the license terms.
