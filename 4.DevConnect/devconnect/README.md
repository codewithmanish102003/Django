# DevConnect - Developer Networking Platform

A comprehensive Django-based platform for developers to connect, collaborate, and build professional relationships. This project demonstrates advanced Django concepts including DRF, WebSockets, Celery, and more.

## 🚀 Features

### Core Functionality
- **User Authentication & Profiles**: Custom user model with developer-specific fields
- **Real-time Chat**: WebSocket-based messaging with Django Channels
- **User Discovery**: Advanced search and filtering for finding developers
- **Professional Networking**: Connection management and profile interactions

### Advanced Django Concepts Demonstrated

#### 1. Django REST Framework (DRF)
- **Serializers**: Data transformation and validation
- **ViewSets**: CRUD operations with automatic URL generation
- **Routers**: Auto-generated API endpoints
- **JWT Authentication**: Secure API access with token-based auth
- **Permissions & Throttling**: Access control and rate limiting

#### 2. Real-time Communication
- **WebSockets**: Real-time chat and notifications
- **Django Channels**: Asynchronous communication support
- **Chat Rooms**: Individual and group conversations
- **Live Notifications**: Instant updates for users

#### 3. Background Tasks & Celery
- **Task Queue**: Asynchronous job processing
- **Email Sending**: Welcome emails, notifications, digests
- **Report Generation**: User and system analytics
- **Data Cleanup**: Automated maintenance tasks
- **External API Integration**: GitHub data synchronization

#### 4. Database Optimization
- **Query Optimization**: `select_related()` and `prefetch_related()`
- **Database Indexes**: Strategic indexing for performance
- **Pagination**: Efficient data loading
- **Connection Management**: Optimized database queries

#### 5. Internationalization (i18n)
- **Multi-language Support**: English, Spanish, French, German
- **Dynamic Language Switching**: User preference management
- **Localized Content**: Translated strings and messages

#### 6. Security & Permissions
- **Custom User Model**: Extended authentication
- **Permission Classes**: Role-based access control
- **JWT Tokens**: Secure API authentication
- **CORS Configuration**: Cross-origin request handling

## 🏗️ Project Structure

```
devconnect/
├── devconnect/          # Main project settings
│   ├── settings.py     # Django configuration
│   ├── urls.py         # Main URL routing
│   ├── asgi.py         # ASGI configuration for WebSockets
│   └── celery.py       # Celery configuration
├── users/              # User management app
│   ├── models.py       # Custom user model
│   ├── views.py        # Authentication views
│   ├── forms.py        # User forms
│   └── admin.py        # Admin interface
├── profiles/           # Main application app
│   ├── views.py        # Profile and discovery views
│   └── urls.py         # Profile URL routing
├── api/                # REST API app
│   ├── serializers.py  # Data serialization
│   ├── views.py        # API views and viewsets
│   └── urls.py         # API URL routing
├── chat/               # Real-time chat app
│   ├── models.py       # Chat models
│   ├── consumers.py    # WebSocket consumers
│   ├── views.py        # Chat views
│   └── routing.py      # WebSocket routing
├── notifications/      # Notification system
│   ├── models.py       # Notification models
│   └── admin.py        # Notification admin
├── tasks/              # Background tasks
│   ├── tasks.py        # Celery task definitions
│   └── apps.py         # Task app configuration
├── static/             # Static files
├── media/              # User uploads
├── templates/          # HTML templates
├── locale/             # Translation files
└── requirements.txt    # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Redis server
- PostgreSQL (recommended) or SQLite
- Node.js (for frontend assets)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd devconnect
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost/devconnect
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Database Setup
```bash
# For PostgreSQL
createdb devconnect

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Start Redis Server
```bash
# On macOS with Homebrew
brew services start redis

# On Ubuntu/Debian
sudo systemctl start redis

# On Windows, download and run Redis server
```

### 8. Start Celery Workers
```bash
# Start Celery worker
celery -A devconnect worker -l info

# Start Celery beat (in another terminal)
celery -A devconnect beat -l info
```

### 9. Run the Development Server
```bash
python manage.py runserver
```

## 🚀 Running the Application

### Development Mode
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A devconnect worker -l info

# Terminal 3: Celery beat
celery -A devconnect beat -l info

# Terminal 4: Redis server (if not running as service)
redis-server
```

### Production Mode
```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn devconnect.wsgi:application

# Use Daphne for WebSocket support
daphne devconnect.asgi:application
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### User Endpoints
- `GET /api/users/` - List users (admin only)
- `GET /api/users/{id}/` - Get user details
- `POST /api/users/` - Create new user
- `PATCH /api/users/{id}/` - Update user
- `GET /api/users/search/` - Search users
- `GET /api/users/suggestions/` - User suggestions

### Chat Endpoints
- `GET /chat/` - Chat home
- `GET /chat/conversation/{id}/` - Conversation details
- `POST /chat/api/conversation/{id}/send/` - Send message

### WebSocket Endpoints
- `ws/chat/{room_name}/` - Chat room WebSocket
- `ws/notifications/` - Notifications WebSocket

## 🔧 Configuration Options

### Django Settings
- **Database**: Configure your preferred database backend
- **Email**: Set up SMTP for email notifications
- **Static Files**: Configure static and media file serving
- **CORS**: Adjust allowed origins for your frontend

### Celery Configuration
- **Broker**: Redis configuration for task queue
- **Result Backend**: Redis for task results
- **Task Routing**: Configure task queues
- **Beat Schedule**: Set up periodic tasks

### Channels Configuration
- **Backend**: Redis or in-memory channel layers
- **WebSocket**: Configure WebSocket routing

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific app tests
python manage.py test users
python manage.py test api
```

### Test Configuration
```bash
# Install test dependencies
pip install pytest pytest-django factory-boy

# Run with pytest
pytest
```

## 📊 Monitoring & Logging

### Celery Monitoring
- **Flower**: Web-based monitoring tool
- **Celery Beat**: Schedule monitoring
- **Task Results**: Track task execution

### Django Logging
- **File Logging**: Application logs
- **Console Logging**: Development output
- **Error Tracking**: Sentry integration

## 🌐 Internationalization

### Supported Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)

### Adding New Languages
1. Add language to `LANGUAGES` in settings
2. Create translation files in `locale/` directory
3. Compile messages: `python manage.py compilemessages`

## 🔒 Security Features

- **JWT Authentication**: Secure API access
- **Permission Classes**: Role-based access control
- **CORS Protection**: Cross-origin request handling
- **Rate Limiting**: API request throttling
- **Input Validation**: Form and serializer validation

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up monitoring and logging
- [ ] Configure SSL/TLS certificates
- [ ] Set up backup systems

### Docker Support
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t devconnect .
docker run -p 8000:8000 devconnect
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code examples

## 🔮 Future Enhancements

- **Mobile App**: React Native or Flutter app
- **Advanced Analytics**: User behavior tracking
- **AI Recommendations**: Smart user matching
- **Video Calls**: WebRTC integration
- **Project Management**: Built-in project tools
- **Payment Integration**: Freelancer payments

---

**DevConnect** - Connecting developers, building the future together! 🚀
