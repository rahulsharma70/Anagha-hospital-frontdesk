import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_service.dart';

class DoctorService {
  static String get baseUrl => ApiService.baseUrl;
  
  /// Search doctors dynamically as user types
  static Future<List<Map<String, dynamic>>> searchDoctors(String query, {int? hospitalId}) async {
    if (query.isEmpty || query.length < 2) {
      return [];
    }
    
    try {
      String url = '$baseUrl/api/doctors/search?q=${Uri.encodeComponent(query)}';
      if (hospitalId != null) {
        url += '&hospital_id=$hospitalId';
      }
      
      print('DoctorService: Searching doctors at $url');
      
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ).timeout(const Duration(seconds: 5));

      print('DoctorService: Response status: ${response.statusCode}');
      print('DoctorService: Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final doctors = List<Map<String, dynamic>>.from(data['doctors'] ?? []);
        print('DoctorService: Found ${doctors.length} doctors');
        return doctors;
      } else {
        print('DoctorService: Error status ${response.statusCode}: ${response.body}');
        return [];
      }
    } catch (e) {
      print('DoctorService: Error searching doctors: $e');
      return [];
    }
  }

  /// Add a new doctor to the database
  static Future<Map<String, dynamic>> addNewDoctor({
    required String doctorName,
    String? place,
    String? mobile,
    String? email,
    String? degree,
    String? specialization,
    int? hospitalId,
  }) async {
    try {
      final url = '$baseUrl/api/doctors/add';
      print('DoctorService: Adding doctor at $url');
      
      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'doctor_name': doctorName,
          'place': place,
          'mobile': mobile,
          'email': email,
          'degree': degree,
          'specialization': specialization,
          'hospital_id': hospitalId,
        }),
      ).timeout(const Duration(seconds: 10));

      print('DoctorService: Add doctor response status: ${response.statusCode}');
      print('DoctorService: Add doctor response body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        print('DoctorService: Doctor added successfully: ${data['doctor_name']}');
        return data;
      } else {
        String errorMessage = 'Failed to add doctor';
        try {
          if (response.body.isNotEmpty) {
            final error = jsonDecode(response.body);
            errorMessage = error['detail'] ?? error['message'] ?? errorMessage;
          }
        } catch (e) {
          if (response.statusCode == 404) {
            errorMessage = 'API endpoint not found. Please check if server is running at $baseUrl';
          } else if (response.statusCode == 500) {
            errorMessage = 'Server error. Please try again later.';
          } else {
            errorMessage = 'Failed to add doctor (Status: ${response.statusCode})';
          }
        }
        print('DoctorService: Error: $errorMessage');
        throw Exception(errorMessage);
      }
    } catch (e) {
      print('DoctorService: Error adding doctor: $e');
      rethrow;
    }
  }
}

