# Kubernetes GPU Configuration Reference

## Overview

This directory contains Kubernetes reference configurations for dedicated GPU allocation, NVIDIA Multi-Instance GPU (MIG), GPU time-slicing, and GPU-aware node provisioning with Karpenter.

The configurations demonstrate workload placement, resource allocation, and infrastructure scheduling controls for a hybrid GPU architecture.

## Configuration Files

| File | Purpose |
|---|---|
| `01-dedicated-gpu.yaml` | Dedicated GPU workload |
| `02-mig-gpu.yaml` | MIG-partitioned GPU workload |
| `03-time-sliced-gpu.yaml` | Shared GPU workload |
| `04-time-slicing-config.yaml` | NVIDIA device-plugin sharing configuration |
| `05-karpenter-gpu-nodepool.yaml` | AWS Karpenter GPU NodePool |

## Prerequisites

- Kubernetes cluster with compatible NVIDIA GPU nodes.
- NVIDIA GPU drivers and container runtime integration.
- NVIDIA Kubernetes Device Plugin or GPU Operator.
- Correct node labels, taints, and tolerations.
- MIG-capable hardware with configured MIG instances for MIG workloads.
- Karpenter and a compatible EC2NodeClass for AWS node provisioning.

## GPU Resource Mapping

| Strategy | Node Pool | Requested Resource |
|---|---|---|
| Dedicated | `gpu-dedicated` | `nvidia.com/gpu` |
| MIG | `gpu-mig` | `nvidia.com/mig-1g.10gb` |
| Time-Slicing | `gpu-shared` | `nvidia.com/gpu.shared` |

Resource names must match the NVIDIA Device Plugin configuration and the resources advertised by the target nodes.

The MIG resource shown is hardware-dependent and is provided as a reference example.

## Scheduling Controls

Each workload uses node selectors to target the correct GPU node pool.

Proposed node labels:

- `gpu.example.com/pool=dedicated`
- `gpu.example.com/pool=mig`
- `gpu.example.com/pool=shared`

GPU nodes use the following proposed taint:

`nvidia.com/gpu=true:NoSchedule`

Workload tolerations must match this taint.

Node selectors and tolerations determine placement eligibility, but they do not guarantee that sufficient GPU resources are available.

## GPU Sharing Configuration

The time-slicing configuration uses:

- `renameByDefault: true`
- `failRequestsGreaterThanOne: true`
- `replicas: 4`

With resource renaming enabled, the shared GPU resource is advertised as `nvidia.com/gpu.shared`.

Four replicas represent four logical shared allocations per eligible physical GPU, not four independently isolated GPUs.

Time-slicing does not provide GPU memory isolation or guaranteed proportional compute performance.

The ConfigMap must be integrated with the actual NVIDIA GPU Operator or device-plugin deployment. Creating the ConfigMap alone does not activate sharing.

## Karpenter Integration

The example Karpenter NodePool demonstrates:

- GPU-compatible AWS instance-family restrictions.
- Workload-specific node labels.
- GPU taints.
- Capacity-type selection.
- CPU capacity limits.
- Eligible node consolidation.

It requires a matching `EC2NodeClass`, properly configured Karpenter installation, and compatible AWS infrastructure.

The provided NodePool targets dedicated GPU workloads. Additional hardware-specific NodePools are required for MIG and time-slicing.

## Validation Procedure

### 1. Validate YAML Parsing

Parse the manifest files to detect YAML formatting errors.

### 2. Verify GPU Resource Advertisement

On an authorized GPU-enabled Kubernetes cluster:

```bash
kubectl get nodes
kubectl describe nodes
```

Confirm that GPU resources are advertised by the NVIDIA Device Plugin.

### 3. Inspect GPU Workloads

For a deployed workload:

```bash
kubectl get pods -o wide
kubectl describe pod gpu-dedicated-test
kubectl logs gpu-dedicated-test
```

Review scheduling events, assigned nodes, GPU allocation, and container execution results.

### 4. Verify Node Autoscaling

Inspect Karpenter resources:

```bash
kubectl get nodepools
kubectl get nodeclaims
```

Confirm provisioning behavior using pending workload events and node readiness.

## Deployment Considerations

- Apply configurations only to authorized environments.
- Verify GPU hardware compatibility before using MIG profiles.
- Confirm the correct namespace and configuration method for the installed device plugin.
- Do not apply every reference manifest indiscriminately.
- Validate the `EC2NodeClass` before creating GPU NodePools.
- Apply cloud resource limits and cost controls.
- Capture runtime evidence separately from static configuration checks.

## Validation Status

These files are reference implementations. Local YAML checks do not prove successful GPU allocation, live Pod execution, MIG configuration, or cloud node provisioning.

Runtime validation requires compatible NVIDIA GPU infrastructure.

## References

- [Kubernetes GPU Scheduling](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [NVIDIA Kubernetes Device Plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [NVIDIA GPU Sharing](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/gpu-sharing.html)
- [NVIDIA MIG Documentation](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)
- [Karpenter NodePools](https://karpenter.sh/docs/concepts/nodepools/)