# GPU Scheduling in Kubernetes

**Advanced DevOps | NVIDIA GPU Sharing | GPU-Aware Autoscaling**

## Overview

A technical evaluation of GPU scheduling and resource sharing in Kubernetes, comparing dedicated GPU allocation, NVIDIA Multi-Instance GPU (MIG), and time-slicing for mixed AI workloads.

The project delivers a workload-based decision matrix, hybrid scheduling architecture, Kubernetes reference configurations, and reproducible cost analysis.

## System Architecture

```text
             AI / GPU Workloads
                     |
             Kubernetes Scheduler
                     |
       +-------------+-------------+
       |             |             |
   Dedicated GPU    MIG GPU     Shared GPU
       Pool          Pool         Pool
       |             |             |
   Full Device    Hardware     Time-Slicing
   Allocation     Partitions   Shared Access
       |             |             |
       +-------------+-------------+
                     |
                NVIDIA GPUs

Supporting: NVIDIA Device Plugin, GPU Operator,
            Karpenter / Cluster Autoscaler
```

GPU resource requests, node selectors, taints, and tolerations determine workload placement. GPU-aware autoscaling manages compatible node capacity.

[Architecture](docs/architecture.md) | [Autoscaling](docs/autoscaling.md)

## Technical Implementation

| Strategy | Intended Workload | Resource |
|---|---|---|
| Dedicated GPU | Training and large-model inference | `nvidia.com/gpu` |
| MIG | Partitioned multi-tenant inference | `nvidia.com/mig-1g.10gb` |
| Time-slicing | Lightweight shared inference | `nvidia.com/gpu.shared` |

Five Kubernetes YAML reference configurations cover GPU workloads, NVIDIA sharing, and Karpenter node provisioning.

[Configuration Guide](configs/README.md) | [Decision Matrix](docs/decision-matrix.md)

## Verified Results

| Validation | Result |
|---|---|
| Kubernetes YAML parsing and policy checks | 5 manifests passed |
| Automated Python unit tests | 9 passed |
| Cost-model execution and CSV export | Passed |

### Illustrative Cost Comparison

| Strategy | 120-hour Cost | Cost / 1,000 Successful Requests |
|---|---:|---:|
| Dedicated | $480 | $73.46 |
| MIG | $480 | $51.02 |
| Time-slicing | $480 | $40.40 |

Cost inputs and throughput assumptions are hypothetical, not measured GPU benchmarks.

[Cost Analysis](docs/cost-model.md) | [Validation Report](docs/validation.md)

## Practical Evidence


[Evidence Register](evidence/README.md) | [Practical Verification Guide](docs/practical-evidence.md)

## Repository Structure

```text
gpu-scheduling-kubernetes/
├── configs/          # Five Kubernetes manifests and guide
├── docs/             # Research, architecture, cost and validation
├── evidence/
│   ├── local/        # Execution logs and CSV results
│   └── README.md
├── scripts/          # Python GPU cost model
├── tests/            # Automated unit tests
├── .gitignore
└── README.md
```

## Reproduction

```bash
python3 scripts/gpu_cost_model.py
python3 -m unittest discover -s tests -v
```

The cost model and tests run locally with Python 3. GPU hardware is not required.

## Engineering Conclusion

A hybrid approach is recommended: dedicated GPUs for performance-sensitive workloads, MIG for hardware-isolated partitioning on compatible GPUs, and time-slicing for workloads tolerant of shared execution.

**Validation scope:** Offline configuration checks and cost-model tests completed. Live GPU scheduling, MIG deployment, and autoscaling require compatible infrastructure.
