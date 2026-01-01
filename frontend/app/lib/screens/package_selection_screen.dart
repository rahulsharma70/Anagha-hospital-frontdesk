import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../utils/app_colors.dart';
import '../services/payment_service.dart';
import 'hospital_register_screen.dart';

class PackageSelectionScreen extends StatefulWidget {
  final Map<String, dynamic> hospitalData;

  const PackageSelectionScreen({
    super.key,
    required this.hospitalData,
  });

  @override
  State<PackageSelectionScreen> createState() => _PackageSelectionScreenState();
}

class _PackageSelectionScreenState extends State<PackageSelectionScreen> {
  String? _selectedPackage;
  String? _selectedBillingPeriod;
  bool _isLoading = false;
  String? _paymentOrderId;

  final Map<String, Map<String, dynamic>> _packages = {
    'basic': {
      'name': 'Basic',
      'monthly_price': 5000,
      'yearly_price': 50000,
      'appointments': 50,
      'operations': 5,
      'pharma_appointments': 25,
      'color': Colors.blue,
    },
    'standard': {
      'name': 'Standard',
      'monthly_price': 15000,
      'yearly_price': 150000,
      'appointments': 200,
      'operations': 20,
      'pharma_appointments': 100,
      'color': Colors.purple,
    },
    'premium': {
      'name': 'Premium',
      'monthly_price': 50000,
      'yearly_price': 500000,
      'appointments': 1000,
      'operations': 100,
      'pharma_appointments': 500,
      'color': Colors.orange,
    },
  };

  Future<void> _proceedToPayment() async {
    if (_selectedPackage == null || _selectedBillingPeriod == null) {
      Fluttertoast.showToast(
        msg: 'Please select a package and billing period',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final package = _packages[_selectedPackage!]!;
      final amount = _selectedBillingPeriod == 'monthly'
          ? package['monthly_price'] as double
          : package['yearly_price'] as double;

      // Create payment order
      final paymentOrderResponse = await PaymentService.createPaymentOrder(
        type: 'hospital_registration',
        hospitalId: 0, // Will be set after registration
        patientName: widget.hospitalData['name'] ?? '',
        patientMobile: widget.hospitalData['mobile'] ?? '',
        amount: amount,
        metadata: {
          'hospital_name': widget.hospitalData['name'] ?? '',
          'hospital_email': widget.hospitalData['email'] ?? '',
          'package_type': _selectedPackage!,
          'billing_period': _selectedBillingPeriod!,
        },
      );

      if (paymentOrderResponse == null || paymentOrderResponse['order_id'] == null) {
        throw Exception('Failed to create payment order');
      }

      final orderId = paymentOrderResponse['order_id'] as String;

      setState(() {
        _paymentOrderId = orderId;
        _isLoading = false;
      });

      // Navigate to payment screen with order ID
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => HospitalRegisterScreen(
              initialPaymentOrderId: orderId,
              selectedPackage: _selectedPackage!,
              selectedBillingPeriod: _selectedBillingPeriod!,
            ),
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      Fluttertoast.showToast(
        msg: 'Error creating payment order: ${e.toString()}',
        backgroundColor: AppColors.errorColor,
      );
    }
  }

  Widget _buildPackageCard(String packageKey, Map<String, dynamic> package) {
    final isSelected = _selectedPackage == packageKey;
    final color = package['color'] as Color;
    final monthlyPrice = package['monthly_price'] as int;
    final yearlyPrice = package['yearly_price'] as int;

    return Card(
      elevation: isSelected ? 6 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
        side: BorderSide(
          color: isSelected ? color : Colors.transparent,
          width: isSelected ? 3 : 0,
        ),
      ),
      child: InkWell(
        onTap: () {
          setState(() {
            _selectedPackage = packageKey;
          });
        },
        borderRadius: BorderRadius.circular(15),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(Icons.star, color: color, size: 30),
                  ),
                  const SizedBox(width: 15),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          package['name'] as String,
                          style: TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: color,
                          ),
                        ),
                        if (isSelected)
                          const Text(
                            'Selected',
                            style: TextStyle(
                              fontSize: 12,
                              color: AppColors.successColor,
                            ),
                          ),
                      ],
                    ),
                  ),
                  if (isSelected)
                    Icon(Icons.check_circle, color: color, size: 30),
                ],
              ),
              const SizedBox(height: 20),
              _buildFeatureRow('Appointments', '${package['appointments']}/month'),
              const SizedBox(height: 10),
              _buildFeatureRow('Operations', '${package['operations']}/month'),
              const SizedBox(height: 10),
              _buildFeatureRow('Pharma Appointments', '${package['pharma_appointments']}/month'),
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 15),
              if (_selectedPackage == packageKey) ...[
                Row(
                  children: [
                    Expanded(
                      child: _buildBillingOption('monthly', 'Monthly', monthlyPrice.toDouble()),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _buildBillingOption('yearly', 'Yearly', yearlyPrice.toDouble()),
                    ),
                  ],
                ),
              ] else ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Monthly',
                          style: TextStyle(fontSize: 12, color: AppColors.textLight),
                        ),
                        Text(
                          '₹${monthlyPrice.toString()}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        const Text(
                          'Yearly',
                          style: TextStyle(fontSize: 12, color: AppColors.textLight),
                        ),
                        Text(
                          '₹${yearlyPrice.toString()}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBillingOption(String period, String label, double price) {
    final isSelected = _selectedBillingPeriod == period;
    return InkWell(
      onTap: () {
        setState(() {
          _selectedBillingPeriod = period;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(15),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primaryColor.withOpacity(0.1) : Colors.grey.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isSelected ? AppColors.primaryColor : Colors.transparent,
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: isSelected ? AppColors.primaryColor : AppColors.textDark,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              '₹${price.toStringAsFixed(0)}',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: isSelected ? AppColors.primaryColor : AppColors.textDark,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: AppColors.textLight),
        ),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: AppColors.textDark,
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Package'),
        backgroundColor: AppColors.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Choose Your Package',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppColors.textDark,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Select a package that suits your hospital\'s needs',
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textLight,
              ),
            ),
            const SizedBox(height: 30),
            ..._packages.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 20),
                child: _buildPackageCard(entry.key, entry.value),
              );
            }),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading || _selectedPackage == null || _selectedBillingPeriod == null
                    ? null
                    : _proceedToPayment,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryColor,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(
                        _selectedPackage == null || _selectedBillingPeriod == null
                            ? 'Select Package & Billing Period'
                            : 'Proceed to Payment',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

