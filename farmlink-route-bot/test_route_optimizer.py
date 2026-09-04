import unittest

from app import (
    Location,
    OptimiseRequest,
    RiskLevel,
    RoadCondition,
    Vehicle,
    Weather,
    assess_weather_hazards,
    highest_risk,
    road_condition_for,
)


class RouteOptimizerModelTests(unittest.TestCase):
    def setUp(self):
        self.depot = Location(name="Depot", latitude=26.8, longitude=80.9)
        self.pickup = Location(name="Farm", latitude=26.81, longitude=80.91, access_type="farm")
        self.delivery = Location(name="Market", latitude=26.82, longitude=80.92, access_type="warehouse")

    def test_dangerous_risk_wins_over_warning(self):
        self.assertEqual(highest_risk(RiskLevel.WARNING, RiskLevel.DANGEROUS), RiskLevel.DANGEROUS)

    def test_flood_and_landslide_are_detected(self):
        weather, risk = assess_weather_hazards(
            Weather(rain_mm=35, temperature_c=25, wind_kmh=10, visibility_km=10),
            Location(name="Hill farm", latitude=26.8, longitude=80.9, elevation_m=500),
        )
        self.assertEqual(risk, RiskLevel.DANGEROUS)
        self.assertIn("flooding", [hazard.value for hazard in weather.hazards])
        self.assertIn("landslide", [hazard.value for hazard in weather.hazards])

    def test_road_condition_lookup_is_directional(self):
        condition = RoadCondition(from_name="Farm", to_name="Market", delay_multiplier=2.0, closed=True)
        self.assertIs(road_condition_for([condition], self.delivery, self.pickup), None)
        self.assertTrue(road_condition_for([condition], self.pickup, self.delivery).closed)

    def test_refrigerated_load_requires_refrigerated_vehicle(self):
        with self.assertRaises(ValueError):
            OptimiseRequest(
                depot=self.depot,
                vehicles=[Vehicle(id="truck", capacity_kg=1000)],
                orders=[{
                    "id": "cold-1",
                    "crop": "Tomato",
                    "quantity_kg": 100,
                    "requires_refrigeration": True,
                    "pickup": self.pickup,
                    "delivery": self.delivery,
                }],
            )

    def test_low_storage_temperature_requires_cold_chain(self):
        with self.assertRaises(ValueError):
            OptimiseRequest(
                depot=self.depot,
                vehicles=[Vehicle(id="truck", capacity_kg=1000)],
                orders=[{
                    "id": "cold-2",
                    "crop": "Leafy greens",
                    "quantity_kg": 100,
                    "storage_temp_c": 8,
                    "pickup": self.pickup,
                    "delivery": self.delivery,
                }],
            )


if __name__ == "__main__":
    unittest.main()
