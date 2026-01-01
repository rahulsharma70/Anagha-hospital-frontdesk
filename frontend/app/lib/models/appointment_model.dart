class Appointment {
  final int id;
  final int userId;
  final int doctorId;
  final int? hospitalId;
  final DateTime date;
  final String timeSlot;
  final String status;
  final DateTime? visitDate;
  final DateTime? followupDate;
  final DateTime createdAt;
  final String? userName;
  final String? doctorName;

  Appointment({
    required this.id,
    required this.userId,
    required this.doctorId,
    this.hospitalId,
    required this.date,
    required this.timeSlot,
    required this.status,
    this.visitDate,
    this.followupDate,
    required this.createdAt,
    this.userName,
    this.doctorName,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'],
      userId: json['user_id'],
      doctorId: json['doctor_id'],
      hospitalId: json['hospital_id'],
      date: DateTime.parse(json['date']),
      timeSlot: json['time_slot'],
      status: json['status'],
      visitDate: json['visit_date'] != null ? DateTime.parse(json['visit_date']) : null,
      followupDate: json['followup_date'] != null ? DateTime.parse(json['followup_date']) : null,
      createdAt: DateTime.parse(json['created_at']),
      userName: json['user_name'],
      doctorName: json['doctor_name'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'doctor_id': doctorId,
      'date': date.toIso8601String().split('T')[0],
      'time_slot': timeSlot,
    };
  }
}



