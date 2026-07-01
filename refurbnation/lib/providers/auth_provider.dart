import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_client.dart';

class AuthProvider with ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  final storage = const FlutterSecureStorage();
  bool _isAuthenticated = false;
  String? userRole;

  // Profile state properties
  String _firstName = '';
  String _lastName = '';
  String _email = '';

  bool get isAuthenticated => _isAuthenticated;
  String get firstName => _firstName;
  String get lastName => _lastName;
  String get email => _email;

  Future<bool> login(String email, String password) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login/',
        data: {'email': email, 'password': password},
      );

      if (response.statusCode == 200) {
        String role = response.data['role'] ?? 'USER';

        if (role != 'USER') {
          print("Login Denied: Only 'USER' role is allowed.");
          return false;
        }

        await storage.write(
          key: 'access_token',
          value: response.data['access'],
        );
        await storage.write(
          key: 'refresh_token',
          value: response.data['refresh'],
        );

        userRole = role;
        _isAuthenticated = true;

        // Fetch profile data immediately after successful login
        await fetchUserProfile();

        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      print("Login Error: $e");
      return false;
    }
  }

  // Fetch Profile details from your custom user backend
  Future<void> fetchUserProfile() async {
    try {
      final response = await _apiClient.dio.get('/auth/profile/');
      if (response.statusCode == 200) {
        _firstName = response.data['first_name'] ?? '';
        _lastName = response.data['last_name'] ?? '';
        _email = response.data['email'] ?? '';
        notifyListeners();
      }
    } catch (e) {
      print("Error fetching profile: $e");
    }
  }

  // Update First Name and Last Name on the Django backend
  Future<bool> updateUserProfile(String firstName, String lastName) async {
    try {
      final response = await _apiClient.dio.patch(
        '/auth/profile/',
        data: {'first_name': firstName, 'last_name': lastName},
      );

      if (response.statusCode == 200) {
        _firstName = firstName;
        _lastName = lastName;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      print("Error updating profile: $e");
      return false;
    }
  }

  // Add this inside your AuthProvider class
  Future<bool> signup(String email, String password) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register/',
        data: {'email': email, 'password': password},
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        // Optionally auto-login after signup, or just return true to redirect to login
        return true;
      }
      return false;
    } catch (e) {
      print("Signup Error: $e");
      return false;
    }
  }

  // Clear storage and update state so main.dart redirects to Login Screen
  Future<void> logout() async {
    await storage.deleteAll();
    _isAuthenticated = false;
    userRole = null;
    _firstName = '';
    _lastName = '';
    _email = '';
    notifyListeners();
  }
}
