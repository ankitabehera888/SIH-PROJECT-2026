# MedAssist AI - Symptom Analyst Agent

AI-powered symptom analysis system built with FastAPI and OpenAI.

## Features

- **Multi-turn symptom interviews** using OLDCARTS framework
- **Differential diagnosis** ranked by likelihood and confidence
- **Urgency scoring** with red-flag detection
- **Specialist referral** recommendations
- **Tool calling** for medical knowledge base and patient history

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API:**
   - API docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Start a Symptom Session
```bash
curl -X POST http://localhost:8000/api/v1/symptoms/session \
  -H "Content-Type: application/json" \
  -d '{"chief_complaint": "I have a severe headache for 3 days"}'
```

### Send a Message
```bash
curl -X POST http://localhost:8000/api/v1/symptoms/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "The pain is throbbing, about 7/10 severity"}'
```

### Get Session Details
```bash
curl http://localhost:8000/api/v1/symptoms/session/{session_id}
```

### Complete Session
```bash
curl -X PUT http://localhost:8000/api/v1/symptoms/session/{session_id}/complete
```

## Architecture

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Database ORM
- **OpenAI GPT-4o** - AI reasoning engine
- **Pydantic** - Request/response validation
- **Structlog** - Structured logging

## AI Agent Tools

The Symptom Analyst Agent has access to:

1. **search_medical_kb** - Query medical knowledge base
2. **query_patient_history** - Fetch patient medical history
3. **calculate_urgency_score** - Rule-based urgency scoring
4. **recommend_specialist** - Map symptoms to specialist type

## Development

The application uses mock data for development. To connect to real services:

- Replace `search_medical_kb` stub with vector database
- Replace `query_patient_history` stub with database queries
- Configure OpenAI API key for production use
