# GPU Cost Model — MIG vs Time-Slicing

## Objective

Evaluate the hypothetical infrastructure cost efficiency of dedicated GPU allocation, NVIDIA MIG, and time-slicing for mixed inference workloads.

## Methodology

A controlled scenario uses the same assumed GPU host price and evaluation duration across all three strategies.

Throughput and success rates are varied to demonstrate how workload consolidation affects cost per successful inference request.

No hardware performance benchmark or cloud-provider pricing measurement is claimed.

## Assumptions

| Parameter | Value |
|---|---|
| GPU host | Hypothetical MIG-capable NVIDIA host |
| Node count | 1 per scenario |
| Host cost | $4/hour |
| Evaluation period | 120 hours |
| Total cost per scenario | $480 |
| Workload | Illustrative mixed inference |
| Pricing source | Assumed, not a provider quotation |

### Workload Assumptions

| Strategy | Requests/hour | Success rate |
|---|---:|---:|
| Dedicated | 55 | 99% |
| MIG | 80 | 98% |
| Time-slicing | 110 | 90% |

The throughput and success rates are assumed inputs, not observed measurements.

## Cost Formulas

```text
Infrastructure Cost =
Node Count × Hourly Rate × Runtime Hours

Successful Requests =
Node Count × Requests per Hour × Runtime Hours × Success Rate

Cost per 1,000 Successful Requests =
Infrastructure Cost / Successful Requests × 1,000
```

## Calculated Results

| Strategy | Infrastructure Cost | Successful Requests | Cost per 1,000 |
|---|---:|---:|---:|
| Dedicated | $480 | 6,534 | $73.46 |
| MIG | $480 | 9,408 | $51.02 |
| Time-slicing | $480 | 11,880 | $40.40 |

## Interpretation

Time-slicing produces the lowest modelled cost per successful request under the selected assumptions.

This does not establish that time-slicing is the most economical production strategy.

The comparison does not account for actual inference latency, GPU memory contention, hardware partitioning overhead, workload interference, service-level objectives, or additional operational costs.

MIG may offer greater predictability and isolation, while dedicated GPUs may be necessary for workloads requiring the full device.

## Reproducibility

Run the calculation:

```bash
python3 scripts/gpu_cost_model.py
```

Run automated tests:

```bash
python3 -m unittest discover -s tests -p "test_gpu_cost_model.py" -v
```

Generated evidence:

- `evidence/local/05-cost-model.log`
- `evidence/local/05-cost-comparison.csv`
- `evidence/local/05-unit-tests.log`

## Recommendation

Use the model as a preliminary capacity-planning tool.

Before making production purchasing or scheduling decisions, replace assumed throughput, success rates, and prices with measurements from equivalent workloads on compatible GPU hardware.

Compare cost efficiency alongside latency, isolation, memory pressure, reliability, and operational complexity.