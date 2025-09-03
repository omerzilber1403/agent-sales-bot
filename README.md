# AGENT - Intelligent Sales Bot

A sophisticated AI-powered sales bot that adapts to different business types (B2B/B2C) and provides personalized customer interactions.

## Features

- **Multi-tenant Architecture**: Support for multiple companies with custom configurations
- **B2B/B2C Adaptive**: Different conversation flows for business and consumer customers
- **LangGraph Integration**: Advanced conversation flow management
- **Custom Company Fields**: Configurable data collection per company
- **Real-time Debugging**: Clear visibility into bot responses and conversation flow
- **FastAPI Backend**: RESTful API with comprehensive admin interface
- **React Frontend**: Modern web interface for testing and management

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (or other LLM provider)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AGENT
```

2. **Set up Python environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Initialize database**
```bash
python -c "from backend.database.init_db import init_db; init_db()"
```

5. **Start servers**
```bash
# Windows
.\start_servers.bat

# Or manually:
# Backend (Terminal 1)
cd backend
python -m uvicorn main:app --reload --port 8080

# Frontend (Terminal 2)
cd frontend/tests
npm run dev
```

## Usage

1. **Access the application**: http://localhost:5173
2. **Create a company** with B2B or B2C configuration
3. **Start chatting** with the bot to test different scenarios
4. **Monitor conversations** through the admin interface

## Architecture

### Backend (FastAPI)
- **Graph Engine**: LangGraph-based conversation flow
- **Database**: SQLite with SQLAlchemy ORM
- **LLM Integration**: OpenAI GPT models
- **Multi-tenant**: Company-specific configurations

### Frontend (React)
- **Company Management**: Create and configure companies
- **Chat Interface**: Real-time conversation testing
- **Admin Dashboard**: Monitor and manage conversations

### Key Components

- **Sales Graph**: Intelligent routing between B2B/B2C flows
- **Customer Profiling**: Automatic information extraction and storage
- **Custom Fields**: Company-specific data collection
- **Debug System**: Clear visibility into bot decision-making

## Configuration

### Company Setup
Each company can be configured with:
- Business type (B2B/B2C)
- Products and pricing
- Custom data collection fields
- Brand voice and messaging
- Handoff rules and triggers

### Environment Variables
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Development

### Project Structure
```
AGENT/
├── backend/           # FastAPI backend
│   ├── graph/        # LangGraph conversation flows
│   ├── models/       # Database models
│   ├── routes/       # API endpoints
│   └── services/     # Business logic
├── frontend/tests/   # React frontend
└── data/            # SQLite database
```

### Adding New Features
1. **New Conversation Nodes**: Add to `backend/graph/sales_graph.py`
2. **Database Changes**: Create migration in `backend/migrations/`
3. **API Endpoints**: Add to `backend/routes/`
4. **Frontend Components**: Add to `frontend/tests/src/components/`

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
