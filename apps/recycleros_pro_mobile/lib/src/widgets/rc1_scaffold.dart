import 'package:flutter/material.dart';

class Rc1Scaffold extends StatelessWidget {
  const Rc1Scaffold({
    required this.title,
    required this.body,
    this.actions,
    super.key,
  });

  final String title;
  final Widget body;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title), actions: actions),
      body: SafeArea(
        child: Align(
          alignment: Alignment.topCenter,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 920),
            child: SizedBox(width: double.infinity, child: body),
          ),
        ),
      ),
    );
  }
}

class PageHeader extends StatelessWidget {
  const PageHeader({required this.title, this.detail, super.key});

  final String title;
  final String? detail;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
        if (detail != null) ...[
          const SizedBox(height: 4),
          Text(detail!, style: textTheme.bodyMedium),
        ],
      ],
    );
  }
}
