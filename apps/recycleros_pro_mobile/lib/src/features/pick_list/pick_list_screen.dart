import 'package:flutter/material.dart';

class PickListScreen extends StatelessWidget {
  const PickListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vehicles = [
      ('Greenville Pull-A-Part', 'Row 12', '2019', 'Ford', 'F-150', 'VIN pending'),
      ('Greenville Pull-A-Part', 'Row 12', '2017', 'Chevrolet', 'Silverado', 'VIN pending'),
      ('Greenville Pull-A-Part', 'Row 14', '2018', 'Toyota', 'Camry', 'VIN pending'),
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Pick List Entry')),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          const Text('Pick List Entry', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const Text('Showing up to 10 line items per yard batch.'),
          const SizedBox(height: 12),
          for (final v in vehicles)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('${v.$3} ${v.$4} ${v.$5}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text('Yard: ${v.$1} • Row: ${v.$2}'),
                  Text('VIN: ${v.$6}'),
                  Row(children: [
                    Expanded(child: FilledButton(onPressed: () {}, child: const Text('Available'))),
                    const SizedBox(width: 8),
                    Expanded(child: OutlinedButton(onPressed: () {}, child: const Text('Unavailable'))),
                  ])
                ]),
              ),
            ),
        ],
      ),
    );
  }
}
