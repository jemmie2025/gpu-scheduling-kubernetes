# GPU Scheduling in Kubernetes — Technical Decision Matrix

## 1. Executive Summary

This document evaluates three GPU allocation strategies for Kubernetes: dedicated GPU allocation, NVIDIA Multi-Instance GPU (MIG), and GPU time-slicing.

The objective is to select appropriate scheduling strategies for AI inference, training, and multi-tenant workloads based on resource isolation, performance predictability, scalability, operational complexity, and cost.

**Architecture Decision:** Adopt a hybrid GPU scheduling model that separates workloads into dedicated, MIG-enabled, and time-sliced GPU node pools.

## 2. Kubernetes GPU Scheduling Fundamentals

Kubernetes manages NVIDIA GPU resources through the NVIDIA Device Plugin, which advertises available accelerators as extended resources.

Common resource names include:

- `nvidia.com/gpu`: Physical GPUs or configured shared GPU resources.
- `nvidia.com/mig-1g.10gb`: An example MIG resource available on compatible GPUs using an appropriate device-plugin configuration.

GPU workloads are scheduled according to:

- GPU resource limits and requests.
- Node selectors and node affinity.
- Taints and tolerations.
- Device-plugin-advertised resource availability.
- Node capacity and workload constraints.

Kubernetes does not ordinarily support fractional requests for GPU extended resources. GPU sharing requires supported device-plugin configuration.

## 3. GPU Allocation Comparison

| Criterion | Dedicated GPU | NVIDIA MIG | Time-Slicing |
|---|---|---|---|
| Allocation | Exclusive physical GPU | Hardware GPU partition | Shared GPU access |
| Hardware | Supported NVIDIA GPU | MIG-capable GPU | Supported NVIDIA GPU |
| Memory isolation | Exclusive allocation | Hardware partitioning | None between replicas |
| Compute isolation | Exclusive allocation | Partitioned compute | No guaranteed fraction |
| Performance predictability | High | High within profile limits | Workload-dependent |
| Concurrent allocations | One per physical GPU | Multiple compatible MIG instances | Configured shared replicas |
| Operational complexity | Low–medium | High | Medium |
| Main advantage | Predictable performance | Isolation and consolidation | Increased access concurrency |
| Main limitation | Potential underutilization | Hardware compatibility | Resource contention |

**Key distinction:** MIG provides hardware partitioning on supported NVIDIA devices. Time-slicing increases sharing concurrency without providing equivalent memory isolation or guaranteed compute capacity.

## 4. Workload Decision Matrix

| Workload | Preferred Strategy | Engineering Justification |
|---|---|---|
| Large-model inference | Dedicated GPU | Full GPU memory and predictable execution |
| GPU training | Dedicated GPU | Exclusive resources and reduced interference |
| Multi-tenant inference | MIG | Hardware-partitioned memory and compute |
| Lightweight inference | Time-slicing | Supports intermittent concurrent access |
| Development and testing | Time-slicing | Efficient sharing where contention is acceptable |
| Isolation-sensitive inference | MIG or dedicated | Stronger workload separation |
| Unknown workload profile | Dedicated initially | Establish a performance baseline before sharing |

Recommendations depend on GPU compatibility, workload memory requirements, concurrency, and measured performance.

## 5. Dedicated GPU Allocation

Dedicated GPU allocation assigns exclusive device access to a workload.

### Advantages

- Predictable device availability.
- Full physical GPU memory access.
- Straightforward scheduling and troubleshooting.
- Suitable for high-performance workloads.

### Limitations

- Potentially low utilization during idle periods.
- Higher cost per workload when capacity is underused.
- Limited allocation concurrency.

**Recommendation:** Use dedicated GPUs for large-model inference, training, and performance-sensitive workloads.

## 6. NVIDIA Multi-Instance GPU (MIG)

MIG partitions compatible NVIDIA GPUs into independently allocatable GPU instances with hardware-separated compute and memory resources.

### Advantages

- Hardware-level partitioning.
- Stronger workload isolation.
- Predictable resource allocation within profile limits.
- Consolidation of smaller inference workloads.

### Limitations

- Requires MIG-compatible hardware.
- Available profiles depend on the GPU model.
- Partition management increases operational complexity.
- Workloads must fit within their assigned MIG profiles.

### Kubernetes Integration

With the NVIDIA Device Plugin configured for a `mixed` MIG strategy, supported profiles may be advertised using distinct resource names.

For example:

```yaml
resources:
  limits:
    nvidia.com/mig-1g.10gb: 1
```

The exact profile must be supported by the GPU and advertised by the node.

**Recommendation:** Use MIG for multi-tenant inference requiring predictable resource partitioning.

## 7. NVIDIA GPU Time-Slicing

Time-slicing enables multiple workloads to share GPU execution by exposing configured shared resource replicas.

### Advantages

- Supports concurrent GPU access.
- Useful for intermittent workloads.
- Can increase utilization of underused GPUs.
- Does not require MIG-capable hardware.

### Limitations

- No GPU memory isolation between replicas.
- No guaranteed proportional compute allocation.
- Workloads compete for device memory and execution time.
- Increased concurrency may degrade latency and throughput.
- Advertised replicas do not represent additional physical GPU capacity.

### Example Sharing Configuration

```yaml
version: v1
sharing:
  timeSlicing:
    renameByDefault: false
    failRequestsGreaterThanOne: true
    resources:
      - name: nvidia.com/gpu
        replicas: 4
```

This example configures four shared allocations per eligible GPU. It does not create four physical GPUs or guarantee one-quarter of GPU performance per workload.

**Recommendation:** Use time-slicing for lightweight, bursty workloads that tolerate variable performance and shared memory.

## 8. GPU Node Pool Architecture

Separate workloads into three logical GPU pools:

| Node Pool | Strategy | Intended Workload |
|---|---|---|
| `gpu-dedicated` | Exclusive GPU allocation | Training and large inference |
| `gpu-mig` | MIG hardware partitioning | Multi-tenant inference |
| `gpu-shared` | Time-slicing | Lightweight inference and development |

Each pool should use:

- Explicit node labels.
- GPU-specific taints.
- Matching workload tolerations.
- Correct GPU extended-resource requests.
- Hardware-compatible provisioning constraints.

Workload placement requires both compatible node constraints and sufficient advertised GPU resources.

## 9. GPU-Aware Node Autoscaling

GPU-aware autoscaling adjusts infrastructure capacity when eligible pending Pods require additional GPU resources.

### Karpenter

Karpenter provisions nodes using pending Pod requirements and configured NodePool constraints.

Capabilities include:

- Workload-driven provisioning.
- Compatible instance-type selection.
- NodePool scheduling constraints.
- Eligible node consolidation.

### Cluster Autoscaler

Cluster Autoscaler adjusts the size of configured node groups.

Capabilities include:

- Scaling eligible node groups for unschedulable Pods.
- Enforcing configured minimum and maximum capacity.
- Using node-group templates for placement simulation.
- Integration with supported cloud providers.

### Operational Requirements

Successful GPU node provisioning requires:

1. Compatible NVIDIA GPU hardware.
2. Proper NVIDIA driver configuration.
3. Container runtime integration.
4. An operational NVIDIA Device Plugin.
5. Correct GPU resource registration.
6. Compatible workload placement constraints.

Provisioning a GPU node does not automatically guarantee that its GPU resources are ready.

## 10. Cost and Utilization Evaluation

GPU cost efficiency must be assessed using comparable workloads.

| Metric | Evaluation Purpose |
|---|---|
| Node cost per hour | Infrastructure expenditure |
| GPU utilization | Device activity |
| GPU memory consumption | Memory pressure |
| Inference throughput | Completed requests per second |
| Request latency | Response performance |
| Successful workloads | Delivered processing capacity |
| Idle node hours | Unused infrastructure |
| Autoscaling delay | Time required to add capacity |

### Cost Efficiency Formula

```text
Cost per successful request =
Total infrastructure cost / Successful requests
```

A lower node-hour cost does not necessarily indicate a lower cost per completed request.

MIG and time-slicing must be compared under equivalent workloads, documented assumptions, and measurable performance requirements.

## 11. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| GPU memory exhaustion | Profile memory demand and control concurrency |
| Shared GPU contention | Benchmark latency and throughput |
| Unsupported MIG hardware | Verify GPU model compatibility |
| Incorrect workload placement | Validate selectors, taints, and tolerations |
| Autoscaling failures | Verify capacity configuration and GPU initialization |
| Resource naming mismatch | Check advertised NVIDIA resource names |
| Unexpected infrastructure cost | Apply budgets and node capacity limits |

## 12. Architecture Decision Record

**Decision ID:** ADR-001
**Status:** Proposed
**Decision:** Hybrid GPU Scheduling Architecture

### Decision

Use dedicated GPUs for performance-sensitive workloads, MIG for hardware-isolated inference on supported GPUs, and time-slicing for lightweight workloads tolerant of shared execution.

Integrate GPU-aware node autoscaling to manage compatible node capacity.

### Rationale

A hybrid model allows scheduling decisions to reflect workload characteristics rather than applying a single GPU-sharing mechanism across all applications.

### Consequences

- Improved flexibility in GPU allocation.
- Stronger isolation options for sensitive workloads.
- Greater operational complexity due to multiple GPU configurations.
- Need for workload profiling, capacity monitoring, and configuration validation.

## 13. Validation and Acceptance Criteria

The design will be evaluated using:

- Kubernetes YAML syntax validation.
- GPU resource-request verification.
- Node label, selector, taint, and toleration consistency checks.
- Deliberate scheduling failure scenarios.
- Automated configuration tests.
- Reproducible cost calculations.
- Live GPU scheduling and autoscaling tests where authorized infrastructure is available.

Offline scheduling feasibility tests must not be represented as actual Kubernetes scheduler execution.

## 14. Technical References

- [Kubernetes — Schedule GPUs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [NVIDIA — Kubernetes Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [NVIDIA — MIG User Guide](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)
- [NVIDIA — Supported MIG GPUs](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html)
- [NVIDIA — GPU Sharing](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-sharing.html)
- [Karpenter Documentation](https://karpenter.sh/docs/)
- [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)

## 15. Conclusion

No single GPU scheduling strategy is optimal for every Kubernetes workload.

Dedicated GPUs prioritize exclusive resource access, NVIDIA MIG enables hardware partitioning on compatible devices, and time-slicing increases concurrent access without equivalent isolation.

A hybrid architecture provides a practical foundation for balancing performance, workload isolation, infrastructure utilization, and operational cost.
