# 🚀 Enhanced Task Management System

A comprehensive task management application with AI assistants, background processing, web scraping, and modern authentication.

## ✨ Features

### Core Task Management
- ✅ Create, read, update, and delete tasks
- 🔐 JWT-based authentication and authorization
- 👤 User registration and login system
- 📅 Task deadlines and completion tracking
- 🎨 Modern, responsive web interface

### 🤖 AI Assistants
- **OpenAI Integration**: Advanced task analysis and strategic planning
- **Mistral AI Integration**: Fast, efficient task organization
- **Comparison Mode**: Get responses from both assistants simultaneously
- **Conversation Threading**: Maintain context across chat sessions
- **Real-time Chat Interface**: Interactive chatbot with typing indicators

### ⚙️ Background Processing
- **Celery Integration**: Asynchronous task processing
- **Redis Backend**: Fast message broker and result storage
- **Scheduled Tasks**: Automated cleanup and maintenance
- **Task Reminders**: Automated deadline notifications
- **Bulk Processing**: Handle multiple tasks efficiently

### 🌐 Web Scraping
- **Automated Data Collection**: Scheduled web scraping tasks
- **News Headlines**: Fetch latest news from various sources
- **Custom Scrapers**: Extensible scraping framework
- **Data Storage**: Structured data storage in PostgreSQL

### 🔧 Technical Features
- **Docker Compose**: Complete containerized deployment
- **PostgreSQL Database**: Robust data persistence
- **Redis Caching**: High-performance caching layer
- **CI/CD Pipeline**: Automated testing and deployment
- **Environment Configuration**: Flexible configuration management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (HTML/JS)     │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │◄──►│   Celery        │    │   AI Services   │
│   (Broker)      │    │   Workers       │◄──►│   (OpenAI/      │
└─────────────────┘    └─────────────────┘    │   Mistral)      │
                                               └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- OpenAI API Key (optional)
- Mistral AI API Key (optional)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd task-management-system
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Add your API keys for AI assistants
```

### 3. Start with Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Tasks
- `GET /tasks/get_tasks` - List user tasks
- `POST /tasks/create` - Create new task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `PUT /tasks/{task_id}/complete` - Mark task complete
- `PUT /tasks/{task_id}/incomplete` - Mark task incomplete

### AI Assistants
- `POST /assistant/initialize` - Initialize AI assistants
- `POST /assistant/message` - Send message to assistant
- `POST /assistant/compare` - Compare responses from both assistants
- `POST /assistant/thread` - Create new conversation thread
- `GET /assistant/conversation/{assistant_type}/{thread_id}` - Get chat history
- `GET /assistant/status` - Get assistant status

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-api-key
MISTRAL_API_KEY=your-mistral-api-key

# Web Scraping
SCRAPER_USER_AGENT=TaskManager-Bot/1.0
SCRAPER_DELAY=1
SCRAPER_TIMEOUT=30
```

## 🤖 AI Assistant Usage

### OpenAI Assistant
- **Best for**: Complex analysis, strategic planning, detailed explanations
- **Features**: Code interpretation, file analysis, advanced reasoning
- **Model**: GPT-4 Turbo

### Mistral Assistant
- **Best for**: Quick responses, efficient task organization, concise advice
- **Features**: Fast processing, practical solutions, direct answers
- **Model**: Mistral Large

### Comparison Mode
- Send the same query to both assistants
- Compare different approaches and perspectives
- Get comprehensive insights from multiple AI models

## 🔄 Background Tasks

### Scheduled Tasks
- **Daily Cleanup**: Remove completed tasks older than 30 days
- **News Scraping**: Fetch latest headlines every hour
- **Task Reminders**: Send deadline notifications

### Manual Tasks
- **Bulk Processing**: Handle multiple tasks at once
- **Data Scraping**: On-demand web scraping
- **System Maintenance**: Database optimization

## 🌐 Web Scraping

### Supported Sources
- News websites (Hacker News, etc.)
- Custom data sources
- API endpoints
- RSS feeds

### Data Storage
- Scraped data stored in PostgreSQL
- Structured tables for different data types
- Automatic deduplication
- Timestamp tracking

## 🧪 Development

### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
psql -c "CREATE DATABASE taskmanager;"

# Run migrations (automatic on startup)
python -m src.main

# Start Celery worker (separate terminal)
celery -A src.celery_app worker --loglevel=info

# Start Celery beat (separate terminal)
celery -A src.celery_app beat --loglevel=info
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_tasks.py
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 📁 Project Structure

```
├── src/
│   ├── assistant/          # AI assistant modules
│   │   ├── openai_assistant.py
│   │   ├── mistral_assistant.py
│   │   ├── assistant_manager.py
│   │   └── api.py
│   ├── tasks/              # Task management
│   │   ├── models.py
│   │   ├── crud.py
│   │   ├── api.py
│   │   └── celery_tasks.py
│   ├── scraper/            # Web scraping
│   │   └── tasks.py
│   ├── auth.py             # Authentication
│   ├── auth_api.py         # Auth endpoints
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   ├── celery_app.py       # Celery configuration
│   └── main.py             # FastAPI application
├── frontend/
│   └── index.html          # Web interface
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # CI/CD pipeline
├── docker-compose.yml      # Docker services
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security

- JWT token-based authentication
- Password hashing with bcrypt
- CORS protection
- Environment variable configuration
- API key security best practices

## 🚀 Deployment

### Docker Deployment
```bash
# Production build
docker-compose -f docker-compose.yml up -d

# Scale workers
docker-compose up -d --scale celery-worker=3
```

### Manual Deployment
1. Set up PostgreSQL and Redis
2. Configure environment variables
3. Install Python dependencies
4. Run database migrations
5. Start FastAPI server
6. Start Celery workers and beat

## 📊 Monitoring

- **Health Checks**: Built-in health endpoints
- **Logging**: Comprehensive application logging
- **Metrics**: Task completion and performance metrics
- **Error Tracking**: Detailed error reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Integration with external calendars
- [ ] Voice assistant integration
- [ ] Advanced AI task automation
- [ ] Real-time notifications
- [ ] Task templates and workflows
