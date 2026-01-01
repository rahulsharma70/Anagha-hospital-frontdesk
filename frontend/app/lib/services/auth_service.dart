import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';
import '../models/user_model.dart';
import 'dart:convert';

class AuthService extends ChangeNotifier {
  User? _user;
  String? _token;
  bool _isLoading = false;

  User? get user => _user;
  String? get token => _token;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _token != null && _user != null;

  AuthService() {
    _loadUser();
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    final userJson = prefs.getString('user_data');

    if (token != null && userJson != null) {
      _token = token;
      _user = User.fromJson(jsonDecode(userJson));
      notifyListeners();
    }
  }

  Future<bool> login(String mobile, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.post('/api/users/login', {
        'mobile': mobile,
        'password': password,
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['access_token'];
        _user = User.fromJson(data['user']);

        // Save to local storage
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);
        await prefs.setString('user_data', jsonEncode(_user!.toJson()));

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(Map<String, dynamic> userData) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.post('/api/users/register', userData);

      if (response.statusCode == 200 || response.statusCode == 201) {
        try {
          final data = jsonDecode(response.body);
          _token = data['access_token'];
          _user = User.fromJson(data['user']);

          // Save to local storage
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('auth_token', _token!);
          await prefs.setString('user_data', jsonEncode(_user!.toJson()));

          _isLoading = false;
          notifyListeners();
          return true;
        } catch (parseError) {
          print('Error parsing registration response: $parseError');
          print('Response body: ${response.body}');
          _isLoading = false;
          notifyListeners();
          return false;
        }
      } else {
        print('Registration failed with status: ${response.statusCode}');
        print('Response body: ${response.body}');
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      print('Registration error: $e');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _user = null;
    _token = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('user_data');

    notifyListeners();
  }

  Future<User?> getCurrentUser() async {
    if (_user != null) return _user;

    try {
      final response = await ApiService.get('/api/users/me', requiresAuth: true);
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _user = User.fromJson(data);
        notifyListeners();
        return _user;
      }
    } catch (e) {
      // Handle error
    }
    return null;
  }
}



