import 'package:flutter/material.dart';

class FocusPointScreen extends StatefulWidget {
  const FocusPointScreen({super.key});

  @override
  State<FocusPointScreen> createState() => _FocusPointScreenState();
}

class _FocusPointScreenState extends State<FocusPointScreen> {
  final parts = {'ECM / PCM': false, 'Transmission': false, 'LED Headlights': false, 'Instrument Cluster': false, 'Tailgate': false};

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Focus Point')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('2019 Ford F-150 • Row 12 • VIN Pending', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const Card(child: ListTile(leading: Icon(Icons.timer), title: Text('KPI Timer Active'), subtitle: Text('Started automatically when Focus Point opened.'))),
          const Card(child: ListTile(leading: Icon(Icons.gps_fixed), title: Text('GPS Location Capture'), subtitle: Text('GPS-first location capture with manual yard/row confirmation.'))),
          const Text('Available Parts', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          for (final entry in parts.entries)
            CheckboxListTile(title: Text(entry.key), value: entry.value, onChanged: (value) => setState(() => parts[entry.key] = value ?? false)),
          FilledButton.icon(onPressed: () {}, icon: const Icon(Icons.save), label: const Text('SAVE')),
          OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.arrow_back), label: const Text('BACK')),
        ],
      ),
    );
  }
}
