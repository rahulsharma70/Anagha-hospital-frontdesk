import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:intl/intl.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import '../services/payment_service.dart';
import '../models/hospital_model.dart';
import '../utils/app_colors.dart';
import '../widgets/city_autocomplete.dart';
import 'dart:convert';

class BookOperationScreen extends StatefulWidget {
  const BookOperationScreen({super.key});

  @override
  State<BookOperationScreen> createState() => _BookOperationScreenState();
}

class _BookOperationScreenState extends State<BookOperationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _mobileController = TextEditingController();
  final _placeController = TextEditingController();
  final _timeController = TextEditingController();
  
  DateTime _selectedDate = DateTime.now();
  String? _selectedAmPm = 'AM';
  Hospital? _selectedHospital;
  bool _isLoading = false;
  bool _showPaymentOptions = false;
  String? _selectedPaymentMethod;
  String? _paymentOrderId; // Store payment order ID
  List<Hospital> _hospitals = [];

  @override
  void initState() {
    super.initState();
    _loadHospitals();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _mobileController.dispose();
    _placeController.dispose();
    _timeController.dispose();
    super.dispose();
  }

  Future<void> _loadHospitals() async {
    try {
      final response = await ApiService.get('/api/hospitals/approved');
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        setState(() {
          _hospitals = data.map((json) => Hospital.fromJson(json)).toList();
          if (_hospitals.isNotEmpty) {
            _selectedHospital = _hospitals.first;
          }
        });
      }
    } catch (e) {
      print('Error loading hospitals: $e');
    }
  }

  String? _getUpiIdForMethod(String method) {
    if (_selectedHospital == null) return null;
    
    switch (method) {
      case 'googlepay':
        return _selectedHospital!.googlePayUpiId ?? _selectedHospital!.defaultUpiId;
      case 'phonepe':
        return _selectedHospital!.phonePeUpiId ?? _selectedHospital!.defaultUpiId;
      case 'paytm':
        return _selectedHospital!.paytmUpiId ?? _selectedHospital!.defaultUpiId;
      case 'bhim':
        return _selectedHospital!.bhimUpiId ?? _selectedHospital!.defaultUpiId;
      default:
        return _selectedHospital!.defaultUpiId;
    }
  }

  Future<void> _openUpiApp(String method, String? upiId) async {
    if (upiId == null || upiId.isEmpty) {
      Fluttertoast.showToast(
        msg: 'UPI ID not configured for this payment method',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    String upiUrl = '';
    switch (method) {
      case 'googlepay':
        upiUrl = 'tez://upi/pay?pa=$upiId&pn=Hospital&am=&cu=INR';
        break;
      case 'phonepe':
        upiUrl = 'phonepe://pay?pa=$upiId&pn=Hospital&am=&cu=INR';
        break;
      case 'paytm':
        upiUrl = 'paytmmp://pay?pa=$upiId&pn=Hospital&am=&cu=INR';
        break;
      case 'bhim':
        upiUrl = 'upi://pay?pa=$upiId&pn=Hospital&am=&cu=INR';
        break;
    }

    try {
      final uri = Uri.parse(upiUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        // Fallback to generic UPI
        final paymentAmount = PaymentService.calculateOperationFee(_selectedHospital!.id, null);
        final encodedUpiId = Uri.encodeComponent(upiId);
        final encodedHospitalName = Uri.encodeComponent(_selectedHospital!.name);
        final encodedAmount = paymentAmount.toStringAsFixed(2);
        final genericUri = Uri.parse('upi://pay?pa=$encodedUpiId&pn=$encodedHospitalName&am=$encodedAmount&cu=INR');
        if (await canLaunchUrl(genericUri)) {
          await launchUrl(genericUri, mode: LaunchMode.externalApplication);
        } else {
          Fluttertoast.showToast(
            msg: 'Please install a UPI app to make payment',
            backgroundColor: AppColors.errorColor,
          );
        }
      }
    } catch (e) {
      Fluttertoast.showToast(
        msg: 'Error opening payment app',
        backgroundColor: AppColors.errorColor,
      );
    }
  }

  Future<void> _proceedToPayment() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_selectedHospital == null) {
      Fluttertoast.showToast(
        msg: 'Please select a hospital',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Calculate payment amount
      final paymentAmount = PaymentService.calculateOperationFee(_selectedHospital!.id, null);
      
      // Create payment order
      final paymentOrderResponse = await PaymentService.createPaymentOrder(
        type: 'operation',
        hospitalId: _selectedHospital!.id,
        patientName: _nameController.text.trim(),
        patientMobile: _mobileController.text.trim(),
        amount: paymentAmount,
        metadata: {
          'operation_date': DateFormat('yyyy-MM-dd').format(_selectedDate),
          'operation_time': '${_timeController.text.trim()} $_selectedAmPm',
          'place': _placeController.text.trim(),
        },
      );

      if (paymentOrderResponse == null || paymentOrderResponse['order_id'] == null) {
        throw Exception('Failed to create payment order. Please try again.');
      }

      setState(() {
        _paymentOrderId = paymentOrderResponse['order_id'] as String;
        _showPaymentOptions = true;
        _isLoading = false;
      });

      Fluttertoast.showToast(
        msg: 'Payment order created. Please complete payment.',
        backgroundColor: AppColors.infoColor,
      );
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

  Future<void> _confirmPaymentAndBook() async {
    if (_selectedPaymentMethod == null) {
      Fluttertoast.showToast(
        msg: 'Please select a payment method',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    if (_paymentOrderId == null) {
      Fluttertoast.showToast(
        msg: 'Payment order not created. Please try again.',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // First, verify payment status
      final paymentStatus = await PaymentService.getPaymentStatus(_paymentOrderId!);
      
      if (paymentStatus == null) {
        throw Exception('Could not verify payment status. Please try again.');
      }

      // For UPI payments, we'll mark as paid if order exists (manual verification)
      final paymentStatusValue = paymentStatus['status'] as String? ?? paymentStatus['status'];
      final isPaid = paymentStatusValue == 'paid' || 
                     paymentStatusValue == 'completed' ||
                     (_paymentOrderId!.startsWith('UPI_') && paymentStatusValue == 'created');

      if (!isPaid) {
        // Show dialog to confirm payment completion
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Payment Confirmation'),
            content: const Text(
              'Please confirm that you have completed the payment. '
              'If payment is not completed, the booking will be cancelled.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Payment Completed'),
              ),
            ],
          ),
        );

        if (confirmed != true) {
          setState(() {
            _isLoading = false;
          });
          return;
        }
      }

      final timeString = '${_timeController.text.trim()} $_selectedAmPm';
      final response = await ApiService.post(
        '/api/operations/book',
        {
          'patient_name': _nameController.text.trim(),
          'patient_mobile': _mobileController.text.trim(),
          'place': _placeController.text.trim(),
          'date': DateFormat('yyyy-MM-dd').format(_selectedDate),
          'time': timeString,
          'hospital_id': _selectedHospital!.id,
          'order_id': _paymentOrderId, // Include payment order ID
          'payment_method': _selectedPaymentMethod,
        },
      );

      setState(() {
        _isLoading = false;
      });

      if (response.statusCode == 200 || response.statusCode == 201) {
        Fluttertoast.showToast(
          msg: 'Operation booked successfully!',
          backgroundColor: AppColors.successColor,
        );
        Navigator.pop(context);
      } else {
        try {
          final error = jsonDecode(response.body);
          Fluttertoast.showToast(
            msg: error['detail'] ?? 'Failed to book operation',
            backgroundColor: AppColors.errorColor,
          );
        } catch (e) {
          Fluttertoast.showToast(
            msg: 'Failed to book operation',
            backgroundColor: AppColors.errorColor,
          );
        }
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      Fluttertoast.showToast(
        msg: 'Error booking operation: ${e.toString()}',
        backgroundColor: AppColors.errorColor,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Book Operation'),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Patient Name
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Name of Patient *',
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter patient name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),

              // Mobile Number
              TextFormField(
                controller: _mobileController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Mobile No *',
                  prefixIcon: Icon(Icons.phone),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter mobile number';
                  }
                  if (value.length != 10) {
                    return 'Please enter a valid 10-digit mobile number';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),

              // Place (City Name) - Autocomplete
              CityAutocomplete(
                controller: _placeController,
                labelText: 'Place (Name of City) *',
                hintText: 'Start typing city name...',
                prefixIcon: Icons.location_city,
              ),
              const SizedBox(height: 20),

              // Calendar
              Card(
                child: TableCalendar(
                  firstDay: DateTime.now(),
                  lastDay: DateTime.now().add(const Duration(days: 365)),
                  focusedDay: _selectedDate,
                  selectedDayPredicate: (day) {
                    return isSameDay(_selectedDate, day);
                  },
                  onDaySelected: (selectedDay, focusedDay) {
                    setState(() {
                      _selectedDate = selectedDay;
                    });
                  },
                  calendarStyle: const CalendarStyle(
                    selectedDecoration: BoxDecoration(
                      color: AppColors.primaryColor,
                      shape: BoxShape.circle,
                    ),
                    todayDecoration: BoxDecoration(
                      color: AppColors.secondaryColor,
                      shape: BoxShape.circle,
                    ),
                  ),
                  headerStyle: const HeaderStyle(
                    formatButtonVisible: false,
                    titleCentered: true,
                  ),
                ),
              ),
              const SizedBox(height: 30),

              // Time Selection (AM/PM)
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _timeController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Time *',
                        prefixIcon: Icon(Icons.access_time),
                        hintText: 'e.g., 10:30',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter time';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      value: _selectedAmPm,
                      decoration: const InputDecoration(
                        labelText: 'AM/PM *',
                        prefixIcon: Icon(Icons.schedule),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'AM', child: Text('AM')),
                        DropdownMenuItem(value: 'PM', child: Text('PM')),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedAmPm = value;
                        });
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 30),

              // Hospital Selection
              DropdownButtonFormField<int>(
                value: _selectedHospital?.id,
                decoration: const InputDecoration(
                  labelText: 'Select Hospital *',
                  prefixIcon: Icon(Icons.local_hospital),
                ),
                items: _hospitals.isEmpty
                    ? [
                        const DropdownMenuItem<int>(
                          value: null,
                          child: Text('No hospitals available'),
                          enabled: false,
                        )
                      ]
                    : _hospitals.map((hospital) {
                        return DropdownMenuItem<int>(
                          value: hospital.id,
                          child: Text(hospital.name),
                        );
                      }).toList(),
                onChanged: _hospitals.isEmpty
                    ? null
                    : (value) {
                        setState(() {
                          _selectedHospital = _hospitals.firstWhere((h) => h.id == value);
                          _showPaymentOptions = false;
                          _selectedPaymentMethod = null;
                        });
                      },
                validator: (value) {
                  if (value == null) {
                    return 'Please select a hospital';
                  }
                  return null;
                },
              ),
              if (_hospitals.isEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8.0, left: 16.0),
                  child: Text(
                    'No approved hospitals available. Please contact administrator.',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.warningColor,
                    ),
                  ),
                ),
              const SizedBox(height: 30),

              // Payment Options Section
              if (_showPaymentOptions && _selectedHospital != null) ...[
                const Divider(),
                const SizedBox(height: 20),
                const Text(
                  'Payment Options - Doctor Fee',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                const SizedBox(height: 20),

                // Payment Method Selection
                const Text(
                  'Select Payment Method *',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 10),

                // Google Pay
                if (_selectedHospital!.googlePayUpiId != null || _selectedHospital!.defaultUpiId != null)
                  _buildPaymentOption(
                    'Google Pay',
                    '📱',
                    'googlepay',
                    _getUpiIdForMethod('googlepay') ?? '',
                  ),

                // PhonePe
                if (_selectedHospital!.phonePeUpiId != null || _selectedHospital!.defaultUpiId != null)
                  _buildPaymentOption(
                    'PhonePe',
                    '💳',
                    'phonepe',
                    _getUpiIdForMethod('phonepe') ?? '',
                  ),

                // Paytm
                if (_selectedHospital!.paytmUpiId != null || _selectedHospital!.defaultUpiId != null)
                  _buildPaymentOption(
                    'Paytm',
                    '💵',
                    'paytm',
                    _getUpiIdForMethod('paytm') ?? '',
                  ),

                // BHIM UPI
                if (_selectedHospital!.bhimUpiId != null || _selectedHospital!.defaultUpiId != null)
                  _buildPaymentOption(
                    'BHIM UPI',
                    '🏦',
                    'bhim',
                    _getUpiIdForMethod('bhim') ?? '',
                  ),

                const SizedBox(height: 20),

                // QR Code Display
                if (_selectedPaymentMethod != null)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          const Text(
                            'Scan QR Code to Pay',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 20),
                          Builder(
                            builder: (context) {
                              final upiId = _getUpiIdForMethod(_selectedPaymentMethod!);
                              if (upiId == null || upiId.isEmpty) {
                                return const Text('UPI ID not available');
                              }
                              
                              final paymentAmount = PaymentService.calculateOperationFee(_selectedHospital!.id, null);
                              final encodedUpiId = Uri.encodeComponent(upiId);
                              final encodedHospitalName = Uri.encodeComponent(_selectedHospital!.name);
                              final encodedAmount = paymentAmount.toStringAsFixed(2);
                              final upiPaymentString = 'upi://pay?pa=$encodedUpiId&pn=$encodedHospitalName&am=$encodedAmount&cu=INR';
                              
                              if (_selectedHospital!.paymentQrCode != null && 
                                  _selectedHospital!.paymentQrCode!.isNotEmpty &&
                                  _selectedHospital!.paymentQrCode!.startsWith('http')) {
                                return Image.network(
                                  _selectedHospital!.paymentQrCode!,
                                  width: 250,
                                  height: 250,
                                  errorBuilder: (context, error, stackTrace) {
                                    return QrImageView(
                                      data: upiPaymentString,
                                      version: QrVersions.auto,
                                      size: 250,
                                    );
                                  },
                                );
                              } else {
                                return QrImageView(
                                  data: upiPaymentString,
                                  version: QrVersions.auto,
                                  size: 250,
                                );
                              }
                            },
                          ),
                          const SizedBox(height: 20),
                          Text(
                            _getUpiIdForMethod(_selectedPaymentMethod!) ?? '',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 10),
                          ElevatedButton.icon(
                            onPressed: () => _openUpiApp(_selectedPaymentMethod!, _getUpiIdForMethod(_selectedPaymentMethod!)),
                            icon: const Icon(Icons.payment),
                            label: const Text('Open Payment App'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                const SizedBox(height: 20),

                // Refund Policy Note
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.errorColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.errorColor.withOpacity(0.3)),
                  ),
                  child: const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.warning, color: AppColors.errorColor, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Important Notice',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: AppColors.errorColor,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 10),
                      Text(
                        'Once payment is done and operation is booked, there will be no refund of the booking amount.',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppColors.textDark,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 30),
              ],

              // Proceed to Payment / Book Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading
                      ? null
                      : _showPaymentOptions
                          ? _confirmPaymentAndBook
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
                          _showPaymentOptions ? 'Confirm Payment & Book Operation' : 'Proceed to Payment',
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
      ),
    );
  }

  Widget _buildPaymentOption(String name, String emoji, String method, String upiId) {
    final isSelected = _selectedPaymentMethod == method;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      color: isSelected ? AppColors.primaryColor.withOpacity(0.1) : null,
      child: ListTile(
        leading: Text(emoji, style: const TextStyle(fontSize: 24)),
        title: Text(name),
        subtitle: upiId.isNotEmpty ? Text(upiId, style: const TextStyle(fontSize: 12)) : null,
        trailing: Radio<String>(
          value: method,
          groupValue: _selectedPaymentMethod,
          onChanged: (value) {
            setState(() {
              _selectedPaymentMethod = value;
            });
          },
        ),
        onTap: () {
          setState(() {
            _selectedPaymentMethod = method;
          });
        },
      ),
    );
  }
}

