import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../shared/widgets/custom_app_bar.dart';

class CrisisScreen extends StatefulWidget {
  const CrisisScreen({super.key});

  @override
  State<CrisisScreen> createState() => _CrisisScreenState();
}

class _CrisisScreenState extends State<CrisisScreen> {
  String? _selectedContact;

  final List<EmergencyContact> emergencyContacts = const [
    EmergencyContact(
      id: 1,
      name: 'National Crisis Hotline',
      number: '988',
    ),
    EmergencyContact(
      id: 2,
      name: 'Crisis Text Line',
      number: '741741',
      isTextLine: true,
    ),
    EmergencyContact(
      id: 3,
      name: 'Emergency Services',
      number: '911',
    ),
  ];

  final List<SavedContact> savedContacts = const [
    SavedContact(
      id: 1,
      name: 'Dr. Sarah Johnson',
      role: 'Therapist',
      number: '(555) 123-4567',
    ),
    SavedContact(
      id: 2,
      name: 'Mom',
      role: 'Emergency Contact',
      number: '(555) 234-5678',
    ),
  ];

  Future<void> _makePhoneCall(String phoneNumber) async {
    final Uri launchUri = Uri(
      scheme: 'tel',
      path: phoneNumber,
    );
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    }
  }

  Future<void> _handleCallClick(String name, String number,
      {bool isTextLine = false}) async {
    if (isTextLine) {
      final Uri smsUri = Uri(
        scheme: 'sms',
        path: number,
        queryParameters: {'body': 'HOME'},
      );
      if (await canLaunchUrl(smsUri)) {
        await launchUrl(smsUri);
      }
    } else {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Confirm Call'),
          content: Text('Call $name at $number?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _makePhoneCall(number);
              },
              child: const Text('Call'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: 'Crisis Support',
        action: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Emergency message
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFFDC2626).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFFDC2626).withOpacity(0.2),
                  width: 2,
                ),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.favorite,
                    color: Color(0xFFDC2626),
                    size: 48,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'You matter',
                    style: Theme.of(context).textTheme.headlineSmall,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'If you\'re in crisis, please reach out. Help is available 24/7.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).textTheme.bodySmall?.color,
                        ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Primary action
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: () =>
                    _handleCallClick('National Crisis Hotline', '988'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.phone),
                    SizedBox(width: 8),
                    Text('Get help now - Call 988'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Emergency contacts
            Text(
              'Emergency Resources',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            ...emergencyContacts.map((contact) {
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              contact.name,
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              contact.isTextLine
                                  ? 'Text HOME to ${contact.number}'
                                  : contact.number,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                      OutlinedButton(
                        onPressed: () => _handleCallClick(
                          contact.name,
                          contact.number,
                          isTextLine: contact.isTextLine,
                        ),
                        child: Row(
                          children: [
                            Icon(
                                contact.isTextLine
                                    ? Icons.message
                                    : Icons.phone,
                                size: 16),
                            const SizedBox(width: 4),
                            Text(contact.isTextLine ? 'Text' : 'Call'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: 24),

            // Saved contacts
            Text(
              'Your Contacts',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            ...savedContacts.map((contact) {
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              contact.name,
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              contact.role,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                      OutlinedButton(
                        onPressed: () =>
                            _handleCallClick(contact.name, contact.number),
                        child: Row(
                          children: const [
                            Icon(Icons.phone, size: 16),
                            SizedBox(width: 4),
                            Text('Call'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class EmergencyContact {
  final int id;
  final String name;
  final String number;
  final bool isTextLine;

  const EmergencyContact({
    required this.id,
    required this.name,
    required this.number,
    this.isTextLine = false,
  });
}

class SavedContact {
  final int id;
  final String name;
  final String role;
  final String number;

  const SavedContact({
    required this.id,
    required this.name,
    required this.role,
    required this.number,
  });
}
