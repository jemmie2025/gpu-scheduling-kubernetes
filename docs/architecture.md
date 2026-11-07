# Kubernetes GPU Scheduling — System Architecture

## 1. Architecture Overview

This architecture defines a hybrid GPU scheduling model for Kubernetes, supporting dedicated GPU allocation, NVIDIA Multi-Instance GPU (MIG), and time-slicing.

The design separates workloads by GPU memory requirements, resource isolation, performance sensitivity, and sharing tolerance.

**Architecture status:** Proposed reference design. Production deployment and GPU hardware validation are not claimed.

## 2. Architecture Diagram

```text
                   AI / GPU Applications
                  Inference | Training | Batch
                             |
                             v
                    Kubernetes API Server
                             |
                             v
                     Kubernetes Scheduler
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
       Dedicated Pool     MIG Pool       Shared Pool
       gpu-dedicated      gpu-mig        gpu-shared
             |               |               |
        Full GPU         MIG Instances     Time-Slicing
        Allocation       Hardware Slices   Shared Replicas
             |               |               |
             +---------------+---------------+
                             |
                    NVIDIA GPU Hardware

        GPU Resource Advertisement:
        NVIDIA Device Plugin on GPU Nodes

        Node Capacity Management:
        Karpenter OR Cluster Autoscaler

        Observability:
        GPU Metrics | Pod Events | Node Readiness
```

The Kubernetes scheduler selects eligible nodes according to scheduling constraints and advertised GPU capacity.

The NVIDIA Device Plugin exposes allocatable GPU resources on each compatible node.

Node autoscaling operates separately from GPU resource allocation and requests infrastructure capacity when eligible Pods cannot be scheduled.

## 3. Logical Components

| Component | Responsibility |
|---|---|
| Kubernetes API Server | Stores workload and scheduling configuration |
| Kubernetes Scheduler | Assigns eligible Pods to available nodes |
| NVIDIA Device Plugin | Advertises GPU extended resources |
| GPU Operator | Manages supported NVIDIA GPU software components |
| Dedicated GPU Pool | Provides exclusive physical GPU allocations |
| MIG GPU Pool | Provides hardware-partitioned GPU instances |
| Shared GPU Pool | Provides time-sliced GPU allocations |
| Karpenter / Cluster Autoscaler | Adjusts eligible node capacity |
| Monitoring | Tracks GPU health, utilization, and scheduling behavior |

## 4. GPU Node Pool Design

| Node Pool | GPU Mode | Resource Example | Workloads |
|---|---|---|---|
| gpu-dedicated | Full GPU | nvidia.com/gpu | Training and large-model inference |
| gpu-mig | MIG mixed strategy | nvidia.com/mig-1g.10gb | Multi-tenant inference |
| gpu-shared | Time-slicing | nvidia.com/gpu | Lightweight inference |

The MIG resource is illustrative. Actual profile names depend on the GPU model and partition configuration.

Each pool requires compatible hardware, driver configuration, device-plugin settings, and Kubernetes scheduling policies.

## 5. Node Placement Policy

Proposed node labels:

- `gpu.example.com/pool=dedicated`
- `gpu.example.com/pool=mig`
- `gpu.example.com/pool=shared`

Proposed node taint:

`nvidia.com/gpu=true:NoSchedule`

GPU workloads must tolerate the GPU taint and select the appropriate pool.

Resource requests must match the resources actually advertised by the device plugin.

Node labels alone do not guarantee resource availability.

## 6. Scheduling Workflow

1. A GPU workload is submitted to the Kubernetes API Server.
2. Kubernetes evaluates its resource requests and placement constraints.
3. The scheduler searches for compatible nodes with sufficient advertised GPU resources.
4. If capacity exists, Kubernetes binds the Pod to an eligible node.
5. The NVIDIA Device Plugin participates in device allocation and container startup.
6. If compatible capacity is unavailable, the Pod may remain Pending.
7. A configured node autoscaler can respond by provisioning eligible capacity.
8. The new node must initialize its GPU software and advertise resources.
9. Kubernetes retries scheduling the pending workload.

A Pod may remain unschedulable if resource requirements, taints, labels, infrastructure availability, or provisioner constraints cannot be satisfied.

## 7. GPU Isolation Model

### Dedicated GPUs

Provide exclusive physical device allocation.

Suitable for training, high-memory inference, and performance-sensitive workloads.

### NVIDIA MIG

Provides hardware-partitioned GPU instances on compatible devices.

Suitable for workloads requiring stronger memory and compute isolation.

### NVIDIA Time-Slicing

Allows multiple allocations to share access to compatible GPUs.

Time-slicing does not provide independent GPU memory isolation or guaranteed proportional compute performance.

## 8. Operational Safeguards

- Restrict GPU access using taints and tolerations.
- Apply explicit workload placement labels.
- Validate resource names against actual node capacity.
- Monitor GPU utilization, memory pressure, and Pod failures.
- Establish node capacity and cloud spending limits.
- Verify GPU driver and device-plugin readiness.
- Use workload benchmarks before selecting sharing levels.
- Avoid exposing infrastructure credentials in the repository.

## 9. Failure Scenarios

| Failure | Expected Effect | Mitigation |
|---|---|---|
| Missing toleration | Pod cannot use tainted GPU node | Add correct toleration |
| Incorrect node selector | No eligible matching node | Correct pool selection |
| Insufficient GPU capacity | Pod remains Pending | Free capacity or provision compatible node |
| Device plugin unavailable | GPU resources not advertised correctly | Restore plugin and verify node capacity |
| Unsupported MIG profile | Requested resource unavailable | Select supported partition profile |
| Excessive time-slicing contention | Latency or workload failures | Reduce concurrency or change strategy |
| Autoscaler constraints mismatch | New eligible node cannot be provisioned | Correct node-pool requirements |

## 10. Architecture Decision

**Decision:** Use workload-specific GPU pools with a hybrid allocation strategy.

**Rationale:** Dedicated allocation prioritizes predictable performance, MIG supports hardware partitioning, and time-slicing improves concurrent access for suitable workloads.

**Trade-off:** Multiple GPU pools increase configuration and operational complexity.

**Validation requirement:** Confirm scheduling policies, GPU resource advertisement, capacity provisioning, and actual workload performance before production adoption.

## 11. References

- [Kubernetes GPU Scheduling](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [NVIDIA Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [NVIDIA MIG Documentation](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)
- [Karpenter Scheduling](https://karpenter.sh/docs/concepts/scheduling/)