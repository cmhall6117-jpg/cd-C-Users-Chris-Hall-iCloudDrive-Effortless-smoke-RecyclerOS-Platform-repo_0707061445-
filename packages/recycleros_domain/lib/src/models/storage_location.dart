class StorageLocation {
  final String storageLocationId;
  final String locationCode;
  final String name;
  final String? zone;
  final String? rack;
  final String? shelf;
  final String? bin;

  const StorageLocation({
    required this.storageLocationId,
    required this.locationCode,
    required this.name,
    this.zone,
    this.rack,
    this.shelf,
    this.bin,
  });
}
