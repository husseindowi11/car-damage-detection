# 🚗 Car Damage Detection System

An AI-powered vehicle inspection system that automatically detects and analyzes damage by comparing before and after photos. Perfect for car rental companies, fleet management, and vehicle condition assessments.

## 🌐 Live Demo & Resources

- **🔗 Production API**: [https://car-damage-detection-x3i7.onrender.com/](https://car-damage-detection-x3i7.onrender.com/)
- **📖 API Documentation**: [https://car-damage-detection-x3i7.onrender.com/docs](https://car-damage-detection-x3i7.onrender.com/docs)
- **📱 Android APK**: *Coming soon - check releases*

---

## 📱 What Does This App Do?

Imagine you're running a car rental business. Every time a customer returns a vehicle, you need to check if there's any new damage. This usually means:
- Walking around the car with a clipboard
- Manually noting every scratch, dent, or crack
- Estimating repair costs
- Taking photos for records

**This app automates all of that!**

Simply:
1. **Take "BEFORE" photos** when the customer picks up the car
2. **Take "AFTER" photos** when they return it
3. **Let AI do the work** - It compares the photos and instantly tells you:
   - What's damaged (bumper, door, headlight, etc.)
   - How bad it is (minor scratch, major dent)
   - Where exactly on the car (with highlighted images)
   - How much it will cost to fix

No manual inspection needed. Save time, reduce disputes, and never miss damage again!

---

## 🛠️ Technology Stack

### Backend (Python/FastAPI)
- **FastAPI** - Modern, fast web framework
- **Google Gemini AI** - Vision AI for damage detection
- **SQLite** - Database for inspection records
- **Pillow** - Image processing and annotation

### Mobile App (React Native/Expo)
- **Expo** - React Native development platform
- **TypeScript** - Type-safe code
- **Expo Router** - File-based navigation
- **expo-image-picker** - Camera and gallery access

---

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, make sure you have:
- **Python 3.13+** installed
- **Node.js 18+** and npm installed
- **Google Gemini API Key** ([Get one free here](https://ai.google.dev/))
- A smartphone (iOS or Android) or emulator for testing

---

## 🖥️ Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_actual_api_key_here
```

To get your Gemini API key:
1. Go to [https://ai.google.dev/](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new project or use existing
4. Copy the API key and paste it in `.env`

### 5. Run the Backend
```bash
python main.py
```

The backend will start at `http://localhost:8000`

**Test it**: Open [http://localhost:8000/api/health](http://localhost:8000/api/health) in your browser. You should see:
```json
{"status": "healthy", "message": "API is running"}
```

**View API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

---

## 📱 Mobile App Setup

### 1. Navigate to Mobile App Directory
```bash
cd mobile_app
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure API Connection

**Important**: The mobile app needs to know where your backend is running.

Open `mobile_app/config/api.ts` and update the base URL:

**For iOS Simulator:**
```typescript
return `http://localhost:8000`;
```

**For Android Emulator:**
```typescript
return `http://10.0.2.2:8000`;
```

**For Physical Device (iOS or Android):**
```typescript
return `http://YOUR_COMPUTER_IP:8000`;
```

To find your computer's IP:
- **Mac/Linux**: Run `ifconfig | grep "inet " | grep -v 127.0.0.1`
- **Windows**: Run `ipconfig` and look for IPv4 Address
- Example: `192.168.1.100`

### 4. Start the Development Server
```bash
npx expo start
```

### 5. Run on Your Device

After starting Expo, you'll see a QR code. Choose your platform:

**Option A: Physical Device (Recommended)**
1. Install **Expo Go** app:
   - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
2. Scan the QR code with:
   - iOS: Camera app
   - Android: Expo Go app
3. App will load on your device

**Option B: Emulator/Simulator**
- Press `i` for iOS Simulator (Mac only, requires Xcode)
- Press `a` for Android Emulator (requires Android Studio)

---

## 📖 How to Use the App

### Creating Your First Inspection

1. **Open the app** - You'll see two tabs at the bottom:
   - 📋 **Inspections**: View past inspections
   - 📷 **Inspect**: Create new inspection

2. **Tap "Inspect"** to start a new inspection

3. **Fill in car details**:
   - Car Name (e.g., "Toyota Camry")
   - Model (e.g., "SE", "XLE")
   - Year (e.g., "2023")

4. **Take BEFORE photos** (customer picking up car):
   - Tap "Take Photo" to use camera
   - Or tap "Choose from Library" to select existing photos
   - Take multiple angles (front, rear, sides)
   - Minimum 1 photo required

5. **Take AFTER photos** (customer returning car):
   - Same as above - multiple angles recommended
   - Try to match the same angles as BEFORE photos

6. **Submit**:
   - Tap "Submit Inspection"
   - Wait for AI analysis (may take 30-60 seconds)
   - You'll be redirected to the results

7. **View Results**:
   - See detected damages with descriptions
   - View estimated repair costs
   - Check annotated images with damage highlights
   - Total cost summary and inspection status

### Viewing Past Inspections

1. Go to **Inspections** tab
2. See all inspections sorted by date
3. Tap any inspection to view full details
4. Pull down to refresh the list

---

## 🔧 Troubleshooting

### Backend Issues

**Error: "GEMINI_API_KEY not found"**
- Make sure `.env` file exists in `backend/` folder
- Check that `GEMINI_API_KEY=your_key` is in the file (no spaces around `=`)
- Restart the backend after adding the key

**Error: "ModuleNotFoundError"**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Port 8000 already in use**
- Another app is using port 8000
- Stop the other app or change port in `main.py`

### Mobile App Issues

**Error: "Network request failed" / Timeout**
- Check that backend is running (`http://localhost:8000/api/health`)
- Verify the API URL in `config/api.ts` is correct
- For physical device: Make sure phone and computer are on the same WiFi
- Try increasing timeout in `services/api.ts` (already set to 3 minutes)

**Images not uploading**
- Grant camera/photo permissions when prompted
- Check image file size (very large images may fail)
- Ensure stable internet connection

**App not loading on physical device**
- Ensure phone and computer are on same WiFi network
- Check firewall isn't blocking port 8000
- Try restarting Expo dev server

---

## 🏗️ Project Structure

```
car-damage-detection/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Entry point
│   ├── models/                # Database models & schemas
│   ├── services/              # Business logic (AI, inspection)
│   ├── utils/                 # Helper functions
│   ├── uploads/               # Stored images (gitignored)
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables (create this)
│
├── mobile_app/                # React Native Mobile App
│   ├── app/                   # Screens (Expo Router)
│   │   ├── (tabs)/           # Tab navigation
│   │   │   ├── inspect.tsx   # Create inspection
│   │   │   └── inspections.tsx # List inspections
│   │   └── inspection-detail.tsx # View details
│   ├── components/            # Reusable components
│   ├── config/                # Configuration (API URL)
│   ├── services/              # API calls
│   ├── types/                 # TypeScript types
│   └── package.json           # Node dependencies
│
└── README.md                  # This file
```

---

## 🌟 Features in Detail

### AI-Powered Detection
- Compares multiple before/after images
- Detects dents, scratches, cracks, broken parts
- Generates bounding boxes around damage
- Provides severity assessment (minor, moderate, major)

### Cost Estimation
- Industry-standard pricing
- Labor costs ($60-$120/hr)
- Material costs per panel
- Part replacement estimates
- Total damage summary

### Inspection Status
- **PASS**: No significant damage
- **MINOR_REPAIR**: Small damage, repair recommended
- **MAJOR_REPAIR**: Significant damage requiring attention
- **TOTAL_LOSS**: Damage exceeds vehicle value

### Mobile Experience
- Native camera integration
- Multiple image upload
- Beautiful gradient UI
- Pull-to-refresh
- Image preview with full-screen modal
- Tab-based navigation for image viewing

---

## 📄 API Endpoints

### Health Check
```
GET /api/health
```

### Create Inspection
```
POST /api/inspect
Content-Type: multipart/form-data

Form Data:
- car_name: string
- car_model: string
- car_year: integer
- before_images: file[] (multiple files)
- after_images: file[] (multiple files)
```

### List Inspections
```
GET /api/inspections
```

### Get Inspection Details
```
GET /api/inspections/{inspection_id}
```

**Full API documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (when backend is running)

---

## 🔐 Security Notes

- Never commit `.env` file to version control
- API keys are kept secure in environment variables
- Uploaded images are stored locally in gitignored folders
- CORS is configured for development (adjust for production)

---

## 🚀 Deployment

### Backend (Render.com)
Already deployed at: [https://car-damage-detection-x3i7.onrender.com/](https://car-damage-detection-x3i7.onrender.com/)

### Mobile App (Build APK)
```bash
cd mobile_app
npx expo build:android
```

Or use EAS Build:
```bash
eas build --platform android --profile production
```

---

## 📝 Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---


## 🎯 Future Enhancements

- [ ] iOS App (TestFlight/App Store)
- [ ] User authentication
- [ ] Multi-language support
- [ ] Export reports as PDF
- [ ] Email notifications
- [ ] Fleet management dashboard
- [ ] Historical damage tracking per vehicle
- [ ] Integration with insurance systems

---

## 💡 Tips for Best Results

1. **Lighting**: Take photos in good lighting conditions
2. **Angles**: Capture all sides of the vehicle (front, rear, both sides)
3. **Consistency**: Try to match before/after photo angles
4. **Distance**: Stand at the same distance for before/after shots
5. **Focus**: Ensure images are clear and in focus
6. **Coverage**: Don't miss any part of the vehicle