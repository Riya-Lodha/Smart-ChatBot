# Smart ChatBot

A smart chatbot built with FastAPI and OpenAI, featuring intent-based responses and AI-powered conversations.

## Features

- Intent-based response matching using fuzzy string matching
- OpenAI integration for advanced responses
- Real-time streaming responses
- Web-based chat interface
- Session management
- Response caching
- Health monitoring


## API Endpoints

- GET `/`: Web chat interface
- POST `/chat/stream`: Stream chat responses
- GET `/health`: Service health check
- DELETE `/chat/history/{session_id}`: Clear chat history


##To run the Project
 1. Clone the repository
 2.  Create and activate virtual environment
 3.  Install dependencies
 4.  Create .env file and add your OpenAI API key
 5.  Run the application: `uvicorn app:app --reload`
