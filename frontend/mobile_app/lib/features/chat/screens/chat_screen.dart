import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../shared/widgets/safety_banner.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [
    ChatMessage(
      id: 1,
      text: "Hello! I'm here to support you. How are you feeling today?",
      sender: MessageSender.ai,
      timestamp: DateTime.now(),
    ),
  ];
  bool _isTyping = false;

  final List<String> suggestionChips = [
    "I feel anxious",
    "Help me calm down",
    "Sleep tips",
    "Breathing exercise",
  ];

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _handleSend() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(
        id: _messages.length + 1,
        text: text,
        sender: MessageSender.user,
        timestamp: DateTime.now(),
      ));
      _isTyping = true;
    });

    _messageController.clear();
    _scrollToBottom();

    // Simulate AI response
    Future.delayed(const Duration(milliseconds: 1500), () {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            id: _messages.length + 1,
            text:
                "I understand. It's completely normal to feel this way. Would you like to try a grounding exercise, or would you prefer to talk about what's on your mind?",
            sender: MessageSender.ai,
            timestamp: DateTime.now(),
          ));
          _isTyping = false;
        });
        _scrollToBottom();
      }
    });
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(title: 'AI Assistant'),
      body: Column(
        children: [
          // Safety banner
          Padding(
            padding: const EdgeInsets.all(16),
            child: SafetyBanner(onGetHelp: () => context.go('/crisis')),
          ),

          // Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _messages.length +
                  (_isTyping ? 1 : 0) +
                  (_messages.length == 1 ? 1 : 0),
              itemBuilder: (context, index) {
                // Suggestion chips after first message
                if (_messages.length == 1 && index == _messages.length) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: suggestionChips.map((chip) {
                        return InkWell(
                          onTap: () {
                            _messageController.text = chip;
                            _handleSend();
                          },
                          child: Chip(
                            label: Text(chip),
                            backgroundColor: const Color(0xFFE8F4F2),
                            labelStyle: const TextStyle(
                              color: Color(0xFF1A1F36),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  );
                }

                // Typing indicator
                if (_isTyping && index == _messages.length) {
                  return _buildTypingIndicator();
                }

                // Messages
                final messageIndex =
                    _isTyping && index > _messages.length ? index - 1 : index;
                final message = _messages[messageIndex];
                return _buildMessageBubble(message);
              },
            ),
          ),

          // Input bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1,
                ),
              ),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                      ),
                      maxLines: null,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _handleSend(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    backgroundColor: Theme.of(context).primaryColor,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: _handleSend,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.sender == MessageSender.user;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? Theme.of(context).primaryColor
              : Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(
                color: isUser ? Colors.white : null,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${message.timestamp.hour.toString().padLeft(2, '0')}:${message.timestamp.minute.toString().padLeft(2, '0')}',
              style: TextStyle(
                fontSize: 10,
                color: isUser
                    ? Colors.white.withOpacity(0.7)
                    : Theme.of(context).textTheme.bodySmall?.color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(
            3,
            (index) => Container(
              margin: EdgeInsets.only(left: index > 0 ? 4 : 0),
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: Theme.of(context).textTheme.bodySmall?.color,
                shape: BoxShape.circle,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class ChatMessage {
  final int id;
  final String text;
  final MessageSender sender;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.text,
    required this.sender,
    required this.timestamp,
  });
}

enum MessageSender { user, ai }
