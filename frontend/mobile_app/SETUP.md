# Flutter Frontend Setup - Quick Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd frontend/mobile_app
flutter pub get
```

### Step 2: Configure Environment

```bash
# Windows
copy lib\core\config\env.example.dart lib\core\config\env.dart

# Linux/Mac
cp lib/core/config/env.example.dart lib/core/config/env.dart
```

### Step 3: Update Backend URL

Edit `lib/core/config/env.dart`:

**For local development (same machine):**

```dart
static const String apiBaseUrl = 'http://localhost:8000';
```

**For Android emulator:**

```dart
static const String apiBaseUrl = 'http://10.0.2.2:8000';
```

**For physical device on same network:**

```dart
static const String apiBaseUrl = 'http://192.168.x.x:8000';  // Your computer's IP
```

### Step 4: Verify Backend is Running

```bash
# Check backend health
curl http://localhost:8000/health
```

Should return:

```json
{ "status": "healthy", "version": "1.0.0", "environment": "development" }
```

### Step 5: Run the App

```bash
# Connect your device or start emulator first
flutter devices

# Run app
flutter run
```

## 🎯 Common Issues

### Issue: "Could not resolve Environment"

**Solution:** Make sure `env.dart` exists

```bash
copy lib\core\config\env.example.dart lib\core\config\env.dart
```

### Issue: Backend connection fails on Android emulator

**Solution:** Use `10.0.2.2` instead of `localhost`

```dart
static const String apiBaseUrl = 'http://10.0.2.2:8000';
```

### Issue: Flutter not found

**Solution:** Install Flutter SDK

```bash
# Download from: https://docs.flutter.dev/get-started/install
flutter doctor
```

### Issue: No devices available

**Solution:**

- Start Android emulator: Android Studio → AVD Manager
- Or connect physical device with USB debugging enabled
- Or use web: `flutter run -d chrome`

## 📱 Quick Commands

```bash
# Check Flutter installation
flutter doctor

# List available devices
flutter devices

# Run app
flutter run

# Run on specific device
flutter run -d <device-id>

# Hot reload (while app is running)
# Press 'r' in terminal

# Build APK
flutter build apk
```

## 🔧 Environment Switching

**Development (default):**

```bash
# Already configured in env.dart
```

**Staging:**

```bash
copy lib\core\config\env.staging.dart lib\core\config\env.dart
```

**Production:**

```bash
copy lib\core\config\env.production.dart lib\core\config\env.dart
```

## ✅ Verification Checklist

- [ ] Flutter SDK installed (`flutter doctor` passes)
- [ ] Dependencies installed (`flutter pub get` successful)
- [ ] `env.dart` file exists with correct backend URL
- [ ] Backend is running and accessible
- [ ] Device/emulator is connected
- [ ] App runs successfully

## 🚀 You're Ready!

Your Flutter app should now be running and able to connect to the backend API.

Next steps:

- Explore the app features
- Check [README.md](README.md) for detailed documentation
- Start developing!
