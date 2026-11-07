# Unit 4 — GPU Configuration Validation

**Date:** 2026-11-07  
**Environment:** Ubuntu WSL  
**Validation Type:** Offline YAML and scheduling policy checks

## Results

| Validation | Result |
|---|---|
| Five Kubernetes YAML manifests parsed | PASS |
| Dedicated GPU scheduling policy | PASS |
| MIG GPU scheduling policy | PASS |
| Shared GPU scheduling policy | PASS |
| NVIDIA time-slicing configuration | PASS |
| Karpenter node placement configuration | PASS |

## Outcome

All five manifests passed the executed offline validation checks.

## Scope

Validation confirmed YAML parsing, selected GPU resource requests, node placement constraints, time-slicing settings, and Karpenter placement configuration.

Live GPU allocation, Kubernetes API schema validation, and actual node provisioning were not performed.