import 'package:flutter/material.dart';

ThemeData buildRecyclerOSTheme() {
  final base = ColorScheme.fromSeed(
    seedColor: const Color(0xFF1F5C4A),
    brightness: Brightness.light,
  );
  final colors = base.copyWith(
    primary: const Color(0xFF1F5C4A),
    secondary: const Color(0xFFB66A1E),
    surface: const Color(0xFFF8FAF9),
    surfaceContainerHighest: const Color(0xFFE4E9E7),
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: colors,
    scaffoldBackgroundColor: const Color(0xFFF1F4F3),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFFF8FAF9),
      foregroundColor: Color(0xFF18332B),
      centerTitle: false,
      elevation: 0,
    ),
    inputDecorationTheme: const InputDecorationTheme(
      border: OutlineInputBorder(),
      filled: true,
      fillColor: Color(0xFFFFFFFF),
    ),
    dividerTheme: const DividerThemeData(color: Color(0xFFD4DBD8)),
  );
}
