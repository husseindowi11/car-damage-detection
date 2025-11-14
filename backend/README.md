# Vehicle Damage Detection Backend

AI-powered vehicle condition assessment API for car rental companies using Google Gemini Vision.

## 🚀 Features

- Compare BEFORE/AFTER vehicle images
- Detect new damages automatically using AI
- Generate detailed damage reports with cost estimates
- REST API for mobile app integration
- Annotated image output
- Comprehensive Swagger/OpenAPI documentation

## 📋 Prerequisites

- Python 3.7+
- Google Gemini API key

## 🔧 Installation

1. **Create virtual environment:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## 🏃 Running the Server

### Development
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Render deployment)
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI
Visit **`http://localhost:8000/docs`** for interactive Swagger documentation where you can:
- View all available endpoints
- See request/response schemas
- Test endpoints directly in the browser
- View example requests and responses

### ReDoc
Visit **`http://localhost:8000/redoc`** for beautiful, responsive API documentation

### OpenAPI JSON
Visit **`http://localhost:8000/openapi.json`** for the raw OpenAPI specification

## 🔌 API Endpoints

### `GET /`
Root endpoint - API information

**Response:**
```json
{
  "message": "Vehicle Damage Detection API",
  "version": "1.0.0",
  "status": "running"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "vehicle-damage-detection",
  "ai_service": "google-gemini-vision"
}
```

### `POST /inspect`
Analyze vehicle images for damage detection

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `before`: Image file (JPEG, PNG, WEBP) - Vehicle at pickup
  - `after`: Image file (JPEG, PNG, WEBP) - Vehicle at return

**Response:**
```json
{
  "success": true,
  "inspection_id": "550e8400-e29b-41d4-a716-446655440000",
  "report": {
    "new_damage": [
      {
        "car_part": "rear bumper",
        "damage_type": "dent",
        "severity": "moderate",
        "recommended_action": "repair",
        "estimated_cost_usd": 350.0,
        "description": "Dent on rear bumper, approximately 3 inches in diameter"
      }
    ],
    "total_estimated_cost_usd": 350.0,
    "summary": "1 new damage detected on rear bumper"
  },
  "annotated_image_base64": "base64_encoded_image_string...",
  "saved_images": {
    "before": "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/before.jpg",
    "after": "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/after.jpg"
  }
}
```

## 🧪 Testing with cURL

```bash
curl -X POST "http://localhost:8000/inspect" \
  -F "before=@path/to/before.jpg" \
  -F "after=@path/to/after.jpg"
```

## 🧪 Testing with Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Open `http://localhost:8000/docs` in your browser
3. Click on the `/inspect` endpoint
4. Click "Try it out"
5. Upload your BEFORE and AFTER images
6. Click "Execute"
7. View the response with full schema validation

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── models/
│   ├── __init__.py
│   └── schemas.py       # Pydantic models for API schemas
├── services/
│   ├── __init__.py
│   └── ai_service.py    # Google Gemini integration
├── utils/
│   ├── __init__.py
│   ├── file_handler.py  # File upload handling
│   └── validators.py    # Input validation
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Environment variables (not in git)
└── README.md           # This file
```

## 🌐 Deployment

### Render.com (Free Tier)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GEMINI_API_KEY`
6. Deploy!

After deployment, access Swagger docs at: `https://your-app.onrender.com/docs`

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `PORT` | Server port | No (default: 8000) |
| `ENVIRONMENT` | Environment name | No (default: development) |
| `LOG_LEVEL` | Logging level | No (default: INFO) |

## 📝 API Documentation Features

The API includes comprehensive Swagger documentation with:

- **Request/Response Models**: Full Pydantic schemas for type validation
- **Examples**: Example requests and responses for each endpoint
- **Error Responses**: Documented error codes and messages
- **Tags**: Organized endpoints by category (inspection, health)
- **Descriptions**: Detailed descriptions for each endpoint
- **Interactive Testing**: Test endpoints directly from the browser

## 📝 License

MIT License - Built for AI-Powered Vehicle Condition Assessment Challenge

