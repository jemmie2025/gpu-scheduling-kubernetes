#!/usr/bin/env python3
"""Reproducible illustrative GPU scheduling cost model."""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Scenario:
    name: str
    nodes: int
    hourly_rate: float
    hours: float
    requests_per_hour: float
    success_rate: float


def calculate(scenario: Scenario) -> dict:
    """Calculate infrastructure and successful-request costs."""
    if scenario.nodes <= 0:
        raise ValueError("Node count must be positive")
    if scenario.hourly_rate < 0 or scenario.hours <= 0:
        raise ValueError("Invalid price or duration")
    if scenario.requests_per_hour <= 0:
        raise ValueError("Throughput must be positive")
    if not 0 < scenario.success_rate <= 1:
        raise ValueError("Success rate must be between 0 and 1")

    total_cost = (
        scenario.nodes
        * scenario.hourly_rate
        * scenario.hours
    )
    total_requests = (
        scenario.nodes
        * scenario.requests_per_hour
        * scenario.hours
    )
    successful_requests = total_requests * scenario.success_rate

    return {
        "strategy": scenario.name,
        "total_cost_usd": round(total_cost, 2),
        "successful_requests": round(successful_requests, 2),
        "cost_per_1000_successful_usd": round(
            total_cost / successful_requests * 1000, 4
        ),
    }


def run(output: Path) -> None:
    # Hypothetical, not benchmarked or provider-quoted values.
    # Same host price and duration enable a controlled comparison.
    scenarios = [
        Scenario("Dedicated", 1, 4.00, 120, 55, 0.99),
        Scenario("MIG", 1, 4.00, 120, 80, 0.98),
        Scenario("Time-slicing", 1, 4.00, 120, 110, 0.90),
    ]

    results = [calculate(scenario) for scenario in scenarios]
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("GPU COST COMPARISON — ILLUSTRATIVE ASSUMPTIONS")
    print("Same hypothetical host: $4/hour, 120 hours")
    print("Throughput and success rates are assumptions, not measurements.")
    print()

    for item in results:
        print(
            f"{item['strategy']}: "
            f"${item['total_cost_usd']:.2f} total | "
            f"{item['successful_requests']:.0f} successful requests | "
            f"${item['cost_per_1000_successful_usd']:.4f} "
            "per 1,000 successful requests"
        )

    print(f"\nPASS: Results exported to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="evidence/local/05-cost-comparison.csv",
    )
    args = parser.parse_args()
    run(Path(args.output))