# Pre-Workshop Discovery Questionnaire

Fill this out before every workshop. The answers determine which modules to run and which demos are worth setting up. A 20-minute call with the prospect's technical lead is enough to get through most of this.

---

## 1. Application Stack

| Question | Answer |
|----------|--------|
| Primary languages/runtimes in use? | |
| Key frameworks (Flask, Spring Boot, Express, etc.)? | |
| Current base images (e.g., `python:3.12`, `node:20-alpine`, `ubuntu:22.04`)? | |
| Image sources — Docker Hub, Quay, internal registry, vendor images? | |
| Any custom base image layers maintained by the platform team? | |

**Notes:**

---

## 2. Container Registry

| Question | Answer |
|----------|--------|
| Primary registry (ECR, GCR/Artifact Registry, ACR, Docker Hub, Harbor, JFrog)? | |
| Is the registry private or public-facing? | |
| How do workloads authenticate to pull images (IRSA, Workload Identity, service accounts, tokens)? | |
| Is there a pull-through or mirror cache in place? | |
| Any restrictions on pulling from external registries? | |

**Notes:**

---

## 3. CI/CD Platform

| Question | Answer |
|----------|--------|
| CI/CD system (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, CircleCI, Tekton)? | |
| Are image builds centralized (platform team owns Dockerfiles) or per-team? | |
| How are images promoted across environments (tags, digest pinning, CD tooling)? | |
| Do pipelines currently sign or attest images? | |
| Any GitOps layer (ArgoCD, Flux) in the deploy path? | |

**Notes:**

---

## 4. Security & Compliance Tools

| Question | Answer |
|----------|--------|
| Container image scanner in use (Wiz, Prisma Cloud, Trivy, Snyk, Grype, Anchore, Qualys)? | |
| Is scanning in-pipeline, admission controller, or periodic? | |
| What CVE severity levels block deployments today? | |
| Are SBOMs required (by internal policy, customer contract, or regulation)? | |
| Relevant compliance frameworks (SOC 2, FedRAMP, PCI-DSS, HIPAA, ISO 27001)? | |
| Does a security team own image approval, or do dev teams self-serve? | |

**Notes:**

---

## 5. Current Pain Points

| Question | Answer |
|----------|--------|
| How are CVEs in base images handled today (manual patching, rebuild on schedule, ignored)? | |
| What is the patching SLA for critical CVEs? | |
| How long does it typically take to remediate a critical CVE in a base image? | |
| Is CVE noise (false positives, CVEs with no fix available) a problem? | |
| Any recent audit findings or compliance failures related to container images? | |
| Are dev teams blocked by security findings they can't fix themselves? | |

**Notes:**

---

## 6. Desired Outcomes

Check all that apply and add context:

- [ ] Reduce CVE count in production images
- [ ] Pass an upcoming compliance audit
- [ ] Accelerate patching — reduce time from disclosure to deploy
- [ ] Eliminate manual base image maintenance
- [ ] Produce SBOMs for customer or regulatory requirements
- [ ] Reduce attack surface (remove shell, package managers, etc.)
- [ ] Standardize base images across teams
- [ ] Speed up CI scan gates (fewer findings = faster pipelines)

**Primary outcome they care most about:**

**Secondary outcome:**

---

## 7. Pilot Candidate

| Question | Answer |
|----------|--------|
| Which application or service would they migrate first? | |
| What language/runtime does it use? | |
| Who owns that service (team name, point of contact)? | |
| Is there a timeline or deadline driving this (audit, contract, incident)? | |
| What would "success" look like for a pilot? | |

**Notes:**

---

## Module Selection Guide

Use the answers above to pick modules. This is a guide, not a strict rule.

| Condition | Include |
|-----------|---------|
| Any audience, first touch | Module 01 (always) |
| They use a scanner and care about CVE counts | Module 02 |
| Compliance requirement, audit coming up, SBOMs mentioned | Module 03 |
| Python shop, libraries or dependencies mentioned as pain | Module 04 |
| Platform team owns image builds, "custom base image" mentioned, wants to version image config | Module 05 |
| CI/CD is the buying motion, pipeline integration matters, nonroot or registry migration questions | Module 06 |
| Security team needs to approve new images | Module 03 (lead with attestation and SBOM story) |
| Short on time (< 60 min), executive in the room | Modules 01 + 02 only |
| Full hands-on lab, all-day session | All modules, 01 → 06 |
