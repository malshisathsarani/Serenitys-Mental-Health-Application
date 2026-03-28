import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../core/services/api_service.dart'
    show ApiService, EmergencyContact, SavedContact, EmergencyContactResponse;

class CrisisScreen extends StatefulWidget {
  const CrisisScreen({super.key});

  @override
  State<CrisisScreen> createState() => _CrisisScreenState();
}

class _CrisisScreenState extends State<CrisisScreen> {
  final ApiService _apiService = ApiService();
  String? _selectedContact;
  List<EmergencyContact> emergencyContacts = [];
  List<SavedContact> savedContacts = [];
  bool _isLoading = true;
  String? _error;

  // Form controllers for adding contact
  late TextEditingController _nameController;
  late TextEditingController _phoneController;
  late TextEditingController _relationshipController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _phoneController = TextEditingController();
    _relationshipController = TextEditingController();
    _loadEmergencyContacts();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _relationshipController.dispose();
    super.dispose();
  }

  Future<void> _loadEmergencyContacts() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final contacts = await _apiService.getEmergencyContacts();

      // Separate hotlines from personal contacts
      final hotlines = <EmergencyContact>[];
      final personal = <SavedContact>[];

      for (final contact in contacts) {
        if (contact.isHotline) {
          hotlines.add(contact.toEmergencyContact());
        } else {
          personal.add(contact.toSavedContact());
        }
      }

      if (mounted) {
        setState(() {
          emergencyContacts = hotlines;
          savedContacts = personal;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
          // Show default crisis hotlines on error
          _loadDefaultContacts();
        });
      }
    }
  }

  void _loadDefaultContacts() {
    emergencyContacts = const [
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
    savedContacts = const [
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
  }

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

  void _showAddContactDialog() {
    // Clear previous values
    _nameController.clear();
    _phoneController.clear();
    _relationshipController.clear();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Emergency Contact'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Contact Name',
                  hintText: 'e.g., Mom, Dad, Best Friend',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _relationshipController,
                decoration: const InputDecoration(
                  labelText: 'Relationship (optional)',
                  hintText: 'e.g., Family, Friend, Therapist',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone Number',
                  hintText: '+1 555 123 4567 or (555) 123-4567',
                  helperText: 'Include country code with +',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.phone,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (_validateContactForm()) {
                Navigator.pop(context);
                _addContact();
              }
            },
            child: const Text('Add Contact'),
          ),
        ],
      ),
    );
  }

  bool _validateContactForm() {
    if (_nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter contact name')),
      );
      return false;
    }
    if (_phoneController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter phone number')),
      );
      return false;
    }
    return true;
  }

  Future<void> _addContact() async {
    try {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Adding contact...')),
      );

      await _apiService.addEmergencyContact(
        name: _nameController.text,
        phoneNumber: _phoneController.text,
        contactRelationship: _relationshipController.text.isNotEmpty
            ? _relationshipController.text
            : null,
        isHotline: false,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Contact added successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        // Refresh the contact list
        _loadEmergencyContacts();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error adding contact: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
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
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Error banner if loading failed
                  if (_error != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.orange.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.orange.withOpacity(0.3),
                        ),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.warning, color: Colors.orange),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Using default contacts',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ),
                        ],
                      ),
                    ),
                  if (_error != null) const SizedBox(height: 16),
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

                  // Saved contacts header with add button
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        savedContacts.isEmpty
                            ? 'Your Contacts'
                            : 'Your Contacts (${savedContacts.length})',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      IconButton(
                        icon: const Icon(Icons.add_circle),
                        onPressed: _showAddContactDialog,
                        tooltip: 'Add Emergency Contact',
                        constraints: const BoxConstraints(),
                        padding: EdgeInsets.zero,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Saved contacts list
                  if (savedContacts.isEmpty)
                    Center(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          'No contacts added yet',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ),
                    )
                  else
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

