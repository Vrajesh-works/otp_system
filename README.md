# OTP System with SMS Delivery Status

A robust FastAPI-based OTP (One-Time Password) system with SMS delivery tracking, built with PostgreSQL for secure and scalable authentication.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- ✅ **6-digit OTP Generation** - Secure random OTP codes
- ✅ **5-minute Expiration** - Automatic OTP expiry for security
- ✅ **Rate Limiting** - Maximum 3 verification attempts per OTP
- ✅ **SMS Delivery Tracking** - Complete delivery status callbacks
- ✅ **Template Management** - Customizable SMS templates
- ✅ **RESTful API** - Clean and well-documented endpoints
- ✅ **PostgreSQL Database** - Reliable data persistence
- ✅ **Auto-invalidation** - Previous OTPs automatically invalidated
- ✅ **Comprehensive Logging** - Full audit trail
- ✅ **Interactive Documentation** - Swagger UI and ReDoc

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0.23
- **Database Driver**: psycopg2-binary 2.9.9
- **Validation**: Pydantic 2.5.0
- **ASGI Server**: Uvicorn 0.24.0
- **Environment**: Python 3.8+

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12 or higher** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **pip** (Python package manager) - Comes with Python
- **Git** (optional) - For cloning the repository

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/otp_system.git
cd otp_system
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 2. Edit Configuration

Open `.env` and update with your settings:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/otp_system

# Application Settings
APP_NAME=OTP System API
APP_VERSION=1.0.0
DEBUG=True

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*

# OTP Settings
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
MAX_OTP_ATTEMPTS=3

# SMS Provider (Optional - for actual SMS sending)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## 🗄️ Database Setup

### 1. Create Database

**Using psql:**
```bash
psql -U postgres
CREATE DATABASE otp_system;
\q
```

**Using pgAdmin:**
1. Open pgAdmin 4
2. Right-click "Databases" → Create → Database
3. Name: `otp_system`
4. Save

### 2. Run Database Schema

**Option A - Automatic (Recommended):**
```bash
python seed_data.py
```

**Option B - Manual:**
```bash
psql -U postgres -d otp_system -f schema.sql
```

### 3. Verify Tables

```bash
psql -U postgres -d otp_system -c "\dt"
```

You should see:
- `otps`
- `sms_delivery_statuses`
- `sms_templates`

## 🏃 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the Application

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test all endpoints directly in your browser.

## 🔌 API Endpoints

### OTP Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/otp/generate` | Generate and send OTP |
| POST | `/api/otp/verify` | Verify OTP code |
| GET | `/api/otp/history/{phone_number}` | Get OTP history |

### SMS Delivery

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sms/callback` | SMS delivery status webhook |
| GET | `/api/sms/status/{message_id}` | Get SMS delivery status |

### Template Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/templates` | Create SMS template |
| GET | `/api/templates` | Get all templates |
| GET | `/api/templates/{template_type}` | Get template by type |

## 🧪 Testing

### Quick Test Using cURL

**1. Generate OTP:**
```bash
curl -X POST "http://localhost:8000/api/otp/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "template_type": "login"
  }'
```

**2. Verify OTP:**
```bash
curl -X POST "http://localhost:8000/api/otp/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'
```

### Test Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

### Check OTP in Database

```bash
psql -U postgres -d otp_system
SELECT * FROM otps ORDER BY created_at DESC LIMIT 5;
```

## 📁 Project Structure

```
otp_system/
├── main.py                 # FastAPI application and endpoints
├── models.py              # SQLAlchemy database models
├── database.py            # Database configuration
├── seed_data.py           # Database seeding script
├── schema.sql             # PostgreSQL schema
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .env.example          # Example environment file
├── README.md             # This file
└── venv/                 # Virtual environment (git ignored)
```

## 🔒 Security Features

- **OTP Expiration**: Automatic 5-minute expiry
- **Rate Limiting**: Maximum 3 verification attempts
- **Auto-invalidation**: Previous OTPs invalidated on new generation
- **Secure Random**: Cryptographically secure OTP generation
- **Input Validation**: Pydantic validation on all inputs
- **Phone Format**: Country code validation
- **CORS Configuration**: Configurable origin restrictions

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
# Windows:
services.msc  # Find postgresql service

# macOS/Linux:
sudo service postgresql status
```

### Port Already in Use

```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Or use different port:
uvicorn main:app --reload --port 8001
```

### Module Not Found

```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Cannot Import SQLAlchemy

```bash
# Install manually
pip install sqlalchemy psycopg2-binary
```

## 📊 Database Statistics

Check system statistics:

```sql
-- OTP generation rate
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as otp_count
FROM otps
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- SMS delivery success rate
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM sms_delivery_statuses
GROUP BY status;
```

## 🚀 Production Deployment

### Using Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:pass@prod-host:5432/otp_system
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
```

### Using Systemd (Linux)

```ini
[Unit]
Description=OTP System API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/otp_system
Environment="PATH=/var/www/otp_system/venv/bin"
ExecStart=/var/www/otp_system/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

## 🔄 SMS Provider Integration

### Twilio Example

```python
from twilio.rest import Client

def send_sms(phone_number, message, message_id):
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )
    
    message = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=phone_number,
        status_callback=f"{os.getenv('API_URL')}/api/sms/callback"
    )
    return message.sid
```

Install Twilio:
```bash
pip install twilio
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Twilio SMS API](https://www.twilio.com/docs/sms)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust database ORM
- PostgreSQL for reliable data storage
- The Python community for amazing tools

---

## 📞 Support

If you have any questions or need help, please:

- Open an issue on GitHub
- Check the [Troubleshooting](#troubleshooting) section
- Review the [API Documentation](#api-documentation)

---

**Made with ❤️ using FastAPI and PostgreSQL**

---

## 📈 Roadmap

- [ ] Add JWT authentication
- [ ] Implement Redis caching
- [ ] Add email OTP support
- [ ] Create admin dashboard
- [ ] Add Docker support
- [ ] Implement rate limiting with Redis
- [ ] Add unit tests
- [ ] Create CI/CD pipeline
- [ ] Add monitoring with Prometheus
- [ ] Implement backup strategies

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Last Updated**: November 2025