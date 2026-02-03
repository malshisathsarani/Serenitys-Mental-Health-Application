import 'package:flutter/material.dart';

class MoodSelector extends StatefulWidget {
  final Function(int) onSelect;

  const MoodSelector({super.key, required this.onSelect});

  @override
  State<MoodSelector> createState() => _MoodSelectorState();
}

class _MoodSelectorState extends State<MoodSelector> {
  int? selectedMood;

  final List<MoodOption> moods = [
    MoodOption(emoji: '😊', label: 'Great', value: 5),
    MoodOption(emoji: '🙂', label: 'Good', value: 4),
    MoodOption(emoji: '😐', label: 'Okay', value: 3),
    MoodOption(emoji: '😔', label: 'Low', value: 2),
    MoodOption(emoji: '😢', label: 'Bad', value: 1),
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: moods.map((mood) {
        final isSelected = selectedMood == mood.value;
        return GestureDetector(
          onTap: () {
            setState(() {
              selectedMood = mood.value;
            });
            widget.onSelect(mood.value);
          },
          child: Column(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: isSelected
                      ? Theme.of(context).primaryColor.withOpacity(0.1)
                      : Colors.transparent,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isSelected
                        ? Theme.of(context).primaryColor
                        : Colors.transparent,
                    width: 2,
                  ),
                ),
                child: Center(
                  child: Text(
                    mood.emoji,
                    style: const TextStyle(fontSize: 32),
                  ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                mood.label,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

class MoodOption {
  final String emoji;
  final String label;
  final int value;

  MoodOption({
    required this.emoji,
    required this.label,
    required this.value,
  });
}
