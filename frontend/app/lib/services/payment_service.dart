import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:fluttertoast/fluttertoast.dart';
import '../utils/app_colors.dart';
import 'api_service.dart';

class PaymentService {
  static String get baseUrl => ApiService.baseUrl;
  
  /// Create a payment order for appointment/operation/hospital_registration/pharma_appointment
  static Future<Map<String, dynamic>?> createPaymentOrder({
    required String type, // 'appointment', 'operation', 'hospital_registration', 'pharma_appointment', 'subscription'
    required int hospitalId,
    required String patientName,
    required String patientMobile,
    required double amount,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      print('Creating payment order: type=$type, hospitalId=$hospitalId, amount=$amount');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/payments/create-order'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'type': type,
          'hospital_id': hospitalId,
          'patient_name': patientName,
          'patient_mobile': patientMobile,
          'amount': amount,
          'metadata': metadata ?? {},
        }),
      ).timeout(const Duration(seconds: 30));

      print('Payment order response status: ${response.statusCode}');
      print('Payment order response body: ${response.body}');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        print('Payment order created successfully: ${data['order_id']}');
        return data;
      } else {
        print('Payment order creation failed: Status ${response.statusCode}, Body: ${response.body}');
        try {
          final error = jsonDecode(response.body);
          throw Exception(error['detail'] ?? 'Failed to create payment order');
        } catch (e) {
          throw Exception('Failed to create payment order: ${response.statusCode}');
        }
      }
    } catch (e) {
      print('Error creating payment order: $e');
      rethrow;
    }
  }

  /// Verify payment after completion
  static Future<bool> verifyPayment({
    required String orderId,
    required String paymentId,
    required String signature,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/payments/verify'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'order_id': orderId,
          'payment_id': paymentId,
          'signature': signature,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['verified'] == true;
      }
      return false;
    } catch (e) {
      print('Error verifying payment: $e');
      return false;
    }
  }

  /// Get payment status
  static Future<Map<String, dynamic>?> getPaymentStatus(String orderId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/payments/status/$orderId'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Error getting payment status: $e');
      return null;
    }
  }

  /// Get payment history for a patient
  static Future<List<Map<String, dynamic>>> getPaymentHistory(String patientMobile) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/payments/history/$patientMobile'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['payments'] ?? []);
      }
      return [];
    } catch (e) {
      print('Error getting payment history: $e');
      return [];
    }
  }

  /// Request refund
  static Future<Map<String, dynamic>?> requestRefund({
    required String paymentId,
    required double amount,
    String? reason,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/payments/refund'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'payment_id': paymentId,
          'amount': amount,
          'reason': reason,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('Error requesting refund: $e');
      return null;
    }
  }

  /// Calculate appointment fee
  static double calculateAppointmentFee(int hospitalId, {double? customAmount}) {
    // Default appointment fee - can be customized per hospital
    // In production, fetch from hospital settings
    return customAmount ?? 500.0; // Default ₹500
  }

  /// Calculate operation fee
  static double calculateOperationFee(int hospitalId, String? specialty, {double? customAmount}) {
    // Default operation fee - can be customized per hospital/specialty
    // In production, fetch from hospital settings
    double baseFee = customAmount ?? 5000.0; // Default ₹5000
    
    // Specialty-based pricing (example)
    switch (specialty?.toLowerCase()) {
      case 'surgery':
        return baseFee * 1.5; // 1.5x for surgery
      case 'ortho':
        return baseFee * 1.3; // 1.3x for ortho
      default:
        return baseFee;
    }
  }
}
