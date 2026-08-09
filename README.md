# Chainguard Swag Shop

An intentionally vulnerable Flask storefront wired to a full security
pipeline — the live receipt for a remediation story:

> Scanners drown you in CVEs and offer upgrades that break your app.
> Chainguard gives you **same-version fixes**: a hardened OS image and
> backported library builds. This repo proves it in CI.

The app itself is deliberately ordinary (browse swag, add to cart, check
out). The point is everything around it.

## The two states

| | `main` (before) | `demo/chainguard-fix` (after) |
| --- | --- | --- |
| Base image | `python:3.12-slim` (upstream) | Chainguard Python image |
| Libraries | PyPI pins with known CVEs | Chainguard Libraries backports (`+cgr.N`) |
| Policy gate | 🔴 red — unapplied fixes exist | 🟢 green |

## The pipeline

Every push and PR runs `.github/workflows/security.yml`:

```
unit tests → build image → e2e smoke (Playwright) ─┐
                                                   ├→ scan (Draugr: Trivy · Gitleaks · Semgrep → SARIF)
                                            scan ──┤→ advisor (suture: Chainguard OpenVEX → remediation table)
                                                   └→ policy gate (Conftest/Rego: fails on unapplied Chainguard fixes)
```

Each job writes a **GitHub job summary** — open any run and read top to
bottom; no artifact digging required.

- **Draugr** consolidates SCA, secrets, SAST, and IaC into one SARIF report
  in Security → Code scanning, ranked by real risk.
- **suture** cross-references scan findings against the Chainguard OpenVEX
  feed and answers "is there a same-version fix?": backport /
  upgrade-or-replace / exception-review.
- **The gate** fails exactly when an internet-facing Critical/High has a
  Chainguard fix available that hasn't been applied. On `main` it's red on
  purpose — that's the "before".

## Run it

```bash
docker build -t swag-shop .
docker run -p 8000:8000 swag-shop        # http://127.0.0.1:8000
```

Or locally:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

`make help` lists the common targets (`make develop`, `make e2e-smoke`, …).

## Chainguard Libraries authentication

Pulling `+cgr.N` backported packages requires a `.netrc` entry:

```
machine libraries.cgr.dev
login <username>
password <token>
```

(`chmod 600 ~/.netrc`.) In CI this arrives as a Docker build secret. The
`demo/chainguard-fix` branch documents where it's needed; the Libraries
entitlement for this demo org is pending, so the after-state's library
pulls are the one step that waits on it.

## Contributing

Issues and PRs welcome. This is a demo repo — keep it legible; the audience
is someone reading the pipeline for the first time.
