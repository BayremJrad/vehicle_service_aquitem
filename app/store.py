"""In-memory data store for vehicles.

A simple dict keyed by an auto-incrementing integer id. Seeded with one
vehicle (id=1) so GET/PATCH/DELETE on /vehicles/1 work out of the box.
"""

from threading import Lock


class VehicleStore:
    # Fields that make up a vehicle resource. The order here is also the
    # order used when serializing responses.
    FIELDS = ("id", "nickName", "vin", "make", "model", "year", "miles")

    def __init__(self):
        self._vehicles = {}
        self._next_id = 1
        self._lock = Lock()
        # Seed data so id=1 exists on startup.
        self.create(
            {
                "nickName": "The Lisa Marie",
                "vin": "4M2DV11W4RDJ53329",
                "make": "Mercury",
                "model": "Villager",
                "year": "1994",
                "miles": 159864,
            }
        )

    def _serialize(self, vehicle):
        """Return a dict with exactly the allowed fields, in a stable order.

        year is always a string, miles is always a number.
        """
        out = {}
        for field in self.FIELDS:
            if field not in vehicle:
                continue
            value = vehicle[field]
            if field == "year" and value is not None:
                value = str(value)
            if field == "miles" and value is not None:
                # keep it numeric (int when possible)
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
            out[field] = value
        return out

    def list_all(self):
        with self._lock:
            return [self._serialize(v) for v in self._vehicles.values()]

    def get(self, vehicle_id):
        with self._lock:
            vehicle = self._vehicles.get(vehicle_id)
            return self._serialize(vehicle) if vehicle else None

    def find_by_vin(self, vin):
        with self._lock:
            for v in self._vehicles.values():
                if v.get("vin") == vin:
                    return self._serialize(v)
        return None

    def create(self, data):
        with self._lock:
            vehicle_id = self._next_id
            self._next_id += 1
            vehicle = {"id": vehicle_id}
            for field in self.FIELDS:
                if field == "id":
                    continue
                if field in data:
                    vehicle[field] = data[field]
            self._vehicles[vehicle_id] = vehicle
            return self._serialize(vehicle)

    def update(self, vehicle_id, data):
        with self._lock:
            vehicle = self._vehicles.get(vehicle_id)
            if not vehicle:
                return None
            for field in self.FIELDS:
                if field == "id":
                    continue
                if field in data:
                    vehicle[field] = data[field]
            return self._serialize(vehicle)

    def delete(self, vehicle_id):
        with self._lock:
            if vehicle_id in self._vehicles:
                del self._vehicles[vehicle_id]
                return True
            return False
