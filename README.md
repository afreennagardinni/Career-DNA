# Career DNA Agentic AI Platform

A production-ready Flask backend architecture for career assessment and DNA analysis.

## Project Structure

```
DNA/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask application factory
│   ├── extensions.py        # Flask extensions (db, login, migrate)
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model with common fields
│   │   ├── user.py          # User model
│   │   ├── assessment.py    # Assessment model
│   │   ├── answer.py        # Answer model
│   │   └── profile.py       # Profile model
│   ├── routes/              # Flask route blueprints
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   └── main.py          # Main routes
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── auth_service.py  # Authentication service
│   ├── agents/              # AI agent implementations (future)
│   │   └── __init__.py
│   ├── rag/                 # RAG implementations (future)
│   │   └── __init__.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── logger.py        # Logging setup
├── migrations/              # Database migration files
├── logs/                    # Application logs
├── tests/                   # Test files
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── run.py                  # Application entry point
└── README.md               # This file
```

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for routes, services, models, agents, and RAG
- **Database**: SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL/MySQL)
- **Authentication**: Complete user registration, login, logout, and session management using Flask-Login
- **Configuration**: Environment-based configuration (development, testing, production)
- **Logging**: Comprehensive logging setup with file rotation
- **App Factory Pattern**: Flask application factory for easy testing and multiple instances

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd c:\Users\admin\Desktop\DNA
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and update the `SECRET_KEY` with a secure random string for production.

6. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   
   Or for development, the app will auto-create tables on first run.

### Running the Application

**Development mode:**
```bash
python run.py
```

The application will start on `http://localhost:5000`

**Using Flask CLI:**
```bash
set FLASK_APP=run.py
set FLASK_ENV=development
flask run
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
  ```json
  {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```

- `POST /auth/login` - Log in a user
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

- `POST /auth/logout` - Log out the current user (requires authentication)

- `GET /auth/me` - Get current user information (requires authentication)

- `PUT /auth/me` - Update current user information (requires authentication)

### General

- `GET /` - API information
- `GET /health` - Health check endpoint

## Database Models

### User
- Email, username, password (hashed)
- First name, last name
- Active status, admin flag
- Relationships: assessments, profile

### Assessment
- Title, description, type
- Status (in_progress, completed, abandoned)
- Total score, max score
- Relationships: user, answers

### Answer
- Question text, question ID
- Answer text, answer value
- Score, category, question type
- Relationship: assessment

### Profile
- Job title, industry, years of experience
- Education level
- Career DNA (JSON field for traits, skills, interests)
- Work preferences, career goals
- Completion percentage
- Relationship: user

## Configuration

The application supports three environments:

- **Development**: Debug mode enabled, detailed logging
- **Testing**: In-memory database, CSRF disabled
- **Production**: Debug disabled, secure cookies enabled

Set the environment via the `FLASK_ENV` environment variable or by passing it to `create_app()`.

## Logging

Logs are stored in the `logs/` directory with automatic rotation (10MB max, 10 backups). Log level can be configured via the `LOG_LEVEL` environment variable.

## Future Enhancements

- AI agent implementations in `app/agents/`
- RAG (Retrieval-Augmented Generation) in `app/rag/`
- Additional service layer implementations
- Comprehensive test suite
- API documentation (Swagger/OpenAPI)
- Rate limiting
- Email verification
- Password reset functionality

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Set `SESSION_COOKIE_SECURE=True` in production
- Implement rate limiting for authentication endpoints
- Add CSRF protection for form submissions
- Use environment variables for sensitive configuration

## License

[Add your license here]
