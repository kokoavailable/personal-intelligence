# Golden Questions Evaluation - 2026-06-19

Scope: existing `wiki/` and `public/` notes only.

Raw notes were not used. No public notes were present.

## Evaluated notes

- `wiki/topics/vmss-rolling-upgrade-health-gates.md`
- `wiki/decisions/use-golden-image-vmss-rolling-upgrade.md`
- `wiki/anti-patterns/manual-ssh-deployments-on-vmss.md`

## Results

| Question ID | Status | Evidence | Gap |
|---|---|---|---|
| infra-readiness-liveness | covered | `vmss-rolling-upgrade-health-gates` distinguishes liveness, readiness, startup, load-balancer health, Application Gateway health, and VMSS rollout health gates. | Could be stronger with a dedicated incident/postmortem example, but current wiki can answer the question. |
| opentofu-secret-state | missing | No wiki/public note covers IaC state, tfstate, sensitive variables, or secret leakage in state. | Needs compiled IaC state/security note. |
| k8s-core-model | missing | No wiki/public note covers Pod, Deployment, ReplicaSet, Service, or Ingress. | Needs Kubernetes core model note. |
| algorithm-pattern | missing | No wiki/public note covers algorithm practice patterns. | Needs algorithm pattern note. |
| backend-state-placement | missing | No wiki/public note covers backend state placement categories. | Needs backend state placement note. |
| observability-correlation | missing | VMSS note mentions rollout signals such as probe state, error rate, latency, deployment version, batch progress, and failure reason, but not metrics/logs/traces or correlation limits. | Needs observability correlation note. |
| security-identity-boundary | missing | Current wiki only mentions keeping secrets out of images; it does not explain PKI, SSH, ACME, OIDC, identity, key possession, or controllable-resource boundaries. | Needs security identity boundary note. |
| llm-vector-search | missing | No wiki/public note covers RAG, vector search, semantic search, HNSW, or hybrid retrieval. | Needs LLM retrieval note. |
| investing-thesis | missing | No wiki/public note covers investing thesis structure. | Needs investing report/thesis note. |
| paper-claim | missing | No wiki/public note covers paper claims, limitations, or applicability. | Needs paper-reading note. |
| english-expression | missing | No wiki/public note covers reusable English expressions. | Needs English expression note. |
| career-positioning | missing | No wiki/public note covers career positioning evidence. | Needs career positioning note. |
| anti-patterns | partial | `manual-ssh-deployments-on-vmss` identifies one concrete infrastructure anti-pattern. | Does not yet summarize repeated anti-patterns across recent notes. |

## Summary

Current wiki coverage is narrow and VMSS-deployment focused.

Covered: 1
Partial: 1
Missing: 11

Highest-value next compilation targets:

1. IaC state and secret leakage.
2. Kubernetes core model.
3. Observability metrics/logs/traces correlation.
