# Vehicle Damage Detection Mobile App

A modern React Native mobile app built with Expo for vehicle condition assessment.

## Features

- **Inspections Tab**: View all inspections in a beautiful list with pull-to-refresh
- **Inspect Tab**: Create new inspections with:
  - Car information form (name, model, year)
  - Multiple BEFORE images (camera or gallery)
  - Multiple AFTER images (camera or gallery)
  - Native device camera integration

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure API URL:
   - Open `config/api.ts`
   - Update `BASE_URL` to your backend API URL
   - For physical device testing, use your computer's IP address instead of `localhost`
     - Example: `http://192.168.1.100:8000`

3. Start the development server:
   ```bash
   npx expo start
   ```

4. Run on your device:
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app (for physical devices)

## Project Structure

```
mobile_app/
├── app/                    # Expo Router screens
│   ├── (tabs)/            # Tab navigation screens
│   │   ├── inspections.tsx    # Inspections list
│   │   └── inspect.tsx        # Inspection form
│   └── inspection-detail.tsx  # Inspection detail view
├── config/
│   └── api.ts             # API configuration (BASE_URL here!)
├── services/
│   └── api.ts             # API service functions
├── types/
│   └── api.ts             # TypeScript types
└── components/            # Reusable components
```

## API Configuration

All API calls use the base URL defined in `config/api.ts`. To change the API endpoint:

1. Open `config/api.ts`
2. Update the `BASE_URL` in `API_CONFIG`
3. The change will apply to all API calls automatically

## Permissions

The app requires:
- **Camera Permission**: To take photos of vehicles
- **Photo Library Permission**: To select images from gallery

These permissions are requested automatically when you try to use camera/gallery features.

## Development

- Uses Expo Router for file-based navigation
- TypeScript for type safety
- Modern React Native components
- Dark mode support
- Clean, maintainable code structure

## Troubleshooting

### Images not uploading
- Check that your API URL is correct in `config/api.ts`
- Ensure backend is running and accessible
- For physical devices, use IP address instead of `localhost`

### Camera not working
- Ensure camera permissions are granted
- Check `app.json` has `expo-image-picker` plugin configured

### API connection errors
- Verify backend is running
- Check network connectivity
- For iOS simulator, `localhost` works
- For Android emulator, use `10.0.2.2:8000` instead of `localhost:8000`
- For physical devices, use your computer's IP address
