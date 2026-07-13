import 'vehicle_lifecycle_status.dart';

class Vehicle {
  final String vehicleId;
  final String vehicleCode;
  final String? vin;
  final int? year;
  final String? make;
  final String? model;
  final String? trim;
  final String? engine;
  final String? transmission;
  final String? drivetrain;
  final String? exteriorColor;
  final String? interiorColor;
  final int? mileage;
  final VehicleLifecycleStatus lifecycleStatus;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Vehicle({
    required this.vehicleId,
    required this.vehicleCode,
    this.vin,
    this.year,
    this.make,
    this.model,
    this.trim,
    this.engine,
    this.transmission,
    this.drivetrain,
    this.exteriorColor,
    this.interiorColor,
    this.mileage,
    required this.lifecycleStatus,
    required this.createdAt,
    required this.updatedAt,
  });
}
