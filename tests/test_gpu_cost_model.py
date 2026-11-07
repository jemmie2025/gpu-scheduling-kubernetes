"""Unit tests for the GPU infrastructure cost model."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from gpu_cost_model import Scenario, calculate


class TestGPUCostModel(unittest.TestCase):

    def test_dedicated_gpu_cost(self):
        scenario = Scenario("Dedicated", 1, 4.0, 120, 55, 0.99)
        result = calculate(scenario)

        self.assertEqual(result["total_cost_usd"], 480.0)
        self.assertEqual(result["successful_requests"], 6534.0)
        self.assertAlmostEqual(
            result["cost_per_1000_successful_usd"], 73.4619, places=4
        )

    def test_mig_gpu_cost(self):
        scenario = Scenario("MIG", 1, 4.0, 120, 80, 0.98)
        result = calculate(scenario)

        self.assertEqual(result["total_cost_usd"], 480.0)
        self.assertEqual(result["successful_requests"], 9408.0)

    def test_time_slicing_cost(self):
        scenario = Scenario("Time-slicing", 1, 4.0, 120, 110, 0.90)
        result = calculate(scenario)

        self.assertEqual(result["total_cost_usd"], 480.0)
        self.assertEqual(result["successful_requests"], 11880.0)

    def test_multiple_nodes(self):
        scenario = Scenario("Multi-node", 2, 4.0, 120, 50, 1.0)
        result = calculate(scenario)

        self.assertEqual(result["total_cost_usd"], 960.0)
        self.assertEqual(result["successful_requests"], 12000.0)

    def test_zero_nodes_rejected(self):
        scenario = Scenario("Invalid", 0, 4.0, 120, 50, 1.0)

        with self.assertRaises(ValueError):
            calculate(scenario)

    def test_negative_price_rejected(self):
        scenario = Scenario("Invalid", 1, -4.0, 120, 50, 1.0)

        with self.assertRaises(ValueError):
            calculate(scenario)

    def test_zero_duration_rejected(self):
        scenario = Scenario("Invalid", 1, 4.0, 0, 50, 1.0)

        with self.assertRaises(ValueError):
            calculate(scenario)

    def test_zero_throughput_rejected(self):
        scenario = Scenario("Invalid", 1, 4.0, 120, 0, 1.0)

        with self.assertRaises(ValueError):
            calculate(scenario)

    def test_invalid_success_rate_rejected(self):
        for rate in (0, -0.5, 1.5):
            with self.subTest(rate=rate):
                scenario = Scenario("Invalid", 1, 4.0, 120, 50, rate)

                with self.assertRaises(ValueError):
                    calculate(scenario)


if __name__ == "__main__":
    unittest.main()