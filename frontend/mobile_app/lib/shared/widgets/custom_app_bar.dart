import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final String? subtitle;
  final bool showAvatar;
  final Widget? action;

  const CustomAppBar({
    super.key,
    this.title,
    this.subtitle,
    this.showAvatar = false,
    this.action,
  });

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: subtitle != null
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  subtitle!,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if (title != null)
                  Text(
                    title!,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
              ],
            )
          : title != null
              ? Text(title!)
              : null,
      actions: [
        if (showAvatar)
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: CircleAvatar(
              backgroundColor: Theme.of(context).primaryColor,
              child: const Text(
                'JD',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
        if (action != null) action!,
      ],
    );
  }
}
