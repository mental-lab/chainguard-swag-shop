# Workshop Catalog

This directory contains materials for delivering Chainguard workshops to prospects and customers. Each module maps to a product area. Mix and match based on what you learn in discovery.

Start with the [discovery questionnaire](discovery-questionnaire.md) before every engagement. Use the [delivery guide](delivery-guide.md) for timing, objection handling, and follow-up.

---

## Available Modules

| # | Module | Duration | Best For |
|---|--------|----------|----------|
| 01 | **Container Images: Distroless Fundamentals** | 20 min | Any audience. Start here for image security conversations. |
| 02 | **CVE Comparison: Before & After** | 20 min | Security engineers, compliance teams. High impact when prospect has a scanner already. |
| 03 | **SBOMs, Provenance, and Attestations** | 25 min | Platform engineers, security architects, anyone facing audit or compliance requirements. |
| 04 | **Chainguard Libraries (Remediated PyPI)** | 20 min | Python shops. Works well after Module 02 to show the libraries side of the story. |
| 05 | **Custom Assembly & build.yaml** | 30 min | Platform teams who want to own their image composition. Requires Chainguard org access to demo live. |
| 06 | **CI/CD Integration & Registry Patterns** | 25 min | DevOps/platform engineers. Covers GitHub Actions, digest pinning, pull-through, nonroot migration. |

---

## Pre-Built Formats

These are starting points. Adjust based on discovery answers.

| Format | Duration | Module Composition | Notes |
|--------|----------|--------------------|-------|
| **60-min Intro** | 60 min | 01 → 02 → 03 | Executive-friendly. Keep Module 03 high-level. Skip live demos if time is tight. |
| **90-min Technical** | 90 min | 01 → 02 → 03 → 06 | Best for platform or security engineers who own the CI/CD stack. Leaves time for Q&A. |
| **Half-Day Deep Dive** | 3–4 hrs | 01 → 02 → 03 → 04 → 05 → 06 | Full product story. Reserve for committed prospects or existing customers expanding scope. Include breaks. |

---

## When to Use Each Format

| Situation | Recommended Format |
|-----------|-------------------|
| First call with a new prospect, security buyer, VP-level | 60-min Intro |
| Technical POV kickoff, security/platform team invited | 90-min Technical |
| Hands-on lab, customer is ready to evaluate | Half-Day Deep Dive |
| Discovery call only, no demo yet | Skip workshop — use [questionnaire](discovery-questionnaire.md) to qualify |
| Existing customer adding Libraries or Platform tier | Start at Module 04 or 05, skip 01-02 if they know the base story |

---

## Resources

- [discovery-questionnaire.md](discovery-questionnaire.md) — Fill this out before every workshop. Shapes module selection and demo flow.
- [delivery-guide.md](delivery-guide.md) — Timing tips, objection responses, follow-up email template, POV bypass criteria.
