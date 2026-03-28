import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';

class ToolsScreen extends StatefulWidget {
  const ToolsScreen({super.key});

  @override
  State<ToolsScreen> createState() => _ToolsScreenState();
}

class _ToolsScreenState extends State<ToolsScreen> {
  late SharedPreferences prefs;
  Set<int> favoriteTools = {};

  @override
  void initState() {
    super.initState();
    _loadFavorites();
  }

  Future<void> _loadFavorites() async {
    prefs = await SharedPreferences.getInstance();
    final saved = prefs.getStringList('favoriteTools') ?? [];
    setState(() {
      favoriteTools = saved.map(int.parse).toSet();
    });
  }

  Future<void> _toggleFavorite(int toolId) async {
    prefs = await SharedPreferences.getInstance();
    setState(() {
      if (favoriteTools.contains(toolId)) {
        favoriteTools.remove(toolId);
      } else {
        favoriteTools.add(toolId);
      }
    });
    await prefs.setStringList(
      'favoriteTools',
      favoriteTools.map((id) => id.toString()).toList(),
    );
  }

  void _showToolDetailsDialog(Tool tool) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Icon(
                    tool.icon,
                    size: 28,
                    color: tool.color,
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                tool.name,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                tool.description,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: tool.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Duration: ${tool.duration}',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: tool.color,
                  ),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(context);
                    context.go(tool.route);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: tool.color,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: const Text(
                    'Start Now',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final categories = [
      ToolCategory(
        id: 1,
        name: 'Breathing',
        icon: Icons.air,
        color: const Color(0xFF4DB8A8),
        bgColor: const Color(0xFF4DB8A8).withOpacity(0.1),
        tools: [
          Tool(
            id: 101,
            name: 'Box Breathing',
            icon: Icons.air,
            color: const Color(0xFF4DB8A8),
            description: 'A grounding breathing technique to calm anxiety',
            duration: '5 minutes',
            route: '/tools/breathing-bubble',
          ),
          Tool(
            id: 102,
            name: '4-7-8 Technique',
            icon: Icons.air,
            color: const Color(0xFF4DB8A8),
            description: 'Deep breathing pattern known for relaxation',
            duration: '8 minutes',
            route: '/tools/breathing-bubble',
          ),
          Tool(
            id: 103,
            name: 'Deep Breathing',
            icon: Icons.air,
            color: const Color(0xFF4DB8A8),
            description: 'Simple deep breathing for stress relief',
            duration: '5 minutes',
            route: '/tools/breathing-bubble',
          ),
        ],
      ),
      ToolCategory(
        id: 2,
        name: 'Games',
        icon: Icons.games,
        color: const Color(0xFF7B68EE),
        bgColor: const Color(0xFF7B68EE).withOpacity(0.1),
        tools: [
          Tool(
            id: 201,
            name: 'Calm Puzzle',
            icon: Icons.games,
            color: const Color(0xFF7B68EE),
            description: 'Arrange puzzle pieces smoothly with no time pressure',
            duration: 'No Time Limit',
            route: '/tools/calm-puzzle',
          ),
          Tool(
            id: 203,
            name: 'Creative Drawing',
            icon: Icons.brush,
            color: const Color(0xFF7B68EE),
            description: 'Free-form drawing for creative expression',
            duration: 'No Time Limit',
            route: '/tools/drawing',
          ),
        ],
      ),
      ToolCategory(
        id: 3,
        name: 'Sleep & Relaxation',
        icon: Icons.bedtime,
        color: const Color(0xFF8B5CF6),
        bgColor: const Color(0xFF8B5CF6).withOpacity(0.1),
        tools: [
          Tool(
            id: 301,
            name: 'Sleep Stories',
            icon: Icons.auto_stories,
            color: const Color(0xFF8B5CF6),
            description: 'Calming stories to help you sleep peacefully',
            duration: '20-30 minutes',
            route: '/tools/sleep-stories',
          ),
          Tool(
            id: 302,
            name: 'Guided Relaxation',
            icon: Icons.spa,
            color: const Color(0xFF8B5CF6),
            description: 'Progressive muscle relaxation technique',
            duration: '15 minutes',
            route: '/tools/guided-relaxation',
          ),
          Tool(
            id: 303,
            name: 'White Noise',
            icon: Icons.nightlight,
            color: const Color(0xFF8B5CF6),
            description: 'Ambient sounds for deep, restful sleep',
            duration: 'No Time Limit',
            route: '/tools/white-noise',
          ),
        ],
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
                          const Text(
                            'Calm Puzzle Game',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w700,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'No rush, no timer, no pressure - just calm',
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[700],
                            ),
                          ),
                        ],
                      ),
                      GestureDetector(
                        onTap: () => _toggleFavorite(201),
                        child: Icon(
                          favoriteTools.contains(201)
                              ? Icons.favorite
                              : Icons.favorite_border,
                          color: favoriteTools.contains(201)
                              ? const Color(0xFFDC2626)
                              : Colors.grey,
                          size: 24,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => _showToolDetailsDialog(
                        categories[1].tools[0], // Calm Puzzle
                      ),
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
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: Colors.black87,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    ...category.tools.map((tool) {
                      final isFavorite = favoriteTools.contains(tool.id);
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
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
                                      tool.name,
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.black87,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      tool.duration,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  GestureDetector(
                                    onTap: () => _toggleFavorite(tool.id),
                                    child: Icon(
                                      isFavorite
                                          ? Icons.favorite
                                          : Icons.favorite_border,
                                      color: isFavorite
                                          ? const Color(0xFFDC2626)
                                          : Colors.grey,
                                      size: 20,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  ElevatedButton(
                                    onPressed: () =>
                                        _showToolDetailsDialog(tool),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: tool.color,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16,
                                        vertical: 8,
                                      ),
                                    ),
                                    child: const Text(
                                      'Start',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ],
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
  final List<Tool> tools;

  ToolCategory({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.bgColor,
    required this.tools,
  });
}

class Tool {
  final int id;
  final String name;
  final IconData icon;
  final Color color;
  final String description;
  final String duration;
  final String route;

  Tool({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
    required this.description,
    required this.duration,
    required this.route,
  });
}

