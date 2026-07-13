import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('RecyclerOS Pro')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Login', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          const TextField(
            decoration: InputDecoration(labelText: 'Email', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 12),
          const TextField(
            obscureText: true,
            decoration: InputDecoration(labelText: 'Password', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => context.go('/workspace-select'),
            icon: const Icon(Icons.login),
            label: const Text('Continue'),
          ),
        ],
      ),
    );
  }
}
