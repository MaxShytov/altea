"""
Management command to seed legal documents (Terms of Service and Privacy Policy).

This command creates the initial versions of legal documents required for the app.
Documents are compliant with:
- Swiss Federal Act on Data Protection (FADP/DSG) - effective September 1, 2023
- EU General Data Protection Regulation (GDPR)
- Swiss medical data handling requirements

Usage:
    python manage.py seed_legal_documents
    python manage.py seed_legal_documents --force  # Recreate even if exists
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import LegalDocument


class Command(BaseCommand):
    help = 'Seed legal documents (Terms of Service and Privacy Policy)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of documents even if they already exist',
        )

    def handle(self, *args, **options):
        force = options['force']

        with transaction.atomic():
            # Check if documents already exist
            existing_terms = LegalDocument.objects.filter(
                document_type='terms',
                version='1.0'
            ).exists()
            existing_privacy = LegalDocument.objects.filter(
                document_type='privacy',
                version='1.0'
            ).exists()

            if existing_terms and existing_privacy and not force:
                self.stdout.write(
                    self.style.WARNING(
                        'Legal documents already exist. Use --force to recreate.'
                    )
                )
                return

            # Create Terms of Service
            if force and existing_terms:
                LegalDocument.objects.filter(
                    document_type='terms',
                    version='1.0'
                ).delete()
                self.stdout.write('Deleted existing Terms of Service v1.0')

            if not existing_terms or force:
                self._create_terms_of_service()
                self.stdout.write(
                    self.style.SUCCESS('Created Terms of Service v1.0')
                )

            # Create Privacy Policy
            if force and existing_privacy:
                LegalDocument.objects.filter(
                    document_type='privacy',
                    version='1.0'
                ).delete()
                self.stdout.write('Deleted existing Privacy Policy v1.0')

            if not existing_privacy or force:
                self._create_privacy_policy()
                self.stdout.write(
                    self.style.SUCCESS('Created Privacy Policy v1.0')
                )

        self.stdout.write(
            self.style.SUCCESS('Legal documents seeding completed!')
        )

    def _create_terms_of_service(self):
        """Create Terms of Service document."""
        content = self._get_terms_content()
        LegalDocument.objects.create(
            document_type='terms',
            version='1.0',
            title='Terms of Service',
            content=content,
            effective_date=date.today(),
            is_active=True,
        )

    def _create_privacy_policy(self):
        """Create Privacy Policy document."""
        content = self._get_privacy_content()
        LegalDocument.objects.create(
            document_type='privacy',
            version='1.0',
            title='Privacy Policy',
            content=content,
            effective_date=date.today(),
            is_active=True,
        )

    def _get_terms_content(self):
        """Return Terms of Service HTML content."""
        return """
<h2>1. Introduction and Acceptance</h2>

<p>Welcome to Altea ("App", "Service", "we", "us", or "our"). These Terms of Service ("Terms") govern your access to and use of the Altea mobile application and related services designed to support individuals in their addiction recovery journey.</p>

<p>By creating an account, accessing, or using our Service, you agree to be bound by these Terms. If you do not agree to these Terms, please do not use our Service.</p>

<p><strong>Important Notice:</strong> Altea is a wellness support tool and is NOT a substitute for professional medical advice, diagnosis, or treatment. If you are experiencing a medical emergency, please contact emergency services immediately.</p>

<h2>2. Eligibility</h2>

<p>To use Altea, you must:</p>
<ul>
    <li>Be at least 18 years of age</li>
    <li>Have the legal capacity to enter into binding agreements</li>
    <li>Not be prohibited from using the Service under applicable laws</li>
    <li>Provide accurate and complete registration information</li>
</ul>

<p>If you are using the Service on behalf of a minor under your care (with appropriate legal authority), you are responsible for ensuring compliance with these Terms.</p>

<h2>3. Description of Service</h2>

<p>Altea provides tools and features to support addiction recovery, including:</p>
<ul>
    <li>Tracking sobriety progress and milestones</li>
    <li>Logging consumption events and triggers</li>
    <li>Personalized assessments and insights</li>
    <li>Motivational notifications and reminders</li>
    <li>Progress visualization and statistics</li>
    <li>Ability to share progress with healthcare providers</li>
</ul>

<h2>4. Account Registration and Security</h2>

<h3>4.1 Account Creation</h3>
<p>To use certain features of the Service, you must create an account by providing:</p>
<ul>
    <li>A valid email address</li>
    <li>A secure password</li>
    <li>Your first and last name</li>
    <li>Acceptance of these Terms and our Privacy Policy</li>
</ul>

<h3>4.2 Account Security</h3>
<p>You are responsible for:</p>
<ul>
    <li>Maintaining the confidentiality of your login credentials</li>
    <li>All activities that occur under your account</li>
    <li>Notifying us immediately of any unauthorized access</li>
</ul>

<h3>4.3 Email Verification</h3>
<p>You must verify your email address to access all features of the Service. Unverified accounts may have limited functionality.</p>

<h2>5. User Conduct and Responsibilities</h2>

<p>When using Altea, you agree to:</p>
<ul>
    <li>Provide accurate and truthful information</li>
    <li>Use the Service only for its intended purpose</li>
    <li>Not share your account credentials with others</li>
    <li>Not attempt to circumvent security measures</li>
    <li>Not use the Service for any illegal purposes</li>
    <li>Not interfere with or disrupt the Service</li>
</ul>

<h2>6. Health Disclaimer</h2>

<p><strong>IMPORTANT:</strong></p>
<ul>
    <li>Altea is NOT a medical device and is not intended to diagnose, treat, cure, or prevent any disease or health condition.</li>
    <li>The assessments provided are for informational purposes only and should not replace professional medical evaluation.</li>
    <li>AI-generated insights are suggestions based on general patterns and may not be appropriate for your specific situation.</li>
    <li>Always consult with qualified healthcare professionals for medical advice.</li>
    <li>If you are in crisis or experiencing thoughts of self-harm, please contact emergency services or a crisis helpline immediately.</li>
</ul>

<h3>Swiss Emergency Contacts:</h3>
<ul>
    <li>Emergency: 144 (Ambulance)</li>
    <li>Die Dargebotene Hand: 143 (24/7 crisis support)</li>
    <li>Sucht Schweiz: 0800 104 104</li>
</ul>

<h2>7. Intellectual Property</h2>

<h3>7.1 Our Rights</h3>
<p>The Service, including all content, features, and functionality, is owned by Altea and protected by Swiss and international copyright, trademark, and other intellectual property laws.</p>

<h3>7.2 Your Content</h3>
<p>You retain ownership of the data you input into the Service. By using the Service, you grant us a limited license to process your data as described in our Privacy Policy.</p>

<h2>8. Data Protection</h2>

<p>Your privacy is important to us. Our collection, use, and protection of your personal data is governed by our <a href="/legal/privacy/">Privacy Policy</a>, which complies with:</p>
<ul>
    <li>Swiss Federal Act on Data Protection (FADP/DSG)</li>
    <li>EU General Data Protection Regulation (GDPR)</li>
</ul>

<p>By using the Service, you consent to the data practices described in our Privacy Policy.</p>

<h2>9. Sharing Features</h2>

<p>Altea allows you to share your recovery progress with healthcare providers:</p>
<ul>
    <li>You control what information is shared</li>
    <li>Shared links can be password-protected</li>
    <li>You can revoke access at any time</li>
    <li>We are not responsible for how recipients use shared information</li>
</ul>

<h2>10. Service Availability and Modifications</h2>

<h3>10.1 Availability</h3>
<p>We strive to maintain Service availability but do not guarantee uninterrupted access. The Service may be temporarily unavailable due to maintenance, updates, or circumstances beyond our control.</p>

<h3>10.2 Modifications</h3>
<p>We reserve the right to modify, suspend, or discontinue any part of the Service at any time. We will provide reasonable notice of significant changes when possible.</p>

<h2>11. Termination</h2>

<h3>11.1 By You</h3>
<p>You may terminate your account at any time by contacting us or using the account deletion feature in the app. Upon termination:</p>
<ul>
    <li>Your access to the Service will cease</li>
    <li>Your data will be handled according to our Privacy Policy</li>
    <li>Data may be retained as required by law</li>
</ul>

<h3>11.2 By Us</h3>
<p>We may terminate or suspend your account if you:</p>
<ul>
    <li>Violate these Terms</li>
    <li>Engage in fraudulent or illegal activity</li>
    <li>Pose a security risk to the Service</li>
</ul>

<h2>12. Limitation of Liability</h2>

<p>TO THE MAXIMUM EXTENT PERMITTED BY SWISS LAW:</p>
<ul>
    <li>The Service is provided "AS IS" without warranties of any kind</li>
    <li>We are not liable for any indirect, incidental, special, or consequential damages</li>
    <li>Our total liability shall not exceed the amount you paid for the Service in the 12 months preceding the claim</li>
    <li>We are not liable for any decisions you make based on information provided by the Service</li>
</ul>

<h2>13. Indemnification</h2>

<p>You agree to indemnify and hold harmless Altea and its officers, directors, employees, and agents from any claims, damages, or expenses arising from your:</p>
<ul>
    <li>Use of the Service</li>
    <li>Violation of these Terms</li>
    <li>Violation of any third-party rights</li>
</ul>

<h2>14. Governing Law and Jurisdiction</h2>

<p>These Terms are governed by the laws of Switzerland, without regard to conflict of law principles. Any disputes shall be resolved exclusively in the courts of Zurich, Switzerland.</p>

<p>For consumers residing in the EU, this choice of jurisdiction does not deprive you of the protection afforded by mandatory consumer protection laws of your country of residence.</p>

<h2>15. Changes to Terms</h2>

<p>We may update these Terms from time to time. When we make significant changes:</p>
<ul>
    <li>We will notify you via email or in-app notification</li>
    <li>The updated Terms will be posted with a new effective date</li>
    <li>Continued use of the Service constitutes acceptance of the updated Terms</li>
</ul>

<h2>16. Severability</h2>

<p>If any provision of these Terms is found to be unenforceable, the remaining provisions will continue in full force and effect.</p>

<h2>17. Entire Agreement</h2>

<p>These Terms, together with our Privacy Policy, constitute the entire agreement between you and Altea regarding the Service.</p>

<h2>18. Contact Information</h2>

<p>If you have questions about these Terms, please contact us at:</p>
<p>
    <strong>Altea</strong><br>
    Email: legal@altea.ch<br>
    Address: Switzerland
</p>

<p><em>Last updated: December 2025</em></p>
"""

    def _get_privacy_content(self):
        """Return Privacy Policy HTML content."""
        return """
<h2>1. Introduction</h2>

<p>Altea ("we", "us", "our") is committed to protecting your privacy and personal data. This Privacy Policy explains how we collect, use, store, and protect your information when you use the Altea mobile application ("App", "Service").</p>

<p>This Privacy Policy complies with:</p>
<ul>
    <li>Swiss Federal Act on Data Protection (FADP/DSG) - effective September 1, 2023</li>
    <li>EU General Data Protection Regulation (GDPR)</li>
    <li>Swiss medical data handling requirements</li>
</ul>

<p><strong>Data Controller:</strong><br>
Altea<br>
Switzerland<br>
Email: privacy@altea.ch</p>

<h2>2. Categories of Personal Data We Collect</h2>

<h3>2.1 Account Information</h3>
<ul>
    <li>Email address</li>
    <li>First and last name</li>
    <li>Password (stored securely hashed)</li>
    <li>Profile picture (optional)</li>
    <li>Phone number (optional)</li>
    <li>Date of birth (optional)</li>
    <li>Country and language preferences</li>
</ul>

<h3>2.2 Health and Recovery Data (Sensitive Personal Data)</h3>
<p>Under Swiss law (FADP) and GDPR, health data is classified as <strong>sensitive personal data</strong> requiring special protection. We collect:</p>
<ul>
    <li>Types of addictions being tracked</li>
    <li>Assessment questionnaire responses and scores</li>
    <li>Consumption/relapse events (dates, amounts, notes)</li>
    <li>Trigger information</li>
    <li>Mood and emotional data</li>
    <li>Recovery milestones and streaks</li>
    <li>Photos you choose to upload (journal entries)</li>
</ul>

<h3>2.3 Technical Data</h3>
<ul>
    <li>Device information (type, operating system)</li>
    <li>IP address</li>
    <li>App usage data and analytics</li>
    <li>Push notification tokens</li>
    <li>Crash reports and error logs</li>
</ul>

<h2>3. Legal Basis for Processing</h2>

<p>We process your personal data based on the following legal grounds:</p>

<table>
    <tr>
        <th>Data Type</th>
        <th>Legal Basis</th>
    </tr>
    <tr>
        <td>Account data</td>
        <td>Contract performance (Art. 6(1)(b) GDPR)</td>
    </tr>
    <tr>
        <td>Health/recovery data</td>
        <td><strong>Explicit consent</strong> (Art. 9(2)(a) GDPR, Art. 6(7) FADP)</td>
    </tr>
    <tr>
        <td>Technical data</td>
        <td>Legitimate interest (Art. 6(1)(f) GDPR)</td>
    </tr>
    <tr>
        <td>Marketing communications</td>
        <td>Consent (Art. 6(1)(a) GDPR)</td>
    </tr>
</table>

<p><strong>Important:</strong> Processing of your health data requires your <strong>explicit consent</strong>, which you provide when accepting these terms during registration. You may withdraw consent at any time.</p>

<h2>4. How We Use Your Data</h2>

<h3>4.1 Service Provision</h3>
<ul>
    <li>Creating and managing your account</li>
    <li>Tracking your recovery progress</li>
    <li>Providing personalized assessments and recommendations</li>
    <li>Generating statistics and visualizations</li>
    <li>Enabling progress sharing with healthcare providers</li>
</ul>

<h3>4.2 AI-Powered Features</h3>
<p>We use artificial intelligence to:</p>
<ul>
    <li>Analyze assessment responses and provide personalized insights</li>
    <li>Identify patterns in your recovery journey</li>
    <li>Generate motivational content</li>
</ul>
<p><strong>Note:</strong> AI analysis is performed on anonymized/pseudonymized data where possible. No human reviews your personal data unless required for support requests you initiate.</p>

<h3>4.3 Communications</h3>
<ul>
    <li>Sending email verification and password reset emails</li>
    <li>Push notifications (milestones, reminders, motivation)</li>
    <li>Service updates and important notices</li>
</ul>

<h3>4.4 Service Improvement</h3>
<ul>
    <li>Analyzing aggregated, anonymized usage patterns</li>
    <li>Improving app features and performance</li>
    <li>Fixing bugs and security issues</li>
</ul>

<h2>5. Data Sharing and Disclosure</h2>

<h3>5.1 We Do NOT:</h3>
<ul>
    <li>Sell your personal data to third parties</li>
    <li>Share your health data with advertisers</li>
    <li>Use your data for profiling for marketing purposes</li>
</ul>

<h3>5.2 We May Share Data With:</h3>

<p><strong>Healthcare Providers (with your explicit consent):</strong></p>
<ul>
    <li>When you use the sharing feature to generate a link</li>
    <li>You control exactly what data is shared</li>
    <li>You can revoke access at any time</li>
</ul>

<p><strong>Service Providers:</strong></p>
<ul>
    <li>Cloud hosting providers (data stored in Switzerland/EU)</li>
    <li>Email delivery services (for transactional emails only)</li>
    <li>Analytics providers (anonymized data only)</li>
</ul>
<p>All service providers are bound by data processing agreements and must comply with FADP/GDPR requirements.</p>

<p><strong>AI Service Providers:</strong></p>
<ul>
    <li>We use OpenAI for AI-powered features</li>
    <li>Only anonymized/pseudonymized data is sent for processing</li>
    <li>No directly identifiable health data is shared</li>
</ul>

<p><strong>Legal Requirements:</strong></p>
<ul>
    <li>When required by Swiss law or valid legal process</li>
    <li>To protect our rights, privacy, safety, or property</li>
    <li>In connection with legal proceedings</li>
</ul>

<h2>6. International Data Transfers</h2>

<p>Your data is primarily stored and processed in Switzerland. When data is transferred outside Switzerland or the EEA, we ensure adequate protection through:</p>
<ul>
    <li>Standard Contractual Clauses (SCCs) approved by the EU Commission</li>
    <li>Adequacy decisions by the Swiss FDPIC</li>
    <li>Other appropriate safeguards under Art. 46 GDPR / Art. 16 FADP</li>
</ul>

<h2>7. Data Retention</h2>

<table>
    <tr>
        <th>Data Type</th>
        <th>Retention Period</th>
    </tr>
    <tr>
        <td>Account data</td>
        <td>Duration of account + 30 days after deletion</td>
    </tr>
    <tr>
        <td>Health/recovery data</td>
        <td>Duration of account + 30 days after deletion</td>
    </tr>
    <tr>
        <td>Anonymized analytics</td>
        <td>Up to 2 years</td>
    </tr>
    <tr>
        <td>Technical logs</td>
        <td>90 days</td>
    </tr>
    <tr>
        <td>Backup data</td>
        <td>30 days after deletion from live system</td>
    </tr>
</table>

<p><strong>Legal obligations:</strong> We may retain certain data longer if required by law (e.g., for tax or legal compliance purposes).</p>

<h2>8. Your Rights</h2>

<p>Under Swiss (FADP) and EU (GDPR) data protection laws, you have the following rights:</p>

<h3>8.1 Right to Access (Art. 15 GDPR / Art. 25 FADP)</h3>
<p>Request a copy of your personal data we hold.</p>

<h3>8.2 Right to Rectification (Art. 16 GDPR / Art. 6 FADP)</h3>
<p>Request correction of inaccurate or incomplete data.</p>

<h3>8.3 Right to Erasure ("Right to be Forgotten") (Art. 17 GDPR)</h3>
<p>Request deletion of your personal data. This includes:</p>
<ul>
    <li>All account information</li>
    <li>All health and recovery data</li>
    <li>All associated content</li>
</ul>

<h3>8.4 Right to Data Portability (Art. 20 GDPR / Art. 28 FADP)</h3>
<p>Receive your data in a structured, machine-readable format (JSON/PDF export).</p>

<h3>8.5 Right to Restrict Processing (Art. 18 GDPR)</h3>
<p>Request limitation of processing in certain circumstances.</p>

<h3>8.6 Right to Object (Art. 21 GDPR)</h3>
<p>Object to processing based on legitimate interests.</p>

<h3>8.7 Right to Withdraw Consent (Art. 7(3) GDPR / Art. 6(7) FADP)</h3>
<p>Withdraw consent for health data processing at any time. This will not affect the lawfulness of processing before withdrawal.</p>

<h3>8.8 Right to Lodge a Complaint</h3>
<p>You may lodge a complaint with:</p>
<ul>
    <li><strong>Switzerland:</strong> Federal Data Protection and Information Commissioner (FDPIC)<br>
        Website: <a href="https://www.edoeb.admin.ch">www.edoeb.admin.ch</a></li>
    <li><strong>EU:</strong> Your local Data Protection Authority</li>
</ul>

<h3>How to Exercise Your Rights</h3>
<p>Contact us at: <a href="mailto:privacy@altea.ch">privacy@altea.ch</a></p>
<p>We will respond within 30 days. We may request identity verification for security purposes.</p>

<h2>9. Data Security</h2>

<p>We implement comprehensive security measures to protect your data:</p>

<h3>9.1 Technical Measures</h3>
<ul>
    <li><strong>Encryption in transit:</strong> TLS 1.3 for all API communications</li>
    <li><strong>Encryption at rest:</strong> AES-256 for sensitive data</li>
    <li><strong>Password security:</strong> Passwords hashed using industry-standard algorithms</li>
    <li><strong>Access controls:</strong> Role-based access, principle of least privilege</li>
    <li><strong>Regular security audits:</strong> Vulnerability assessments and penetration testing</li>
</ul>

<h3>9.2 Organizational Measures</h3>
<ul>
    <li>Staff training on data protection</li>
    <li>Confidentiality agreements with employees</li>
    <li>Incident response procedures</li>
    <li>Regular data protection impact assessments</li>
</ul>

<h2>10. Data Breach Notification</h2>

<p>In the event of a data breach that poses a risk to your rights and freedoms:</p>
<ul>
    <li>We will notify the FDPIC without undue delay</li>
    <li>We will inform affected users as soon as possible</li>
    <li>We will provide information about the breach and steps taken</li>
</ul>

<h2>11. Children's Privacy</h2>

<p>Altea is not intended for users under 18 years of age. We do not knowingly collect data from children. If you believe a child has provided us with personal data, please contact us immediately.</p>

<h2>12. Automated Decision-Making</h2>

<p>We use AI to provide insights and recommendations based on your data. However:</p>
<ul>
    <li>No decisions with legal or significant effects are made solely by automated means</li>
    <li>AI-generated suggestions are informational only</li>
    <li>You have the right to request human review of any automated analysis</li>
</ul>

<h2>13. Cookies and Similar Technologies</h2>

<p>The Altea mobile app does not use cookies. For our web services (e.g., email verification pages), we use:</p>
<ul>
    <li><strong>Essential cookies:</strong> Required for basic functionality (no consent needed)</li>
</ul>
<p>We do not use tracking or advertising cookies.</p>

<h2>14. Third-Party Links</h2>

<p>Our Service may contain links to third-party websites. We are not responsible for the privacy practices of these sites. Please review their privacy policies before providing personal data.</p>

<h2>15. Changes to This Policy</h2>

<p>We may update this Privacy Policy periodically. When we make significant changes:</p>
<ul>
    <li>We will notify you via email or in-app notification</li>
    <li>The updated policy will be posted with a new effective date</li>
    <li>For material changes affecting health data processing, we will seek renewed consent</li>
</ul>

<h2>16. Swiss Representative</h2>

<p>For users outside Switzerland accessing our services, our Swiss representative is:</p>
<p>
    Altea<br>
    Switzerland<br>
    Email: privacy@altea.ch
</p>

<h2>17. Contact Us</h2>

<p>For privacy-related questions, requests, or complaints:</p>

<p>
    <strong>Data Protection Officer</strong><br>
    Altea<br>
    Email: <a href="mailto:privacy@altea.ch">privacy@altea.ch</a><br>
    Address: Switzerland
</p>

<p>We aim to respond to all inquiries within 30 days.</p>

<p><em>Last updated: December 2025</em></p>
<p><em>Version: 1.0</em></p>
"""
