import 'package:flutter/material.dart';

class SafetyBanner extends StatelessWidget {
  final VoidCallback onGetHelp;

  const SafetyBanner({super.key, required this.onGetHelp});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFDC2626).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFFDC2626).withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.info,
            color: Color(0xFFDC2626),
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'In Crisis?',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: const Color(0xFFDC2626),
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'If you\'re having thoughts of self-harm',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: onGetHelp,
            style: TextButton.styleFrom(
              backgroundColor: const Color(0xFFDC2626),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: const Text('Get Help'),
          ),
        ],
      ),
    );
  }
}
