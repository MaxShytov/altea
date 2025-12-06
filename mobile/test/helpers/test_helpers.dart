import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:altea_mobile/data/models/auth_response.dart';
import 'package:altea_mobile/data/models/user_model.dart';
import 'package:altea_mobile/data/repositories/auth_repository.dart';
import 'package:altea_mobile/presentation/providers/registration_state.dart';

/// Mock AuthRepository for testing.
class MockAuthRepository implements AuthRepository {
  bool shouldSucceed;
  String? errorMessage;
  Map<String, List<String>>? fieldErrors;
  int registerCallCount = 0;
  int resendVerificationCallCount = 0;
  int loginCallCount = 0;
  bool _isLoggedIn = false;

  MockAuthRepository({
    this.shouldSucceed = true,
    this.errorMessage,
    this.fieldErrors,
  });

  @override
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    loginCallCount++;
    await Future.delayed(const Duration(milliseconds: 100));

    if (!shouldSucceed) {
      throw MockApiException(
        message: errorMessage ?? 'Login failed',
        fieldErrors: fieldErrors ?? {},
      );
    }

    _isLoggedIn = true;
    return AuthResponse(
      accessToken: 'mock_access_token',
      refreshToken: 'mock_refresh_token',
      user: UserModel(
        id: 'test-uuid',
        email: email,
        firstName: 'Test',
        lastName: 'User',
        profileCompleted: false,
        language: 'en',
      ),
    );
  }

  @override
  Future<void> logout() async {
    _isLoggedIn = false;
  }

  @override
  Future<bool> isLoggedIn() async {
    return _isLoggedIn;
  }

  @override
  Future<String?> getAccessToken() async {
    return _isLoggedIn ? 'mock_access_token' : null;
  }

  @override
  Future<UserModel> register({
    required String email,
    required String password,
    required String passwordConfirm,
    required String firstName,
    required String lastName,
    required bool termsAccepted,
  }) async {
    registerCallCount++;
    await Future.delayed(const Duration(milliseconds: 100));

    if (!shouldSucceed) {
      throw MockApiException(
        message: errorMessage ?? 'Registration failed',
        fieldErrors: fieldErrors ?? {},
      );
    }

    return UserModel(
      id: 'test-uuid',
      email: email,
      firstName: firstName,
      lastName: lastName,
      isVerified: false,
    );
  }

  @override
  Future<void> resendVerification(String email) async {
    resendVerificationCallCount++;
    await Future.delayed(const Duration(milliseconds: 100));

    if (!shouldSucceed) {
      throw MockApiException(message: errorMessage ?? 'Resend failed');
    }
  }
}

/// Mock API exception for testing.
class MockApiException implements Exception {
  final String message;
  final Map<String, List<String>> fieldErrors;

  MockApiException({
    required this.message,
    this.fieldErrors = const {},
  });

  String get userMessage => message;
}

/// Helper to wrap widget in necessary providers and material app.
Widget createTestWidget({
  required Widget child,
  List<Override>? overrides,
}) {
  return ProviderScope(
    overrides: overrides ?? [],
    child: MaterialApp(
      home: child,
    ),
  );
}

/// Helper to create a mock registration notifier for testing.
class TestRegistrationNotifier extends StateNotifier<RegistrationState> {
  final MockAuthRepository repository;

  TestRegistrationNotifier(this.repository)
      : super(const RegistrationState.initial());

  Future<void> register({
    required String email,
    required String password,
    required String passwordConfirm,
    required String firstName,
    required String lastName,
    required bool termsAccepted,
  }) async {
    state = const RegistrationState.loading();

    try {
      final user = await repository.register(
        email: email,
        password: password,
        passwordConfirm: passwordConfirm,
        firstName: firstName,
        lastName: lastName,
        termsAccepted: termsAccepted,
      );

      state = RegistrationState.success(user: user, email: email);
    } on MockApiException catch (e) {
      state = RegistrationState.error(
        message: e.userMessage,
        fieldErrors: e.fieldErrors,
      );
    } catch (e) {
      state = RegistrationState.error(
        message: 'An unexpected error occurred. Please try again.',
      );
    }
  }

  Future<bool> resendVerification(String email) async {
    try {
      await repository.resendVerification(email);
      return true;
    } on MockApiException {
      return false;
    }
  }

  void reset() {
    state = const RegistrationState.initial();
  }
}
