import 'package:flutter/material.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';

class ToolsScreen extends StatelessWidget {
  const ToolsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final categories = [
      ToolCategory(
        id: 1,
        name: 'Breathing',
        icon: Icons.air,
        color: const Color(0xFF4DB8A8),
        bgColor: const Color(0xFF4DB8A8).withOpacity(0.1),
        tools: const ['Box Breathing', '4-7-8 Technique', 'Deep Breathing'],
      ),
      ToolCategory(
        id: 2,
        name: 'Sleep',
        icon: Icons.nightlight,
        color: Theme.of(context).primaryColor,
        bgColor: Theme.of(context).primaryColor.withOpacity(0.1),
        tools: const ['Sleep Stories', 'Relaxation', 'White Noise'],
      ),
      ToolCategory(
        id: 3,
        name: 'Anxiety',
        icon: Icons.psychology,
        color: const Color(0xFFF59E0B),
        bgColor: const Color(0xFFF59E0B).withOpacity(0.1),
        tools: const [
          'Grounding 5-4-3-2-1',
          'Progressive Relaxation',
          'Guided Meditation'
        ],
      ),
      ToolCategory(
        id: 4,
        name: 'Focus',
        icon: Icons.center_focus_strong,
        color: const Color(0xFF10B981),
        bgColor: const Color(0xFF10B981).withOpacity(0.1),
        tools: const ['Pomodoro Timer', 'Mindful Breathing', 'Body Scan'],
      ),
    ];

    return Scaffold(
      appBar: const CustomAppBar(title: 'Wellness Tools'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Featured tool
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Theme.of(context).primaryColor.withOpacity(0.1),
                    const Color(0xFFE8F4F2),
                    const Color(0xFF4DB8A8).withOpacity(0.1),
                  ],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.auto_awesome,
                                size: 16,
                                color: Theme.of(context).primaryColor,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                'Featured',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Theme.of(context).primaryColor,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '5-Minute Calm',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Quick breathing exercise to reduce stress',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                      const Icon(Icons.favorite_border, size: 24),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {},
                      child: const Text('Start now'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Categories
            ...categories.map((category) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: category.bgColor,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            category.icon,
                            color: category.color,
                            size: 20,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          category.name,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    ...category.tools.map((tool) {
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
                                      tool,
                                      style:
                                          Theme.of(context).textTheme.bodyLarge,
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '5-10 minutes',
                                      style:
                                          Theme.of(context).textTheme.bodySmall,
                                    ),
                                  ],
                                ),
                              ),
                              OutlinedButton(
                                onPressed: () {},
                                child: const Text('Start'),
                              ),
                            ],
                          ),
                        ),
                      );
                    }),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 2),
    );
  }
}

class ToolCategory {
  final int id;
  final String name;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final List<String> tools;

  ToolCategory({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.bgColor,
    required this.tools,
  });
}
