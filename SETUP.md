# Chainguard Swag Shop — Setup & Troubleshooting Guide

## Overview

This application is a pre-sales demo for Chainguard's product story across three areas:

- **Container Security** — Chainguard distroless images vs standard Docker Hub images
- **Libraries** — Chainguard-remediated PyPI packages vs standard PyPI CVEs
- **Platform: Custom Assembly** — Versioned `build.yaml`, automated CI pipeline, evidence bundle

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.12+ | Local development | `brew install python` |
| Docker (with BuildKit) | Container builds | Docker Desktop |
| `chainctl` | Chainguard CLI | `brew install chainguard-dev/tap/chainctl` |
| `cosign` | Image signature verification | `brew install cosign` |
| `gh` | GitHub CLI | `brew install gh` |
| `jq` | JSON parsing in scripts | `brew install jq` |

---

## Local Development

### 1. Clone and install dependencies

```bash
git clone https://github.com/mental-lab/chainguard-swag-shop
cd chainguard-swag-shop
make install
```

### 2. Run the app locally

```bash
make develop
# App available at http://localhost:8000
```

### 3. Switch between PyPI sources (for Libraries demo)

```bash
# Use Chainguard remediated index (default)
make switch-cgr

# Use standard PyPI only
make switch-pypi

# Show current config and installed packages
make show-config
```

### 4. Build and run the container

`.netrc` must contain credentials for `libraries.cgr.dev` (Chainguard PyPI auth). The build mounts it as a secret — it is never baked into the image.

```bash
# Ensure ~/.netrc has Chainguard credentials:
# machine libraries.cgr.dev login <user> password <token>

make runtime
# Builds as swag-store:runtime

docker run -p 8000:8000 swag-store:runtime
```

---

## GitHub Actions Workflows

### platform-build.yml

Triggers on changes to `build.yaml` or the workflow file itself.

**What it does:**
1. Authenticates to Chainguard via OIDC (`setup-chainctl`) — no long-lived credentials
2. Runs `chainctl images repos build apply` to trigger Custom Assembly
3. Verifies the image signature with `cosign`
4. Extracts SBOM and SLSA provenance attestations
5. Scans with Grype (fails on critical/high CVEs)
6. Uploads an evidence bundle (SBOM, provenance, Grype results, build.yaml) as a 90-day Actions artifact
7. Opens a PR with the updated pinned image digest in the Dockerfile

**Required repo variables (Settings → Variables):**

| Variable | Value | Notes |
|----------|-------|-------|
| `CHAINGUARD_ORG` | `packetloss.network` | Your Chainguard org |
| `CHAINGUARD_IDENTITY` | `<assumable identity ID>` | See [OIDC identity setup](https://edu.chainguard.dev/chainguard/administration/iam-organizations/assumable-ids/identity-examples/github-actions-identity/) |

If either variable is unset, all build steps are skipped gracefully with a log message.

### digestabot.yml

Runs daily at 06:00 UTC. Opens PRs to update container image digests in the Dockerfile. Authenticates with Chainguard via `CHAINGUARD_IDENTITY` to resolve the private org image digest.

### frizbee.yml

Runs weekly on Monday at 06:00 UTC. Attempts to open PRs pinning any mutable Action refs (e.g. `@v4`) to commit SHAs.

> **Note:** `GITHUB_TOKEN` cannot push changes to `.github/workflows/` files — this is a hard GitHub platform limitation. The automated workflow will fail on the "Pin Actions refs" step if unpinned refs exist in workflow files. To pin refs manually, run locally:
>
> ```bash
> GITHUB_TOKEN=$(gh auth token) frizbee actions .github/workflows
> git add .github/workflows && git commit -m "ci: pin Actions refs to SHAs"
> ```

---

## Custom Assembly (build.yaml)

The `build.yaml` at the repo root is the versioned image configuration for the Platform demo. It declares which packages are in the custom image.

```yaml
contents:
  packages:
    - python-3.12
    - py3.12-pip
    - ca-certificates-bundle
```

**Apply manually:**

```bash
chainctl images repos build apply \
  --parent packetloss.network \
  --repo python \
  -f build.yaml \
  --yes
```

> **Note:** Custom Certificates (`certificates:` block) require a separate entitlement. Contact your Chainguard Customer Success team to enable. Do not add a `certificates:` block without this entitlement — the build will fail.

---

## Troubleshooting

### `chainctl images repos build apply` prompts interactively in CI

**Symptom:** CI fails with `{"error":"EOF"}` — chainctl is waiting for `[y,N]` input.

**Fix:** Add `--yes` flag to suppress the confirmation prompt.

```bash
chainctl images repos build apply --parent "$ORG" --repo "$REPO" -f build.yaml --yes
```

---

### `jq: parse error: Invalid numeric literal`

**Symptom:** The build step fails trying to extract the digest with `jq`.

**Root cause:** `chainctl images repos build apply --output json` returns plain text in some cases (see below), not JSON.

**Fix:** Use `grep` to extract the digest instead of relying on clean JSON:

```bash
DIGEST=$(echo "$RESULT" | grep -o '"digest":"[^"]*"' | cut -d'"' -f4)
```

---

### `No changes detected in build config for python`

**Symptom:** The build step logs this message and no digest is produced.

**This is normal behavior.** chainctl returns this when the declared packages in `build.yaml` match what was already built. The workflow handles this gracefully and skips downstream steps (scan, PR, evidence bundle).

To force a new build, make a meaningful change to `build.yaml` (add or update a package).

---

### `{"error":"You are not entitled to use Custom Certificates."}`

**Symptom:** `chainctl images repos build apply` returns this error.

**Fix:** Remove the `certificates:` block from `build.yaml`. Custom Certificates require a separate Chainguard entitlement not included by default.

---

### Workflow fails with "workflow file issue" (0s duration, no jobs ran)

**Symptom:** A GitHub Actions run shows failure at workflow-file level — no jobs ran, duration is 0s.

**Root cause:** An invalid permission scope in the workflow `permissions:` block. `workflows` is not a valid `GITHUB_TOKEN` permission scope in workflow YAML.

**Fix:** Remove `workflows: write` from the `permissions:` block. This scope does not exist for `GITHUB_TOKEN` and causes GitHub to reject the workflow file at parse time.

---

### Frizbee fails: `refusing to allow a GitHub App to create or update workflow without workflows permission`

**Symptom:** Frizbee runs but cannot push its branch containing updated workflow files.

**Root cause:** GitHub blocks `GITHUB_TOKEN` from pushing changes to `.github/workflows/` files regardless of declared permissions. This is a hard platform limit, not a configuration issue.

**Workarounds:**
1. Run Frizbee locally and commit the result (recommended for demo):
   ```bash
   GITHUB_TOKEN=$(gh auth token) frizbee actions .github/workflows
   git add .github/workflows && git commit -m "ci: pin Actions refs to SHAs"
   ```
2. Use a fine-grained PAT scoped to this repo with `Contents + Pull requests + Workflows` write permissions, stored as `FRIZBEE_TOKEN`.

---

### Grype scan shows CVEs after switching to Chainguard Libraries

**Symptom:** Grype still reports CVEs even after `make switch-cgr`.

**Check:** Ensure `requirements.txt` pins current versions. Known-vulnerable pinned versions:

| Package | Vulnerable version | Fixed at |
|---------|-------------------|---------|
| Werkzeug | < 3.1.8 | 3.1.8 |
| Flask | < 3.1.3 | 3.1.3 |

Run `make show-config` to confirm which index is active and which versions are installed.

---

### Non-fast-forward push rejected

**Symptom:** `git push` fails with `rejected — non-fast-forward`.

**Fix:**
```bash
git pull --rebase origin main
git push origin main
```

---

### Grype DB is stale — scan results are outdated

**Symptom:** Grype returns old CVE data or misses recently patched CVEs.

**Fix:** Set the environment variable in the scan step to force a fresh DB download:

```yaml
env:
  GRYPE_DB_UPDATE_ON_START: "true"
```

---

## Package Index Reference

| Index | URL | Purpose |
|-------|-----|---------|
| Chainguard remediated | `https://libraries.cgr.dev/python-remediated/simple` | CVE-free patched packages |
| Chainguard standard | `https://libraries.cgr.dev/python/simple` | Chainguard-built packages |
| PyPI | `https://pypi.org/simple` | Fallback / standard |

Authentication for `libraries.cgr.dev` uses `~/.netrc` locally and a BuildKit secret (`--secret id=netrc`) in Docker builds.
