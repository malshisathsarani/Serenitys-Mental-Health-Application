import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:record/record.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../shared/widgets/custom_app_bar.dart';
import '../../../shared/widgets/safety_banner.dart';
import '../../../core/services/api_service.dart';
import '../../../core/services/emergency_settings_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ApiService _apiService = ApiService();
  final AudioRecorder _audioRecorder = AudioRecorder();
  final List<ChatMessage> _messages = [
    ChatMessage(
      id: 1,
      text: "Hello! I'm here to support you. How are you feeling today?",
      sender: MessageSender.ai,
      timestamp: DateTime.now(),
    ),
  ];
  bool _isTyping = false;
  /// Server conversation id; set after first successful send (Phase 1 threading).
  int? _serverConversationId;
  bool _isRecording = false;
  StreamSubscription<Uint8List>? _recordingSub;
  final List<int> _recordedBytes = [];
  double? _pendingVoiceRiskScore;
  bool? _pendingVoiceCrisisDetected;
  String? _voiceStatus;
  final Set<int> _submittedFeedbackMessageIds = <int>{};
  final EmergencySettingsService _emergencySettingsService =
      EmergencySettingsService();

  final List<String> suggestionChips = [
    "I feel anxious",
    "Help me calm down",
    "Sleep tips",
    "Breathing exercise",
  ];

  @override
  void dispose() {
    _recordingSub?.cancel();
    _audioRecorder.dispose();
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _submitMessageFeedback({
    required int messageId,
    required bool helpful,
  }) async {
    if (_submittedFeedbackMessageIds.contains(messageId)) return;
    try {
      await _apiService.submitFeedback(messageId: messageId, helpful: helpful);
      if (mounted) {
        setState(() {
          _submittedFeedbackMessageIds.add(messageId);
        });
      }
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Thanks for your feedback.')),
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not submit feedback right now.')),
      );
    }
  }

  void _handleSend() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    // Add user message
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

    try {
      // Get conversation history (last 5 messages for context)
      final history = _messages
          .where((m) => m.sender == MessageSender.user)
          .map((m) => m.text)
          .toList()
          .reversed
          .take(5)
          .toList()
          .reversed
          .toList();

      // Call backend API
      final response = await _apiService.sendMessage(
        text,
        conversationHistory: history,
        conversationId: _serverConversationId,
        voiceRiskScore: _pendingVoiceRiskScore,
        voiceCrisisDetected: _pendingVoiceCrisisDetected,
      );

      // Add AI response
      if (mounted) {
        setState(() {
          _serverConversationId = response.conversationId;
          _messages.add(ChatMessage(
            id: _messages.length + 1,
            text: response.response,
            sender: MessageSender.ai,
            timestamp: DateTime.now(),
            prediction: response.prediction,
            crisisDetected: response.crisisDetected,
            serverAssistantMessageId: response.assistantMessageId,
          ));
          _isTyping = false;
          _pendingVoiceRiskScore = null;
          _pendingVoiceCrisisDetected = null;
          _voiceStatus = null;

          // Show crisis alert if detected
          if (response.crisisDetected) {
            _showCrisisAlert(response.crisisResources);
            _triggerAutoEmergencyPromptIfEnabled();
          }
        });
        _scrollToBottom();
      }
    } catch (e) {
      // Handle error
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            id: _messages.length + 1,
            text:
                "I'm having trouble connecting right now. Please check your connection and try again. If you're in crisis, please call emergency services or a crisis hotline.",
            sender: MessageSender.ai,
            timestamp: DateTime.now(),
          ));
          _isTyping = false;
        });
        _scrollToBottom();
      }
    }
  }

  Future<void> _triggerAutoEmergencyPromptIfEnabled() async {
    final settings = await _emergencySettingsService.load();
    if (!settings.autoPromptEnabled) return;
    if (!mounted) return;

    final hotline = settings.hotlineNumber.trim();
    if (hotline.isEmpty) return;
    await _showEmergencyCountdownDialog(
      hotlineNumber: hotline,
      contactNumber: settings.emergencyContactNumber.trim(),
      countdownSec: settings.autoPromptCountdownSec,
    );
  }

  Future<void> _showEmergencyCountdownDialog({
    required String hotlineNumber,
    required String contactNumber,
    required int countdownSec,
  }) async {
    int secondsLeft = countdownSec;
    Timer? timer;
    bool didLaunch = false;

    Future<void> launchHotline() async {
      if (didLaunch) return;
      didLaunch = true;
      timer?.cancel();
      final uri = Uri(scheme: 'tel', path: hotlineNumber);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
    }

    await showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            timer ??= Timer.periodic(const Duration(seconds: 1), (t) {
              secondsLeft -= 1;
              if (secondsLeft <= 0) {
                t.cancel();
                Navigator.of(dialogContext).pop();
                launchHotline();
                return;
              }
              setDialogState(() {});
            });
            return AlertDialog(
              title: const Text('Emergency action countdown'),
              content: Text(
                'High-risk detected. Calling $hotlineNumber in $secondsLeft seconds.\n'
                'Tap Cancel to stop.\n'
                '${contactNumber.isNotEmpty ? 'Backup contact: $contactNumber' : ''}',
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    timer?.cancel();
                    Navigator.of(dialogContext).pop();
                  },
                  child: const Text('Cancel'),
                ),
                ElevatedButton(
                  onPressed: () async {
                    Navigator.of(dialogContext).pop();
                    await launchHotline();
                  },
                  child: const Text('Call now'),
                ),
              ],
            );
          },
        );
      },
    );
    timer?.cancel();
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _stopRecordingAndAnalyze();
      return;
    }
    await _startRecording();
  }

  Future<void> _startRecording() async {
    try {
      final hasPermission = await _audioRecorder.hasPermission();
      if (!hasPermission) {
        if (mounted) {
          setState(() {
            _voiceStatus = 'Microphone permission is required.';
          });
        }
        return;
      }

      _recordedBytes.clear();
      final stream = await _audioRecorder.startStream(
        const RecordConfig(
          encoder: AudioEncoder.pcm16bits,
          sampleRate: 16000,
          numChannels: 1,
        ),
      );

      _recordingSub = stream.listen((chunk) {
        _recordedBytes.addAll(chunk);
      });

      if (mounted) {
        setState(() {
          _isRecording = true;
          _voiceStatus = 'Recording voice... tap mic to stop.';
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _voiceStatus = 'Could not start recording.';
        });
      }
    }
  }

  Future<void> _stopRecordingAndAnalyze() async {
    try {
      await _audioRecorder.stop();
      await _recordingSub?.cancel();
      _recordingSub = null;

      if (mounted) {
        setState(() {
          _isRecording = false;
          _voiceStatus = 'Analyzing voice signal...';
        });
      }

      if (_recordedBytes.isEmpty) {
        if (mounted) {
          setState(() {
            _voiceStatus = 'No voice captured. Try recording again.';
          });
        }
        return;
      }

      final analysis = await _apiService.analyzeVoiceBytes(
        Uint8List.fromList(_recordedBytes),
        filename: 'voice.pcm',
      );

      if (mounted) {
        setState(() {
          _pendingVoiceRiskScore = analysis.voiceRiskScore;
          _pendingVoiceCrisisDetected = analysis.voiceCrisisDetected;
          _voiceStatus =
              'Voice ready: risk ${(analysis.voiceRiskScore * 100).toStringAsFixed(0)}% (attached to next message)';
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _isRecording = false;
          _voiceStatus = 'Voice analysis failed. You can still send text.';
        });
      }
    }
  }

  void _showCrisisAlert(Map<String, dynamic>? resources) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning, color: Colors.red),
            SizedBox(width: 8),
            Text('Crisis Support Available'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'We noticed you may be in distress. Please consider reaching out to a crisis helpline:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (resources != null && resources['hotlines'] != null)
              ...((resources['hotlines'] as List).map((hotline) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text('• $hotline'),
                  ))),
            const SizedBox(height: 8),
            const Text(
              'Or call emergency services: 911 (US)',
              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => context.go('/crisis'),
            child: const Text('Get Help Now'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Continue Chat'),
          ),
        ],
      ),
    );
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
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_voiceStatus != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(
                          _voiceStatus!,
                          style: TextStyle(
                            fontSize: 12,
                            color: _isRecording ? Colors.red : Colors.black54,
                          ),
                        ),
                      ),
                    ),
                  Row(
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
                        backgroundColor:
                            _isRecording ? Colors.red : Colors.blueGrey,
                        child: IconButton(
                          icon: Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            color: Colors.white,
                          ),
                          onPressed: _toggleRecording,
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
              : message.crisisDetected
                  ? Colors.red.shade50
                  : Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(16),
          border: message.crisisDetected
              ? Border.all(color: Colors.red, width: 2)
              : null,
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
            if (message.prediction != null && !isUser) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Analysis: ${message.prediction}',
                  style: const TextStyle(fontSize: 10, color: Colors.black54),
                ),
              ),
            ],
            if (!isUser && message.serverAssistantMessageId != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Text(
                    'Did this feel wrong/biased?',
                    style: TextStyle(
                      fontSize: 11,
                      color: Theme.of(context).textTheme.bodySmall?.color,
                    ),
                  ),
                  const SizedBox(width: 8),
                  TextButton(
                    onPressed: _submittedFeedbackMessageIds
                            .contains(message.serverAssistantMessageId)
                        ? null
                        : () => _submitMessageFeedback(
                              messageId: message.serverAssistantMessageId!,
                              helpful: false,
                            ),
                    style: TextButton.styleFrom(
                      minimumSize: const Size(0, 24),
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    child: const Text('Yes'),
                  ),
                  TextButton(
                    onPressed: _submittedFeedbackMessageIds
                            .contains(message.serverAssistantMessageId)
                        ? null
                        : () => _submitMessageFeedback(
                              messageId: message.serverAssistantMessageId!,
                              helpful: true,
                            ),
                    style: TextButton.styleFrom(
                      minimumSize: const Size(0, 24),
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    child: const Text('No'),
                  ),
                ],
              ),
            ],
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
  final String? prediction;
  final bool crisisDetected;
  /// Backend [Message] id for assistant rows; used for feedback (Phase 3).
  final int? serverAssistantMessageId;

  ChatMessage({
    required this.id,
    required this.text,
    required this.sender,
    required this.timestamp,
    this.prediction,
    this.crisisDetected = false,
    this.serverAssistantMessageId,
  });
}

enum MessageSender { user, ai }
