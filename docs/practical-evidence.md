# Kubernetes GPU Scheduling — Practical Evidence

## 1. Objective

Document reproducible validation procedures for dedicated GPU scheduling, MIG allocation, time-slicing, and GPU-aware node autoscaling.

The purpose is to demonstrate scheduling constraints, expected failure conditions, recovery procedures, and verification requirements.

## 2. Evidence Classification

| Category | Method | Status |
|---|---|---|
| YAML configuration validation | Python and PyYAML | Passed |
| Scheduling policy consistency | Offline configuration checks | Passed |
| Cost model execution | Python | Passed |
| Automated cost-model tests | Python unittest | 9 passed |
| Kubernetes GPU Pod execution | GPU-enabled cluster | Not tested |
| MIG hardware partitioning | Compatible NVIDIA GPU | Not tested |
| Karpenter node provisioning | Configured cloud cluster | Not tested |

Offline configuration checks are not equivalent to actual Kubernetes scheduler execution.

## 3. Scheduling Failure and Recovery Scenarios

The following scenarios define reproducible experiments for an authorized Kubernetes test cluster.

### Scenario 1 — Missing GPU Toleration

**Objective:** Verify that a GPU workload cannot schedule onto a node protected by an unmatched `NoSchedule` taint.

**Failure condition:** Remove the required GPU toleration from the Pod.

**Expected result:** The Pod remains Pending when no other eligible node exists.

**Recovery:** Restore the matching toleration.

**Verification:**

```bash
kubectl describe pod gpu-dedicated-test
kubectl get pod gpu-dedicated-test -o wide
```

Capture scheduler events before and after correcting the configuration.

### Scenario 2 — Insufficient GPU Capacity

**Objective:** Demonstrate scheduling failure when requested GPU capacity is unavailable.

**Failure condition:** Submit a workload requesting more GPU capacity than eligible nodes can provide.

**Expected result:** The Pod remains Pending unless an eligible autoscaler provisions additional capacity.

**Recovery:** Reduce demand or make compatible GPU capacity available.

**Verification:**

```bash
kubectl describe pod gpu-dedicated-test
kubectl describe nodes
```

Record advertised GPU capacity, allocatable resources, and scheduling events.

### Scenario 3 — Incorrect GPU Node Selector

**Objective:** Verify workload placement restrictions.

**Failure condition:** Configure a node selector that matches no eligible GPU node.

**Expected result:** The Pod remains Pending.

**Recovery:** Correct the selector to match the intended GPU node pool.

**Verification:**

```bash
kubectl get nodes --show-labels
kubectl describe pod gpu-dedicated-test
```

### Scenario 4 — Unsupported MIG Resource

**Objective:** Verify that MIG workloads require compatible hardware and advertised MIG capacity.

**Failure condition:** Request a MIG profile that is not advertised by the target nodes.

**Expected result:** No eligible GPU allocation is available.

**Recovery:** Configure a supported MIG profile or select a compatible node.

**Verification:**

```bash
kubectl describe nodes
kubectl describe pod gpu-mig-test
```

### Scenario 5 — Time-Slicing Resource Mismatch

**Objective:** Verify consistency between shared GPU workload requests and the NVIDIA Device Plugin configuration.

**Failure condition:** Request `nvidia.com/gpu.shared` on a node that does not advertise this resource.

**Expected result:** The Pod cannot be scheduled using that resource.

**Recovery:** Ensure time-slicing is activated on the intended node and verify resource advertisement.

**Verification:**

```bash
kubectl describe nodes
kubectl describe pod gpu-shared-test
```

### Scenario 6 — GPU-Aware Autoscaling

**Objective:** Verify compatible GPU node provisioning for eligible pending workloads.

**Prerequisites:**

- Authorized Kubernetes cluster.
- Installed and configured Karpenter.
- Compatible GPU instance types.
- Valid EC2NodeClass and NodePool.
- Appropriate permissions and spending controls.

**Expected workflow:**

1. A GPU Pod remains Pending due to insufficient compatible capacity.
2. Karpenter evaluates its scheduling requirements.
3. An eligible GPU node is provisioned.
4. NVIDIA GPU software initializes.
5. The device plugin advertises GPU resources.
6. Kubernetes schedules the workload.

**Verification:**

```bash
kubectl get nodepools
kubectl get nodeclaims
kubectl get nodes
kubectl get pods -o wide
```

## 4. Current Practical Results

### GPU Configuration Validation

Five manifests passed offline YAML parsing and selected scheduling-policy consistency checks.

Evidence: [Configuration Validation](../evidence/local/04-configuration-validation.md).

### Cost Model Execution

The reproducible Python model generated the scenario comparison.

Evidence:

- [Cost Model Log](../evidence/local/05-cost-model.log)
- [Cost Comparison CSV](../evidence/local/05-cost-comparison.csv)

### Automated Tests

Nine Python cost-model tests passed.

Evidence: [Unit Test Log](../evidence/local/05-unit-tests.log).

## 5. Acceptance Criteria

| Criterion | Evidence Requirement |
|---|---|
| Correct GPU resource requests | Manifest validation |
| Consistent node placement policies | Selector and toleration checks |
| Time-slicing configuration consistency | ConfigMap validation |
| Reproducible cost calculations | Python execution and CSV |
| Automated calculation correctness | Unit test output |
| Actual GPU scheduling | Live Pod events and execution logs |
| Actual GPU autoscaling | Node provisioning and readiness records |

## 6. Conclusion

The completed local validation demonstrates reproducible configuration checks and cost-model execution.

The failure-and-recovery scenarios provide a practical verification plan for deployment on authorized GPU infrastructure.

Live GPU scheduling, MIG partitioning, time-slicing performance, and node autoscaling remain unverified and are not presented as completed experiments.