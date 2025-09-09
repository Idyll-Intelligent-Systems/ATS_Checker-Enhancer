# ZeX-ATS-AI Project Structure

This document provides a comprehensive overview of the project structure and architecture.

## 📁 Project Structure

```
ZeX-ATS-AI/
├── 📁 src/                           # Main application source code
│   ├── 📁 api/                       # API layer
│   │   ├── v1/                       # API version 1
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── users.py             # User management endpoints
│   │   │   ├── analyze.py           # Resume analysis endpoints
│   │   │   ├── jobs.py              # Job search and matching endpoints
│   │   │   ├── analytics.py         # Analytics endpoints
│   │   │   └── admin.py             # Admin endpoints
│   │   └── middleware.py            # Custom middleware
│   │
│   ├── 📁 core/                      # Core system components
│   │   ├── config.py                # Application configuration
│   │   ├── database.py              # Database management
│   │   ├── security.py              # Security utilities
│   │   ├── exceptions.py            # Custom exceptions
│   │   └── logging.py               # Logging configuration
│   │
│   ├── 📁 models/                    # Database models
│   │   ├── base.py                  # Base model class
│   │   ├── user.py                  # User model
│   │   ├── resume.py                # Resume model
│   │   ├── analysis.py              # Analysis model
│   │   ├── job.py                   # Job model
│   │   └── subscription.py          # Subscription model
│   │
│   ├── 📁 services/                  # Business logic layer
│   │   ├── ai_service.py            # AI integration service
│   │   ├── analysis_service.py      # Resume analysis service
│   │   ├── user_service.py          # User management service
│   │   ├── job_service.py           # Job matching service
│   │   ├── email_service.py         # Email service
│   │   ├── file_service.py          # File handling service
│   │   └── analytics_service.py     # Analytics service
│   │
│   ├── 📁 ai/                        # AI and ML components
│   │   ├── models/                  # AI model configurations
│   │   │   ├── openai_client.py     # OpenAI integration
│   │   │   ├── anthropic_client.py  # Anthropic integration
│   │   │   └── huggingface_client.py # Hugging Face integration
│   │   ├── prompts/                 # AI prompts and templates
│   │   │   ├── resume_analysis.py   # Resume analysis prompts
│   │   │   ├── job_matching.py      # Job matching prompts
│   │   │   └── optimization.py      # Optimization prompts
│   │   └── processors/              # Document processing
│   │       ├── pdf_processor.py     # PDF document processing
│   │       ├── docx_processor.py    # Word document processing
│   │       └── text_processor.py    # Text processing utilities
│   │
│   ├── 📁 schemas/                   # Pydantic schemas for API
│   │   ├── auth.py                  # Authentication schemas
│   │   ├── user.py                  # User schemas
│   │   ├── resume.py                # Resume schemas
│   │   ├── analysis.py              # Analysis schemas
│   │   └── job.py                   # Job schemas
│   │
│   ├── 📁 utils/                     # Utility functions
│   │   ├── validators.py            # Input validation utilities
│   │   ├── helpers.py               # General helper functions
│   │   ├── constants.py             # Application constants
│   │   ├── file_utils.py            # File handling utilities
│   │   └── rate_limiter.py          # Rate limiting implementation
│   │
│   ├── 📁 tasks/                     # Background tasks
│   │   ├── celery_app.py            # Celery configuration
│   │   ├── email_tasks.py           # Email sending tasks
│   │   ├── analysis_tasks.py        # Background analysis tasks
│   │   └── cleanup_tasks.py         # System cleanup tasks
│   │
│   └── main.py                      # FastAPI application entry point
│
├── 📁 tests/                         # Test suite
│   ├── 📁 test_api/                  # API endpoint tests
│   │   ├── test_auth.py             # Authentication tests
│   │   ├── test_users.py            # User API tests
│   │   ├── test_analyze.py          # Analysis API tests
│   │   └── test_jobs.py             # Job API tests
│   │
│   ├── 📁 test_services/             # Service layer tests
│   │   ├── test_ai_service.py       # AI service tests
│   │   ├── test_analysis_service.py # Analysis service tests
│   │   ├── test_user_service.py     # User service tests
│   │   └── test_job_service.py      # Job service tests
│   │
│   ├── 📁 test_ai/                   # AI integration tests
│   │   ├── test_openai.py           # OpenAI tests
│   │   ├── test_anthropic.py        # Anthropic tests
│   │   └── test_processors.py       # Document processor tests
│   │
│   ├── 📁 fixtures/                  # Test data and fixtures
│   │   ├── sample_resumes/          # Sample resume files
│   │   ├── test_data.py             # Test data generators
│   │   └── mocks.py                 # Mock objects
│   │
│   └── conftest.py                  # pytest configuration
│
├── 📁 frontend/                      # Frontend application (React/Next.js)
│   ├── 📁 src/
│   │   ├── 📁 components/           # React components
│   │   ├── 📁 pages/                # Page components
│   │   ├── 📁 hooks/                # Custom React hooks
│   │   ├── 📁 services/             # API service clients
│   │   ├── 📁 utils/                # Frontend utilities
│   │   └── 📁 styles/               # CSS and styling
│   │
│   ├── package.json                 # Node.js dependencies
│   ├── next.config.js               # Next.js configuration
│   └── tailwind.config.js           # Tailwind CSS configuration
│
├── 📁 mobile/                        # Mobile application (React Native)
│   ├── 📁 src/
│   │   ├── 📁 components/           # React Native components
│   │   ├── 📁 screens/              # App screens
│   │   ├── 📁 navigation/           # Navigation setup
│   │   ├── 📁 services/             # API services
│   │   └── 📁 utils/                # Mobile utilities
│   │
│   ├── package.json                 # React Native dependencies
│   ├── metro.config.js              # Metro bundler config
│   └── app.json                     # Expo configuration
│
├── 📁 docker/                        # Docker configurations
│   ├── Dockerfile                   # Main application Docker image
│   ├── Dockerfile.frontend          # Frontend Docker image
│   ├── docker-compose.yml           # Production compose file
│   ├── docker-compose.dev.yml       # Development compose file
│   └── nginx.conf                   # Nginx configuration
│
├── 📁 scripts/                       # Utility scripts
│   ├── deploy.sh                    # Deployment script
│   ├── setup-dev.sh                 # Development setup script
│   ├── backup.sh                    # Database backup script
│   ├── migrate.py                   # Database migration script
│   └── seed_data.py                 # Database seeding script
│
├── 📁 docs/                          # Documentation
│   ├── api/                         # API documentation
│   ├── deployment/                  # Deployment guides
│   ├── development/                 # Development guides
│   └── user_guide/                  # User documentation
│
├── 📁 config/                        # Configuration files
│   ├── nginx.conf                   # Nginx configuration
│   ├── prometheus.yml               # Prometheus configuration
│   ├── grafana/                     # Grafana dashboards
│   └── ssl/                         # SSL certificates
│
├── 📁 migrations/                    # Database migrations
│   ├── versions/                    # Migration versions
│   └── alembic.ini                  # Alembic configuration
│
├── 📄 requirements.txt               # Python dependencies
├── 📄 requirements-dev.txt           # Development dependencies
├── 📄 pyproject.toml                 # Python project configuration
├── 📄 .env.example                   # Environment variables template
├── 📄 .gitignore                     # Git ignore rules
├── 📄 .dockerignore                  # Docker ignore rules
├── 📄 cli.py                         # Command line interface
├── 📄 README.md                      # Project documentation
├── 📄 LICENSE                        # MIT License
└── 📄 CHANGELOG.md                   # Version history
```

## 🏗️ Architecture Layers

### 1. **API Layer** (`src/api/`)
- **FastAPI** routes organized by functionality
- **Request/Response** validation using Pydantic
- **Authentication** middleware and dependency injection
- **Rate limiting** and security controls
- **OpenAPI** documentation generation

### 2. **Business Logic Layer** (`src/services/`)
- **Service classes** containing business logic
- **AI integration** for resume analysis and job matching
- **User management** and subscription handling
- **File processing** and document analysis
- **Email notifications** and communication

### 3. **Data Layer** (`src/models/`)
- **SQLAlchemy** ORM models
- **Database relationships** and constraints
- **Data validation** at the model level
- **Audit trails** and timestamps
- **Soft deletes** and data integrity

### 4. **AI/ML Layer** (`src/ai/`)
- **Multi-model AI** integration (OpenAI, Anthropic, Hugging Face)
- **Document processing** (PDF, DOCX, TXT)
- **Prompt engineering** and template management
- **Model selection** and fallback strategies
- **Performance optimization** and caching

### 5. **Infrastructure Layer**
- **Database** management with PostgreSQL
- **Caching** with Redis for performance
- **File storage** with MinIO/S3 compatibility
- **Background tasks** using Celery
- **Monitoring** with Prometheus and Grafana

## 🔄 Data Flow

### Resume Analysis Flow
```
Upload Resume → File Processing → AI Analysis → Score Calculation → Result Storage → User Notification
```

### Job Matching Flow
```
User Profile → Skill Extraction → Job Database Search → AI Ranking → Match Scoring → Recommendations
```

### Authentication Flow
```
Login Request → Credential Validation → JWT Generation → Rate Limit Check → Access Grant
```

## 🛡️ Security Architecture

### Authentication & Authorization
- **JWT tokens** with refresh mechanism
- **Role-based access control** (RBAC)
- **Rate limiting** per user tier
- **Session management** with Redis
- **Password hashing** with bcrypt

### Data Protection
- **Input validation** at all entry points
- **SQL injection** prevention with ORM
- **XSS protection** with proper escaping
- **CORS** configuration for frontend access
- **Secure headers** implementation

### File Security
- **File type validation** and size limits
- **Virus scanning** for uploaded files
- **Secure file storage** with encryption
- **Access control** for file retrieval
- **Audit logging** for file operations

## 📊 Performance Optimizations

### Database
- **Connection pooling** for efficient database access
- **Query optimization** with proper indexing
- **Read replicas** for scaling read operations
- **Database migrations** for schema management
- **Backup strategies** for data recovery

### Caching Strategy
- **Redis caching** for frequently accessed data
- **HTTP caching** for static content
- **AI model caching** to reduce API costs
- **Session caching** for user data
- **Query result caching** for complex operations

### Background Processing
- **Celery workers** for asynchronous tasks
- **Task queuing** for heavy operations
- **Scheduled tasks** for maintenance
- **Error handling** and retry logic
- **Progress tracking** for long operations

## 🚀 Deployment Architecture

### Container Strategy
- **Multi-stage builds** for optimized images
- **Health checks** for container monitoring
- **Resource limits** for stability
- **Secret management** for sensitive data
- **Log aggregation** for debugging

### Orchestration
- **Docker Compose** for local development
- **Kubernetes** for production scaling
- **Load balancing** for high availability
- **Service discovery** for microservices
- **Auto-scaling** based on demand

### Monitoring & Observability
- **Application metrics** with Prometheus
- **Custom dashboards** with Grafana
- **Error tracking** with Sentry
- **Log management** with structured logging
- **Performance monitoring** with APM tools

## 🧪 Testing Strategy

### Test Coverage
- **Unit tests** for individual components
- **Integration tests** for API endpoints
- **End-to-end tests** for user workflows
- **Performance tests** for scalability
- **Security tests** for vulnerability assessment

### Test Data Management
- **Fixtures** for consistent test data
- **Mock services** for external dependencies
- **Database seeding** for integration tests
- **Test isolation** for reliable results
- **Continuous integration** with automated testing

This architecture provides a solid foundation for a scalable, maintainable, and secure ATS resume optimization platform. The modular design allows for easy extension and modification as requirements evolve.
