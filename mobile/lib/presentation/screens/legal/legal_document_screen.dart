import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/extensions/build_context_extensions.dart';

/// Screen that displays a legal document (Terms of Service or Privacy Policy).
/// Opens the document in the device's browser.
class LegalDocumentScreen extends StatefulWidget {
  const LegalDocumentScreen({
    super.key,
    required this.title,
    required this.url,
  });

  final String title;
  final String url;

  @override
  State<LegalDocumentScreen> createState() => _LegalDocumentScreenState();
}

class _LegalDocumentScreenState extends State<LegalDocumentScreen> {
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _openInBrowser();
  }

  Future<void> _openInBrowser() async {
    final uri = Uri.parse(widget.url);

    try {
      final canLaunch = await canLaunchUrl(uri);
      if (canLaunch) {
        await launchUrl(
          uri,
          mode: LaunchMode.inAppBrowserView,
        );
        // Go back after browser is closed
        if (mounted) {
          Navigator.of(context).pop();
        }
      } else {
        setState(() {
          _isLoading = false;
          _errorMessage = context.l10n.couldNotOpen(widget.title);
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = context.l10n.failedToOpen(widget.title, e.toString());
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Center(
        child: _isLoading
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 16),
                  Text(l10n.openingInBrowser),
                ],
              )
            : _buildErrorView(),
      ),
    );
  }

  Widget _buildErrorView() {
    final l10n = context.l10n;

    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            _errorMessage ?? l10n.anErrorOccurred,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              setState(() {
                _isLoading = true;
                _errorMessage = null;
              });
              _openInBrowser();
            },
            icon: const Icon(Icons.refresh),
            label: Text(l10n.retry),
          ),
        ],
      ),
    );
  }
}
