import 'package:flutter/material.dart';

class AppTheme {
  // Color palette
  static const Color primaryColor = Color(0xFF2D5AA6);
  static const Color secondaryColor = Color(0xFF4DB8A8);
  static const Color accentColor = Color(0xFFE8F4F2);
  static const Color destructiveColor = Color(0xFFDC2626);
  static const Color warningColor = Color(0xFFF59E0B);
  static const Color successColor = Color(0xFF10B981);

  // Light theme colors
  static const Color lightBackground = Color(0xFFFAFBFC);
  static const Color lightForeground = Color(0xFF1A1F36);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightMuted = Color(0xFFF0F1F3);
  static const Color lightMutedForeground = Color(0xFF6B7280);
  static const Color lightBorder = Color(0x14000000);
  static const Color lightInputBackground = Color(0xFFF8F9FA);

  // Dark theme colors
  static const Color darkBackground = Color(0xFF0F1419);
  static const Color darkForeground = Color(0xFFF0F1F3);
  static const Color darkCard = Color(0xFF1A1F36);
  static const Color darkMuted = Color(0xFF2A2F45);
  static const Color darkMutedForeground = Color(0xFF9CA3AF);
  static const Color darkBorder = Color(0x1FFFFFFF);
  static const Color darkInputBackground = Color(0xFF1F2937);

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primaryColor,
    scaffoldBackgroundColor: lightBackground,
    colorScheme: const ColorScheme.light(
      primary: primaryColor,
      secondary: secondaryColor,
      surface: lightCard,
      error: destructiveColor,
      onPrimary: Colors.white,
      onSecondary: lightForeground,
      onSurface: lightForeground,
      onError: Colors.white,
    ),

    // Text theme
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: lightForeground,
      ),
      displayMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: lightForeground,
      ),
      displaySmall: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: lightForeground,
      ),
      headlineMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: lightForeground,
      ),
      headlineSmall: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: lightForeground,
      ),
      titleLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: lightForeground,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: lightForeground,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: lightForeground,
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: lightMutedForeground,
      ),
    ),

    // Card theme
    cardTheme: CardThemeData(
      color: lightCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: lightBorder, width: 1),
      ),
    ),

    // AppBar theme
    appBarTheme: const AppBarTheme(
      backgroundColor: lightBackground,
      foregroundColor: lightForeground,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: lightForeground,
      ),
    ),

    // Input decoration theme
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: lightInputBackground,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      hintStyle: const TextStyle(color: lightMutedForeground),
    ),

    // Button themes
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: lightForeground,
        side: const BorderSide(color: lightBorder),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),

    // Bottom navigation bar theme
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: lightCard,
      selectedItemColor: primaryColor,
      unselectedItemColor: lightMutedForeground,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),

    fontFamily: 'Inter',
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primaryColor,
    scaffoldBackgroundColor: darkBackground,
    colorScheme: const ColorScheme.dark(
      primary: primaryColor,
      secondary: secondaryColor,
      surface: darkCard,
      error: destructiveColor,
      onPrimary: Colors.white,
      onSecondary: darkForeground,
      onSurface: darkForeground,
      onError: Colors.white,
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: darkForeground,
      ),
      displayMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: darkForeground,
      ),
      displaySmall: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: darkForeground,
      ),
      headlineMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: darkForeground,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.normal,
        color: darkForeground,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.normal,
        color: darkForeground,
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.normal,
        color: darkMutedForeground,
      ),
    ),
    cardTheme: CardThemeData(
      color: darkCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: darkBorder, width: 1),
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: darkBackground,
      foregroundColor: darkForeground,
      elevation: 0,
      centerTitle: false,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: darkInputBackground,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      hintStyle: const TextStyle(color: darkMutedForeground),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: darkCard,
      selectedItemColor: primaryColor,
      unselectedItemColor: darkMutedForeground,
      type: BottomNavigationBarType.fixed,
    ),
    fontFamily: 'Inter',
  );
}
