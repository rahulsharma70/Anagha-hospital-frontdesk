import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import '../services/payment_service.dart';
import '../services/auth_service.dart';
import '../services/doctor_service.dart';
import '../models/hospital_model.dart';
import '../utils/app_colors.dart';
import '../widgets/doctor_autocomplete.dart';
import '../widgets/city_autocomplete.dart';
import 'dart:convert';

class BookPharmaAppointmentScreen extends StatefulWidget {
  const BookPharmaAppointmentScreen({super.key});

  @override
  State<BookPharmaAppointmentScreen> createState() => _BookPharmaAppointmentScreenState();
}

class _BookPharmaAppointmentScreenState extends State<BookPharmaAppointmentScreen> {
  final _formKey = GlobalKey<FormState>();
  final _doctorController = TextEditingController();
  final _placeController = TextEditingController();
  final _timeController = TextEditingController();
  final _companyNameController = TextEditingController();
  final _product1Controller = TextEditingController();
  final _product2Controller = TextEditingController();
  final _product3Controller = TextEditingController();
  final _product4Controller = TextEditingController();
  
  DateTime _selectedDate = DateTime.now();
  String? _selectedAmPm = 'AM';
  Hospital? _selectedHospital;
  bool _isLoading = false;
  bool _showPaymentOptions = false;
  String? _selectedPaymentMethod;
  List<Hospital> _hospitals = [];
  Map<String, dynamic>? _selectedDoctor;
  int? _selectedDoctorId;

  @override
  void initState() {
    super.initState();
    _loadHospitals();
    // Listen to doctor controller changes to update doctor ID
    _doctorController.addListener(_onDoctorNameChanged);
  }
  
  void _onDoctorNameChanged() {
    final doctorName = _doctorController.text.trim();
    if (doctorName.isNotEmpty && _selectedDoctorId == null) {
      // Search for doctor when name is entered
      _onDoctorSelected(doctorName);
    } else if (doctorName.isEmpty) {
      setState(() {
        _selectedDoctorId = null;
        _selectedDoctor = null;
      });
    }
  }
  
  // Callback to handle doctor selection
  Future<void> _onDoctorSelected(String doctorName) async {
    // Search for doctor by name to get ID
    await _searchDoctorByName(doctorName);
  }
  
  Future<void> _searchDoctorByName(String doctorName) async {
    try {
      final doctors = await DoctorService.searchDoctors(doctorName);
      if (doctors.isNotEmpty) {
        final doctor = doctors.firstWhere(
          (d) => d['doctor_name']?.toString().toLowerCase() == doctorName.toLowerCase(),
          orElse: () => doctors.first,
        );
        setState(() {
          _selectedDoctor = doctor;
          _selectedDoctorId = doctor['id'] as int?;
        });
      }
    } catch (e) {
      print('Error searching doctor: $e');
    }
  }

  @override
  void dispose() {
    _doctorController.removeListener(_onDoctorNameChanged);
    _doctorController.dispose();
    _placeController.dispose();
    _timeController.dispose();
    _companyNameController.dispose();
    _product1Controller.dispose();
    _product2Controller.dispose();
    _product3Controller.dispose();
    _product4Controller.dispose();
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
        Fluttertoast.showToast(
          msg: 'Payment app not installed',
          backgroundColor: AppColors.errorColor,
        );
      }
    } catch (e) {
      Fluttertoast.showToast(
        msg: 'Error opening payment app: $e',
        backgroundColor: AppColors.errorColor,
      );
    }
  }

  Future<void> _selectTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    );
    if (picked != null) {
      setState(() {
        final hour = picked.hour;
        final minute = picked.minute;
        _selectedAmPm = hour >= 12 ? 'PM' : 'AM';
        final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
        _timeController.text = '${displayHour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
      });
    }
  }

  Future<void> _submitBooking() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final authService = Provider.of<AuthService>(context, listen: false);
    if (!authService.isAuthenticated || authService.user?.role != 'pharma') {
      Fluttertoast.showToast(
        msg: 'Only pharma professionals can book appointments',
        backgroundColor: AppColors.errorColor,
      );
      return;
    }

    if (_selectedDoctorId == null) {
      Fluttertoast.showToast(
        msg: 'Please select a doctor',
        backgroundColor: AppColors.errorColor,
      );
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
      // Step 1: Create appointment
      final appointmentData = {
        'pharma_user_id': authService.user!.id,
        'doctor_id': _selectedDoctorId,
        'appointment_date': DateFormat('yyyy-MM-dd').format(_selectedDate),
        'appointment_time': '${_timeController.text} ${_selectedAmPm}',
        'company_name': _companyNameController.text.trim(),
        'product1': _product1Controller.text.trim().isEmpty ? null : _product1Controller.text.trim(),
        'product2': _product2Controller.text.trim().isEmpty ? null : _product2Controller.text.trim(),
        'product3': _product3Controller.text.trim().isEmpty ? null : _product3Controller.text.trim(),
        'product4': _product4Controller.text.trim().isEmpty ? null : _product4Controller.text.trim(),
        'place': _placeController.text.trim(),
        'hospital_id': _selectedHospital!.id,
      };

      final appointmentResponse = await ApiService.post(
        '/api/pharma-appointments/book',
        appointmentData,
      );

      if (appointmentResponse.statusCode != 200 && appointmentResponse.statusCode != 201) {
        throw Exception('Failed to create appointment: ${appointmentResponse.body}');
      }

      final appointmentResult = jsonDecode(appointmentResponse.body);
      final appointmentId = appointmentResult['id'];

      // Step 2: Create payment order
      final paymentAmount = 500.0; // Fixed fee for pharma appointments
      final paymentOrderResponse = await PaymentService.createPaymentOrder(
        type: 'pharma_appointment',
        hospitalId: _selectedHospital!.id,
        patientName: authService.user!.name,
        patientMobile: authService.user!.mobile,
        amount: paymentAmount,
        metadata: {
          'entity_id': appointmentId,
          'entity_type': 'pharma_appointment',
          'description': 'Pharma Appointment with ${_doctorController.text}',
        },
      );

      if (paymentOrderResponse == null) {
        throw Exception('Failed to create payment order');
      }

      final orderId = paymentOrderResponse['order_id'];
      if (orderId == null) {
        throw Exception('Failed to create payment order - no order ID returned');
      }

      // Step 3: Show payment options
      setState(() {
        _showPaymentOptions = true;
        _isLoading = false;
      });

      Fluttertoast.showToast(
        msg: 'Please complete payment to confirm appointment',
        backgroundColor: AppColors.infoColor,
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      Fluttertoast.showToast(
        msg: 'Error booking appointment: $e',
        backgroundColor: AppColors.errorColor,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Book Pharma Appointment'),
        backgroundColor: AppColors.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (!_showPaymentOptions) ...[
                // Doctor Selection
                DoctorAutocomplete(
                  controller: _doctorController,
                  labelText: 'Select Doctor *',
                  hintText: 'Start typing doctor name...',
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please select a doctor';
                    }
                    return null;
                  },
                  hospitalId: _selectedHospital?.id,
                ),
                const SizedBox(height: 20),

                // Place (City)
                CityAutocomplete(
                  controller: _placeController,
                  labelText: 'Place (Name of City) *',
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter place/city name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),

                // Hospital Selection
                DropdownButtonFormField<Hospital>(
                  value: _selectedHospital,
                  decoration: const InputDecoration(
                    labelText: 'Select Hospital *',
                    prefixIcon: Icon(Icons.local_hospital),
                  ),
                  items: _hospitals.map((hospital) {
                    return DropdownMenuItem(
                      value: hospital,
                      child: Text(hospital.name),
                    );
                  }).toList(),
                  onChanged: (hospital) {
                    setState(() {
                      _selectedHospital = hospital;
                    });
                  },
                  validator: (value) {
                    if (value == null) {
                      return 'Please select a hospital';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),

                // Date Selection
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Select Date *',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 10),
                        TableCalendar(
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
                          calendarFormat: CalendarFormat.month,
                          startingDayOfWeek: StartingDayOfWeek.monday,
                          headerStyle: const HeaderStyle(
                            formatButtonVisible: false,
                            titleCentered: true,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Time Selection
                TextFormField(
                  controller: _timeController,
                  decoration: InputDecoration(
                    labelText: 'Time *',
                    prefixIcon: const Icon(Icons.access_time),
                    suffixIcon: DropdownButton<String>(
                      value: _selectedAmPm,
                      items: ['AM', 'PM'].map((ampm) {
                        return DropdownMenuItem(
                          value: ampm,
                          child: Text(ampm),
                        );
                      }).toList(),
                      onChanged: (value) {
                        setState(() {
                          _selectedAmPm = value;
                        });
                      },
                    ),
                  ),
                  readOnly: true,
                  onTap: _selectTime,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please select time';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 30),

                // Pharma Professional Details
                const Divider(),
                const Text(
                  'Pharma Professional Details',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primaryColor,
                  ),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _companyNameController,
                  decoration: const InputDecoration(
                    labelText: 'Company Name *',
                    prefixIcon: Icon(Icons.business),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter company name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _product1Controller,
                  decoration: const InputDecoration(
                    labelText: 'Product 1 (for reminders if appointment cancelled by Dr)',
                    prefixIcon: Icon(Icons.inventory),
                  ),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _product2Controller,
                  decoration: const InputDecoration(
                    labelText: 'Product 2',
                    prefixIcon: Icon(Icons.inventory),
                  ),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _product3Controller,
                  decoration: const InputDecoration(
                    labelText: 'Product 3',
                    prefixIcon: Icon(Icons.inventory),
                  ),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: _product4Controller,
                  decoration: const InputDecoration(
                    labelText: 'Product 4',
                    prefixIcon: Icon(Icons.inventory),
                  ),
                ),
                const SizedBox(height: 30),

                // Submit Button
                ElevatedButton(
                  onPressed: _isLoading ? null : _submitBooking,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primaryColor,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          'Book Appointment',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                ),
              ] else ...[
                // Payment Section
                Card(
                  color: AppColors.successColor.withOpacity(0.1),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.payment,
                          size: 60,
                          color: AppColors.successColor,
                        ),
                        const SizedBox(height: 10),
                        const Text(
                          'Complete Payment',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          'Amount: ₹500.00',
                          style: TextStyle(
                            fontSize: 18,
                            color: AppColors.textDark,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Payment Methods
                if (_selectedHospital != null) ...[
                  _buildPaymentOption('Google Pay', 'googlepay', Icons.account_balance_wallet, Colors.blue),
                  const SizedBox(height: 15),
                  _buildPaymentOption('PhonePe', 'phonepe', Icons.phone_android, Colors.purple),
                  const SizedBox(height: 15),
                  _buildPaymentOption('Paytm', 'paytm', Icons.payment, Colors.blue),
                  const SizedBox(height: 15),
                  _buildPaymentOption('BHIM UPI', 'bhim', Icons.qr_code, Colors.green),
                ],

                const SizedBox(height: 20),
                const Text(
                  'Note: Once payment is done and appointment is booked, there will be no refund of the booking amount.',
                  style: TextStyle(
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                    color: AppColors.textLight,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPaymentOption(String title, String method, IconData icon, Color color) {
    final upiId = _getUpiIdForMethod(method);
    final hasUpiId = upiId != null && upiId.isNotEmpty;

    return Card(
      elevation: 2,
      child: InkWell(
        onTap: hasUpiId ? () => _openUpiApp(method, upiId) : null,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (hasUpiId)
                      Text(
                        upiId,
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.textLight,
                        ),
                      )
                    else
                      const Text(
                        'Not configured',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.errorColor,
                        ),
                      ),
                  ],
                ),
              ),
              if (hasUpiId)
                const Icon(Icons.arrow_forward_ios, size: 16)
              else
                const Icon(Icons.block, color: AppColors.errorColor),
            ],
          ),
        ),
      ),
    );
  }
}

