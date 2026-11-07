# GPU-Aware Node Autoscaling — Technical Design

## 1. Objective

Evaluate GPU-aware node scaling in Kubernetes using Karpenter and Cluster Autoscaler.

The objective is to provision compatible GPU node capacity for eligible pending workloads while controlling infrastructure cost, scheduling failures, and operational complexity.

## 2. Autoscaling Architecture

```text
                     GPU Workload
                          |
                          v
                  Kubernetes Scheduler
                          |
                 Sufficient Capacity?
                     /         \
                   Yes          No
                    |            |
                    v            v
                Schedule     Pending Pod
                    |            |
                    |            v
                    |      Node Autoscaler
                    |            |
                    |            v
                    |      Compatible GPU Node
                    |            |
                    |            v
                    |      Driver / Device Plugin
                    |            |
                    |            v
                    +------ GPU Ready
                                 |
                                 v
                            Schedule Pod
```

Node provisioning and GPU initialization are distinct operations.

An autoscaler may provision a node successfully even when GPU device registration subsequently fails.

## 3. Autoscaler Comparison

| Criterion | Karpenter | Cluster Autoscaler |
|---|---|---|
| Scaling model | Workload-driven provisioning | Existing node-group scaling |
| Capacity selection | Uses NodePool constraints | Uses configured node groups |
| GPU scheduling | Supports GPU resource requirements | Supports configured GPU node groups |
| Infrastructure integration | Provider-specific | Provider-specific |
| Node consolidation | Supported through disruption policies | Scale-down of eligible nodes |
| Configuration | NodePools and NodeClasses | Node groups and autoscaler configuration |
| Best fit | Flexible dynamic provisioning | Established managed node groups |

Karpenter and Cluster Autoscaler are alternatives for the same managed capacity. Avoid allowing both to independently manage the same node pool.

## 4. Karpenter Design

Karpenter evaluates pending Pod requirements and compatible NodePool definitions.

GPU NodePools should define:

- Compatible instance families and capacity types.
- GPU-specific taints.
- Node labels identifying workload pools.
- Appropriate CPU, memory, and GPU capacity.
- Resource limits and disruption policies.
- A compatible provider NodeClass.

The GPU device plugin must initialize successfully for GPU resources to become available.

## 5. Cluster Autoscaler Design

Cluster Autoscaler scales configured node groups when pending Pods cannot be scheduled using existing capacity.

GPU node-group requirements include:

- Compatible GPU instance types.
- Correct node templates and labels.
- GPU taints and matching workload tolerations.
- Configured minimum and maximum node counts.
- Appropriate infrastructure permissions.
- GPU driver and device-plugin initialization.

Cluster Autoscaler does not dynamically configure MIG partitions or time-slicing policies.

These must be established through the GPU software and node configuration.

## 6. GPU Provisioning Lifecycle

1. GPU workload requests an NVIDIA extended resource.
2. Kubernetes finds no suitable existing capacity.
3. The configured autoscaler evaluates eligible infrastructure.
4. A compatible GPU node is provisioned.
5. The node joins the Kubernetes cluster.
6. NVIDIA drivers and runtime components initialize.
7. NVIDIA Device Plugin advertises compatible resources.
8. Kubernetes schedules eligible pending workloads.

Provisioning may fail because of incompatible GPU types, capacity shortages, permissions, unsupported resource profiles, or incorrect scheduling constraints.

## 7. Scaling and Cost Controls

Recommended safeguards:

- Define node-pool or node-group capacity limits.
- Use GPU-specific labels and taints.
- Monitor unschedulable Pod events.
- Measure node startup and GPU initialization time.
- Set workload resource requirements explicitly.
- Control idle GPU capacity and unnecessary node retention.
- Review disruption policies for long-running workloads.
- Apply cloud budgets and spending alerts.

GPU-intensive training workloads may require stricter disruption controls than stateless inference services.

## 8. Validation Scenarios

| Scenario | Expected Behavior |
|---|---|
| Compatible GPU capacity available | Pod schedules without provisioning |
| GPU capacity unavailable | Pod remains Pending |
| Eligible autoscaler configured | Compatible node provisioning attempted |
| No matching node pool | Pod remains unschedulable |
| GPU device plugin unavailable | GPU resources are not advertised correctly |
| Incorrect toleration | Scheduling blocked on tainted nodes |
| Capacity limit reached | Additional nodes cannot be provisioned beyond configured limit |

These are expected behaviors, not claims of executed live-cluster tests.

## 9. Recommendation

**Preferred approach:** Evaluate Karpenter for dynamic GPU node provisioning on a supported cloud platform.

Use Cluster Autoscaler where existing managed GPU node groups or infrastructure constraints make it the more appropriate choice.

For an on-premises Kubernetes deployment, select autoscaling technology based on actual infrastructure provider support rather than assuming AWS-specific Karpenter functionality is available.

## 10. References

- [Karpenter NodePools](https://karpenter.sh/docs/concepts/nodepools/)
- [Karpenter Scheduling](https://karpenter.sh/docs/concepts/scheduling/)
- [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [Kubernetes GPU Scheduling](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [NVIDIA Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)