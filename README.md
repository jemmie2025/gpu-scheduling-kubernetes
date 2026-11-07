# GPU Scheduling in Kubernetes

**GPU Resource Optimization | NVIDIA GPU Sharing | Kubernetes Autoscaling**

## Overview

This project evaluates GPU scheduling and resource-sharing strategies in Kubernetes, focusing on efficient GPU allocation, workload isolation, scalability, and infrastructure cost optimization.

The research compares dedicated GPU allocation, NVIDIA Multi-Instance GPU (MIG), and time-slicing to determine appropriate deployment strategies for AI inference, batch processing, and GPU-intensive workloads.

The implementation design incorporates NVIDIA's Device Plugin, GPU-aware scheduling constraints, and node autoscaling through Karpenter or Cluster Autoscaler.

## Objectives

- Evaluate Kubernetes GPU resource discovery and scheduling.
- Compare dedicated GPUs, MIG, and time-slicing.
- Develop a workload-based GPU allocation decision matrix.
- Design GPU node pools with appropriate labels, taints, and tolerations.
- Evaluate GPU-aware node autoscaling strategies.
- Model GPU capacity and infrastructure costs.
- Provide reproducible configurations and validation evidence.

## System Architecture

The proposed architecture separates GPU workloads into dedicated, MIG-enabled, and time-sliced node pools.

```text
                     AI / GPU Workloads
                             |
                     Kubernetes Scheduler
                             |
              +--------------+--------------+
              |              |              |
        Dedicated GPU      MIG GPU      Time-Sliced GPU
          Node Pool       Node Pool        Node Pool
              |              |              |
        Full GPU Access  Hardware-Based    Shared GPU
                          Partitioning     Access
              |              |              |
              +--------------+--------------+
                             |
                       GPU Hardware

Supporting Components:
- NVIDIA Device Plugin: Advertises GPU resources
- NVIDIA GPU Operator: Manages GPU software components
- Karpenter / Cluster Autoscaler: Scales GPU node capacity
```

The NVIDIA Device Plugin advertises GPU resources to Kubernetes. Node labels, selectors, taints, tolerations, and resource requests control workload placement. Node autoscalers provision compatible GPU capacity where supported and configured.

Detailed design: [System Architecture](docs/architecture.md).

## GPU Allocation Strategies

| Strategy | Isolation | Recommended Workload |
|---|---|---|
| Dedicated GPU | Exclusive device allocation | Training and large-model inference |
| NVIDIA MIG | Hardware-partitioned GPU resources | Predictable multi-tenant inference |
| Time-Slicing | Shared GPU without memory isolation | Lightweight, bursty inference |

MIG requires compatible NVIDIA hardware. Time-slicing increases access concurrency but does not guarantee proportional compute or memory capacity.

## Technology Stack

| Technology | Purpose |
|---|---|
| Kubernetes | Container orchestration and scheduling |
| NVIDIA Device Plugin | GPU resource discovery and allocation |
| NVIDIA GPU Operator | GPU software lifecycle management |
| NVIDIA MIG | Hardware GPU partitioning |
| NVIDIA Time-Slicing | Shared GPU access |
| Karpenter | Dynamic node provisioning |
| Cluster Autoscaler | Node group capacity scaling |
| Python | Cost modelling and automated validation |
| YAML | Kubernetes configuration definitions |

## Repository Structure

```text
gpu-scheduling-kubernetes/
├── configs/                    # GPU scheduling configurations
├── docs/
│   ├── architecture.md         # System architecture
│   ├── autoscaling.md          # GPU node autoscaling
│   ├── cost-model.md           # Comparative cost analysis
│   ├── decision-matrix.md      # GPU allocation evaluation
│   ├── practical-evidence.md   # Practical experiments
│   ├── references.md           # Technical references
│   └── validation.md           # Verification procedures
├── evidence/
│   ├── local/                  # Reproducible test outputs
│   └── README.md               # Evidence register
├── scripts/                    # Validation and analysis scripts
├── tests/                      # Automated tests
├── .gitignore
└── README.md
```

## Validation Strategy

Validation is organized into three categories:

1. **Static Validation:** Verify YAML syntax, GPU resource requests, scheduling constraints, and configuration consistency.
2. **Offline Experiments:** Evaluate scheduling feasibility, deliberate failure scenarios, automated tests, and cost calculations.
3. **Live-Cluster Validation:** Verify GPU Pod scheduling, resource allocation, and autoscaling behavior when authorized GPU infrastructure is available.

Offline scheduling simulations are distinguished from actual Kubernetes scheduler execution.

See [Practical Evidence](docs/practical-evidence.md) and [Validation](docs/validation.md).

## Deliverables

- GPU scheduling research and technical decision matrix.
- Kubernetes GPU scheduling architecture.
- Dedicated, MIG, and time-sliced GPU configuration examples.
- GPU-aware autoscaling design.
- Comparative cost model with documented assumptions.
- Automated validation procedures and practical evidence.
- Reproducible technical documentation.

## References

Technical decisions are based on official documentation:

- [Kubernetes — Schedule GPUs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [NVIDIA — Kubernetes Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [NVIDIA — MIG User Guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)
- [NVIDIA — GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/)
- [Karpenter Documentation](https://karpenter.sh/docs/)
- [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)

## Project Status

**In Development**

Research, configurations, cost analysis, and practical validation are being completed and committed as independently reviewable units.