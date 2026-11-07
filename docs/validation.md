# Kubernetes GPU Scheduling — Validation Report

## 1. Purpose

This report documents the validation of the Kubernetes GPU scheduling reference configurations and GPU cost model.

The objective is to establish reproducible evidence of configuration consistency, scheduling-policy correctness, and calculation accuracy.

## 2. Test Environment

| Component | Environment |
|---|---|
| Operating system | Ubuntu on Windows Subsystem for Linux |
| Configuration format | Kubernetes YAML |
| Validation tooling | Python and PyYAML |
| Automated testing | Python unittest |
| Infrastructure | Local development environment |
| GPU hardware | Not required for offline validation |

## 3. Validation Summary

| ID | Validation | Result |
|---|---|---|
| VAL-01 | Five Kubernetes manifests parsed | PASS |
| VAL-02 | Dedicated GPU scheduling policy | PASS |
| VAL-03 | MIG GPU scheduling policy | PASS |
| VAL-04 | Time-sliced GPU scheduling policy | PASS |
| VAL-05 | NVIDIA time-slicing settings | PASS |
| VAL-06 | Karpenter node placement policy | PASS |
| VAL-07 | Cost model execution and CSV export | PASS |
| VAL-08 | Nine automated Python unit tests | PASS |

## 4. Configuration Validation

Five Kubernetes manifests were evaluated:

1. `configs/01-dedicated-gpu.yaml`
2. `configs/02-mig-gpu.yaml`
3. `configs/03-time-sliced-gpu.yaml`
4. `configs/04-time-slicing-config.yaml`
5. `configs/05-karpenter-gpu-nodepool.yaml`

The offline checks verified:

- YAML parsing and required metadata.
- GPU resource requests and limits.
- Workload node selectors.
- GPU taints and tolerations.
- NVIDIA time-slicing configuration.
- Karpenter node placement constraints.

All five manifests passed the executed checks.

## 5. Cost Model Verification

The Python cost model was executed successfully using documented hypothetical inputs.

| Strategy | Total Cost | Successful Requests | Cost per 1,000 |
|---|---:|---:|---:|
| Dedicated | $480 | 6,534 | $73.46 |
| MIG | $480 | 9,408 | $51.02 |
| Time-slicing | $480 | 11,880 | $40.40 |

The model generated a CSV report and terminal execution log.

The values are illustrative and do not represent provider pricing quotations or GPU performance benchmarks.

## 6. Automated Tests

Nine Python unit tests passed, covering:

- Dedicated GPU cost calculations.
- MIG and time-slicing calculations.
- Multiple-node cost calculations.
- Invalid node count.
- Invalid pricing.
- Invalid runtime.
- Invalid throughput.
- Invalid success-rate inputs.

Test evidence: [Automated Test Log](../evidence/local/05-unit-tests.log).

## 7. Evidence References

| Evidence | Location |
|---|---|
| Configuration validation | [Validation Record](../evidence/local/04-configuration-validation.md) |
| Cost model output | [Execution Log](../evidence/local/05-cost-model.log) |
| Cost comparison | [CSV Results](../evidence/local/05-cost-comparison.csv) |
| Automated tests | [Test Log](../evidence/local/05-unit-tests.log) |

## 8. Verification Boundaries

The completed checks establish offline configuration consistency and cost calculation correctness within the tested cases.

The following require a compatible GPU-enabled Kubernetes environment for verification:

- Physical GPU allocation.
- MIG partition initialization.
- Runtime GPU time-slicing behavior.
- Kubernetes scheduler events.
- Karpenter node provisioning.
- GPU performance, utilization, and latency measurements.

No live hardware-dependent results are claimed.

## 9. Conclusion

The reference configurations passed the executed offline checks, and the reproducible cost model passed its automated tests.

The evidence supports the project's configuration and analytical design while distinguishing verified results from proposed infrastructure behavior.