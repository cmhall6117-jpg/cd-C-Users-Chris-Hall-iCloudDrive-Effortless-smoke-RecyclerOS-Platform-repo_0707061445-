import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_routes.dart';
import '../../state/rc1_workflow.dart';
import '../../widgets/rc1_scaffold.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _continue() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    ref.read(rc1WorkflowProvider.notifier).signIn(_emailController.text);
    context.go(AppPaths.workspace);
  }

  @override
  Widget build(BuildContext context) {
    return Rc1Scaffold(
      title: 'RecyclerOS Pro',
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const PageHeader(title: 'Sign in', detail: 'Effortless Smoke operations'),
          const SizedBox(height: 24),
          Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  key: const Key('emailField'),
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  autofillHints: const [AutofillHints.email],
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.alternate_email),
                  ),
                  validator: (value) {
                    final email = value?.trim() ?? '';
                    return email.contains('@') ? null : 'Enter a valid email.';
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  key: const Key('passwordField'),
                  controller: _passwordController,
                  obscureText: true,
                  textInputAction: TextInputAction.done,
                  autofillHints: const [AutofillHints.password],
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    prefixIcon: Icon(Icons.lock_outline),
                  ),
                  validator: (value) => (value ?? '').isEmpty
                      ? 'Enter your password.'
                      : null,
                  onFieldSubmitted: (_) => _continue(),
                ),
                const SizedBox(height: 20),
                FilledButton.icon(
                  key: const Key('loginContinue'),
                  onPressed: _continue,
                  icon: const Icon(Icons.login),
                  label: const Text('Continue'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
