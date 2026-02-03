import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/mood_selector.dart';
import '../../../shared/widgets/action_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(
        subtitle: 'Good morning,',
        title: 'Jordan',
        showAvatar: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Daily check-in card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Theme.of(context).primaryColor.withOpacity(0.05),
                    const Color(0xFF4DB8A8).withOpacity(0.05),
                  ],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'How are you feeling today?',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),
                  MoodSelector(
                    onSelect: (value) {
                      debugPrint('Mood selected: $value');
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Quick actions
            Text(
              'Quick Actions',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            GridView.count(
              crossAxisCount: 4,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 16,
              crossAxisSpacing: 12,
              children: [
                ActionCard(
                  icon: Icons.chat_bubble,
                  label: 'Talk to AI',
                  color: Theme.of(context).primaryColor,
                  bgColor: Theme.of(context).primaryColor.withOpacity(0.1),
                  onTap: () => context.go('/chat'),
                ),
                ActionCard(
                  icon: Icons.air,
                  label: 'Breathing',
                  color: const Color(0xFF4DB8A8),
                  bgColor: const Color(0xFF4DB8A8).withOpacity(0.1),
                  onTap: () => context.go('/tools'),
                ),
                ActionCard(
                  icon: Icons.anchor,
                  label: 'Grounding',
                  color: const Color(0xFF1A1F36),
                  bgColor: const Color(0xFFE8F4F2),
                  onTap: () => context.go('/tools'),
                ),
                ActionCard(
                  icon: Icons.phone,
                  label: 'Emergency',
                  color: const Color(0xFFDC2626),
                  bgColor: const Color(0xFFDC2626).withOpacity(0.1),
                  onTap: () => context.go('/crisis'),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Your Progress
            Text(
              'Your Progress',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(
                              Icons.local_fire_department,
                              color: Color(0xFF10B981),
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '7',
                                style: Theme.of(context).textTheme.displaySmall,
                              ),
                              Text(
                                'Day streak',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: Theme.of(context)
                                  .primaryColor
                                  .withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              Icons.calendar_today,
                              color: Theme.of(context).primaryColor,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '12',
                                style: Theme.of(context).textTheme.displaySmall,
                              ),
                              Text(
                                'Sessions',
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Suggested tool
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFE8F4F2).withOpacity(0.5),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Suggested for you',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Try a 5-minute breathing exercise',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => context.go('/tools'),
                    child: const Text('Start'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 0),
    );
  }
}
