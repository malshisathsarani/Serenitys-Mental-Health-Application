# Serenity - Mental Health Mobile App (Flutter)

A compassionate mental health wellness companion mobile application built with Flutter.

## 📁 Project Structure

```
lib/
├── core/                   # Core functionality
│   ├── config/            # Environment configuration
│   │   ├── config.dart    # Config exports
│   │   ├── env.dart       # Active environment (gitignored)
│   │   ├── env.example.dart
│   │   ├── env.production.dart
│   │   └── env.staging.dart
│   ├── routes/            # App routing
│   └── theme/             # App theming
├── features/              # Feature modules
│   ├── auth/             # Authentication
│   ├── chat/             # Chat functionality
│   ├── crisis/           # Crisis support
│   ├── home/             # Home screen
│   ├── onboarding/       # User onboarding
│   ├── profile/          # User profile
│   ├── splash/           # Splash screen
│   └── tools/            # Mental health tools
├── shared/               # Shared components
│   └── widgets/          # Reusable widgets
└── main.dart             # App entry point
```

## 🚀 Quick Start

### Prerequisites

- Flutter SDK 3.0.0+
- Dart SDK 3.0.0+
- Android Studio / VS Code

### Setup

1. **Install dependencies**:

```bash
flutter pub get
```

2. **Configure environment**:

```bash
# Windows
copy lib\core\config\env.example.dart lib\core\config\env.dart

# Linux/Mac
cp lib/core/config/env.example.dart lib/core/config/env.dart
```

3. **Update backend URL** in `lib/core/config/env.dart`:

```dart
static const String apiBaseUrl = 'http://localhost:8000';  // Your backend URL
```

4. **Run the app**:

```bash
flutter run
```

## 🔧 Environment Configuration

The app uses environment-specific configuration files in `lib/core/config/`:

| File                  | Purpose       | Committed?         |
| --------------------- | ------------- | ------------------ |
| `env.example.dart`    | Template      | ✅ Yes             |
| `env.dart`            | Active config | ❌ No (gitignored) |
| `env.staging.dart`    | Staging       | ✅ Yes             |
| `env.production.dart` | Production    | ✅ Yes             |

**Usage in code:**

```dart
import 'package:serenity/core/config/config.dart';

final apiUrl = Environment.apiBaseUrl;
final isDebug = Environment.isDebug;
```

## 📱 Running & Building

```bash
# Development
flutter run

# Release build (Android)
flutter build apk --release

# App bundle (Google Play)
flutter build appbundle --release

# iOS (requires macOS)
flutter build ios --release
```

## 🧪 Testing

```bash
# Run tests
flutter test

# With coverage
flutter test --coverage
```

## 🔒 Security Notes

**DO NOT commit:**

- `lib/core/config/env.dart` (environment config)
- `android/key.properties` (signing keys)
- `*.jks`, `*.keystore` (Android keystores)
- API keys or secrets

**Build artifacts are gitignored:**

- `build/` folder
- Platform-specific generated files
- Gradle wrapper and build files

## 🛠️ Development Tips

### Android Emulator Network

- Use `http://10.0.2.2:8000` to access localhost from Android emulator
- Update `apiBaseUrl` in `env.dart`

### Hot Reload

- Press `r` for hot reload (instant UI updates)
- Press `R` for hot restart (full app restart)

### Code Quality

```bash
flutter analyze          # Check for issues
flutter format .         # Format code
flutter pub outdated     # Check outdated packages
```

## 🐛 Troubleshooting

**Backend connection fails:**

- Ensure backend is running: `curl http://localhost:8000/health`
- For Android emulator: use `http://10.0.2.2:8000`

**Build fails:**

```bash
flutter clean
flutter pub get
flutter run
```

**"Could not resolve Environment" error:**

- Make sure `env.dart` exists (copy from `env.example.dart`)

## 📚 Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Language](https://dart.dev/guides)
- [Flutter Widget Catalog](https://docs.flutter.dev/development/ui/widgets)

## 📦 Dependencies

Key packages:

- `go_router` - Navigation
- `provider` - State management
- `shared_preferences` - Local storage
- `url_launcher` - External links
- `flutter_svg` - SVG support

See `pubspec.yaml` for complete list.

## 🚀 Production Checklist

- [ ] Configure production API URL
- [ ] Set up proper error handling
- [ ] Implement API service layer
- [ ] Add authentication
- [ ] Enable crash reporting
- [ ] Add analytics
- [ ] Implement offline support
- [ ] Set up CI/CD
- [ ] Configure app signing
- [ ] Test on multiple devices

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Run `flutter format .` and `flutter analyze`
4. Test your changes
5. Submit pull request

## 📄 License

[Your License Here]
