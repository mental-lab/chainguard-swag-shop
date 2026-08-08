#!/usr/bin/env bash
# Live "Moment 3" demo: verify an artifact's signature, SBOM attestation and
# build provenance. Always pass a DIGEST reference, never a mutable tag.
#
#   ./scripts/verify-artifact.sh ghcr.io/<org>/chainguard-swag-shop@sha256:<digest>
set -euo pipefail

IMAGE="${1:?usage: verify-artifact.sh <image>@sha256:<digest>}"

if [[ "${IMAGE}" != *@sha256:* ]]; then
  echo "ERROR: reference must be digest-pinned (…@sha256:…), not a tag" >&2
  exit 2
fi

echo "==> Artifact"
echo "    ${IMAGE}"
echo

echo "==> 1/4 Verify keyless cosign signature"
cosign verify "${IMAGE}" \
  --certificate-identity-regexp 'https://github.com/' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  | jq -r '.[0].critical.identity' | sed 's/^/    identity: /'
echo "    Signature: VALID"
echo

echo "==> 2/4 Retrieve SBOM attestation"
cosign verify-attestation "${IMAGE}" \
  --type https://spdx.dev/Document \
  --certificate-identity-regexp 'https://github.com/' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  | jq -r '.payload' | base64 -d | jq '.predicate.packages | length' \
  | sed 's/^/    packages in SBOM: /'
echo "    SBOM: VERIFIED"
echo

echo "==> 3/4 Verify SLSA build provenance (GitHub artifact attestation)"
gh attestation verify "${IMAGE}" --owner "$(echo "${IMAGE}" | cut -d/ -f2)" \
  | sed 's/^/    /'
echo

echo "==> 4/4 Transparency evidence (Rekor)"
cosign verify "${IMAGE}" \
  --certificate-identity-regexp 'https://github.com/' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  >/dev/null
echo "    Transparency log entry: VALID"
echo

echo "Verification successful — signature, SBOM, provenance and transparency"
echo "evidence all check out for ${IMAGE}"
