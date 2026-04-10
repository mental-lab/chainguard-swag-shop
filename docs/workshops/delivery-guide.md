# Workshop Delivery Guide

SA best practices for running Chainguard workshops. This assumes you know containers. The focus here is Chainguard-specific mechanics, pacing, and the conversations that come up repeatedly.

---

## Pre-Workshop Checklist

Complete these before the session starts. Don't wing the demos.

- [ ] Discovery questionnaire filled out — you know which modules you're running
- [ ] Chainguard console loaded and authenticated in your browser (`console.chainguard.dev`)
- [ ] `chainctl` installed and authenticated locally (`chainctl auth login`)
- [ ] Demo images pulled and available locally (don't rely on network speed during a live session)
- [ ] Grype installed and DB is fresh (`grype db update`)
- [ ] Dockerfiles from the prospect in hand — ideally their actual Dockerfile, not a generic example
- [ ] Cosign installed for attestation demos (`cosign version`)
- [ ] If running Module 05: `build.yaml` ready, Chainguard org with Custom Assembly entitlement confirmed
- [ ] If running Module 04: `.netrc` configured for `libraries.cgr.dev`, `make switch-cgr` tested
- [ ] Fallback screenshots ready for any live step that might fail
- [ ] Know the prospect's current base image — have a Grype scan of it ready to show before the Chainguard comparison

---

## Timing Tips

**Per-module estimates** (these assume a reasonably interactive room):

| Module | Estimated Time | Notes |
|--------|---------------|-------|
| 01 — Distroless Fundamentals | 20 min | Runs short if the audience already knows distroless. Skip the "what is a container layer" basics. |
| 02 — CVE Comparison | 20–30 min | Runs long when the audience wants to debate specific CVEs. Time-box CVE discussion to 5 min. |
| 03 — SBOMs, Provenance, Attestations | 25–35 min | Compliance-heavy audiences will go deep here. Have a "fast path" version that skips cosign CLI details. |
| 04 — Libraries (Remediated PyPI) | 20 min | Fast if you have the demo prepped. Slow if you're installing live. Pre-run `make switch-cgr`. |
| 05 — Custom Assembly | 30–40 min | Allow 40 min if they want to submit their own `build.yaml`. 30 if you're showing yours. |
| 06 — CI/CD Integration | 25–35 min | Digest pinning walkthrough eats time. Have the digestabot PR already open as an example. |

**Where to cut if you're short on time:**

- Module 02: Show one scan result (not both registries). State the numbers, skip the live comparison.
- Module 03: Skip the `cosign verify` CLI walkthrough. Show the console UI attestation view instead.
- Module 05: Skip submitting a new build — show the existing CI run and evidence bundle artifact.
- Module 06: Skip the GitOps section if they're not using ArgoCD/Flux.

**Where audiences linger:**

- CVE debates in Module 02 — have a response ready (see Objections below)
- "How does Chainguard update images" question in Module 01 — be precise: upstream tracking, nightly rebuilds, Wolfi packages
- Signing and verification details in Module 03 — most audiences don't need to run `cosign` themselves; focus on the policy/audit value

---

## Common Objections and Responses

### "We already use Alpine / Distroless"

**Response:**

Alpine has a smaller footprint than debian-based images but still ships a musl libc, busybox, and a package manager in the runtime image — all of which are CVE surface. Standard distroless images (from Google) ship no CVEs at build time but are rebuilt infrequently and carry unpatched CVEs days or weeks after disclosure.

Chainguard images are rebuilt daily, tracking upstream continuously, with zero CVEs at build time verified. Show the Grype comparison: `python:3.12-alpine` vs `cgr.dev/chainguard/python:latest`. Let the scanner results do the talking.

If they're on Distroless specifically: point out that Google's distroless doesn't provide SBOMs, signatures, or attestations by default, and rebuilds on no fixed cadence.

### "Our security team needs to approve new base images"

**Response:**

That approval process is exactly what SBOMs and attestations are designed to support. Every Chainguard image ships with:
- A signed SBOM (CycloneDX and SPDX) you can feed into your scanner or ITSM
- A SLSA provenance attestation showing the build inputs and build system
- A Cosign signature verifiable against Chainguard's public key without trusting Chainguard's infrastructure at verify time

Point them to Module 03 demo: `cosign verify-attestation --type sbom cgr.dev/chainguard/python:latest`. Security teams can write policy (OPA, Kyverno, Sigstore policy-controller) that enforces these attestations exist before a pod is admitted.

If they have a formal change management process: the evidence bundle from Custom Assembly (build.yaml + Grype results + SBOM + provenance) is designed to go into a change ticket.

### "We're locked into Docker Hub / we can't change registries"

**Response:**

Chainguard images are available on `cgr.dev`. You don't have to migrate everything at once. Two common patterns:

1. **Pull-through / mirror**: Configure ECR, Artifact Registry, or Harbor to pull-through from `cgr.dev`. Your workloads keep pulling from your internal registry URL. One-time registry config change, no Dockerfile or deployment changes.
2. **Selective migration**: Start with the pilot service from the questionnaire. One `FROM` line change. Measure the CVE delta. Expand from there.

If they're specifically paying for Docker Hub rate limits or private repos: that's a separate commercial conversation, not a blocker for evaluation.

### "We can't run as nonroot"

**Response:**

Most blockers here are one of three things:

1. **Port binding below 1024**: The app listens on port 80 or 443. Fix: change the container to listen on 8080/8443, let the service/ingress handle external port mapping. This is a one-line change in most apps.
2. **Volume mounts with root ownership**: The host path or persistent volume has root ownership. Fix: `fsGroup` / `runAsGroup` in the pod spec, or `chown` in an init container.
3. **Assumption that nonroot can't write to /tmp or /app**: Chainguard images create `/home/nonroot` and set ownership. Use that as the working directory, or add a `RUN chown nonroot:nonroot /app` in your Dockerfile.

The Dockerfile in this repo (`WORKDIR /app`, `ENV VIRTUAL_ENV=/home/nonroot/.venv`) is a working example of a nonroot Python service. Show it.

For the rare case where they truly need root at runtime (legacy app, kernel interaction): that's a separate security conversation with their team, not a Chainguard limitation.

### "We need a shell for debugging"

**Response:**

Chainguard ships two variants for every image:

- `:latest` — runtime image, no shell, no package manager, minimal attack surface
- `:latest-dev` — development/debug variant, includes shell and apk

In production: use `:latest`. If you need to debug a running container, use `kubectl debug` with an ephemeral container that has the tooling you need — it attaches without modifying the running pod spec. This is the correct cloud-native pattern regardless of which base image you use.

In CI/CD and build stages: use `:latest-dev` freely. The build stage doesn't end up in your runtime image.

Show the multi-stage Dockerfile pattern: `FROM cgr.dev/chainguard/python:latest-dev AS builder` / `FROM cgr.dev/chainguard/python:latest AS runtime`.

---

## Follow-Up Email Template

Send within 24 hours of the workshop.

---

**Subject:** Chainguard workshop — next steps and resources

Hi [Name],

Thanks for the time today. A few things to follow up on:

**What we covered:**
- [Module list you ran]
- Key finding: [e.g., "your current python:3.12-alpine image carries 47 CVEs vs 0 on the equivalent Chainguard image"]

**Agreed next steps:**
- [ ] [Their action] — [Name], by [date]
- [ ] [Your action] — [Your name], by [date]

**Resources:**
- [Chainguard image catalog](https://images.chainguard.dev) — find the equivalent for any image you're using today
- [chainguard.dev/edu](https://edu.chainguard.dev) — docs, how-tos, and the Wolfi package index
- [Cosign / Sigstore policy-controller](https://docs.sigstore.dev/policy-controller/overview/) — for the security team approval workflow we discussed

**Pilot candidate:** [App/service they named]. I'll send a suggested migration Dockerfile for that stack separately.

Let me know if anything came up after you left. Happy to do a follow-on call with [security team / platform team / whoever wasn't in the room].

[Your name]

---

## POV Bypass Criteria

A formal POV (proof of value) engagement adds process overhead. These conditions suggest you can skip the POV and move directly to a pilot or purchase:

| Condition | Rationale |
|-----------|-----------|
| Prospect already runs a scanner and you showed them the CVE delta live | The data spoke. They saw it themselves. No additional validation needed. |
| Compliance deadline is driving urgency (audit in < 90 days) | They don't have time for a multi-week POV. Go straight to pilot with a defined success criterion. |
| Security team attended the workshop and approved the SBOM/attestation story in the room | Approval blocker is cleared. |
| Pilot candidate is a non-critical internal service with a single team owner | Low blast radius. They can migrate it and measure results without a formal POV structure. |
| Champion has budget authority and a clear success metric | No additional stakeholders to sell. Define success, set a timeline, start the pilot. |
| They're already a Chainguard customer on a different tier | Trust is established. Expanding to a new product area doesn't need a POV — just a scoped pilot. |

When bypassing the POV, still document a success criterion and review date. "We'll migrate [service], scan it with [their scanner], and compare CVE count to baseline at [date]" is enough.
