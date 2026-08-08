#!/usr/bin/env python3
"""Upstream-vs-Chainguard CVE audit → standalone HTML report (the "arm" artifact).

Builds (or pulls) the two swag-shop images — stock upstream and Chainguard —
scans each with grype (raw, and VEX-aware on the Chainguard image), and renders
a single self-contained HTML file an evaluator can open in any browser. No
server, no dashboard: the report *is* the deliverable. Modeled on the
dhi-vex-audit pattern.

Usage:
    python3 scripts/cve_report.py --out cve-audit-report.html
    python3 scripts/cve_report.py --use-cache          # re-render, no re-scan
    python3 scripts/cve_report.py --upstream-img X --chainguard-img Y

Requires: grype + docker on PATH. The VEX-aware pass uses the Chainguard
OpenVEX documents fetched by scripts/vex-cache.py --write-docs.
"""
import argparse
import html
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

CACHE_FILE = "cve_audit_cache.json"
SEVS = ["Critical", "High", "Medium", "Low", "Negligible", "Unknown"]


@dataclass
class ImageReport:
    label: str
    image: str
    raw: List[dict] = field(default_factory=list)
    residual: List[dict] = field(default_factory=list)
    error: str = ""

    def n(self, findings, sev):
        return sum(1 for f in findings if f.get("severity", "").lower() == sev.lower())


def run_cmd(args, timeout=600) -> Tuple[str, str, int]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", f"timed out after {timeout}s", 1
    except FileNotFoundError:
        return "", f"command not found: {args[0]}", 1


def grype(image: str, vex_dir: Optional[str]) -> Tuple[List[dict], str]:
    cmd = ["grype", image, "-o", "json", "--add-cpes-if-none"]
    if vex_dir:
        cmd += ["--vex", vex_dir]
    out, err, rc = run_cmd(cmd)
    if rc != 0 and not out:
        return [], err.strip()
    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        return [], f"JSON parse error: {e}"
    findings = []
    for m in data.get("matches", []):
        v, a = m.get("vulnerability", {}), m.get("artifact", {})
        fix = v.get("fix", {}).get("versions", [])
        findings.append({
            "id": v.get("id", "UNKNOWN"),
            "severity": v.get("severity", "Unknown"),
            "package": a.get("name", ""),
            "version": a.get("version", ""),
            "fixed": fix[0] if fix else None,
        })
    return findings, ""


def ensure_vex_docs() -> Optional[str]:
    docs = Path("vex-documents")
    if docs.exists() and any(docs.glob("*.openvex.json")):
        return str(docs)
    rc = subprocess.call([sys.executable, "scripts/vex-cache.py",
                          "--write-docs", str(docs)])
    return str(docs) if rc == 0 else None


def build_image(dockerfile: str, tag: str) -> str:
    print(f"  building {tag} from {dockerfile} ...", flush=True)
    # netrc build secret authorizes the Chainguard Libraries index.
    cmd = ["docker", "build", "-f", dockerfile, "-t", tag,
           "--secret", "id=netrc,src=" + str(Path.home() / ".netrc"), "."]
    _, err, rc = run_cmd(cmd, timeout=900)
    return "" if rc == 0 else err.strip()


def scan(label, image, use_vex):
    print(f"[{label}] grype {image} (raw) ...", flush=True)
    raw, err = grype(image, None)
    rep = ImageReport(label=label, image=image, raw=raw, error=err)
    if use_vex and not err:
        vex = ensure_vex_docs()
        if vex:
            print(f"[{label}] grype {image} (VEX-aware) ...", flush=True)
            residual, err2 = grype(image, vex)
            rep.residual = residual
            if err2:
                rep.error = err2
    return rep


def sev_td(findings, sev):
    n = sum(1 for f in findings if f.get("severity", "").lower() == sev.lower())
    cls = f"sev-{sev.lower()}" if n else "sev-zero"
    return f'<td class="{cls}">{n}</td>'


def render(reports: List[ImageReport]) -> str:
    up = next((r for r in reports if "upstream" in r.label.lower()), reports[0])
    cg = next((r for r in reports if "chainguard" in r.label.lower()), reports[-1])
    up_total = len(up.raw)
    cg_residual = cg.residual if cg.residual else cg.raw
    cg_total = len(cg_residual)
    pct = (100 * (up_total - cg_total) / up_total) if up_total else 0

    def row(r):
        resid = r.residual if r.residual else r.raw
        raw_cells = "".join(sev_td(r.raw, s) for s in SEVS[:4])
        res_cells = "".join(sev_td(resid, s) for s in SEVS[:4])
        return (f"<tr><td class='img'>{html.escape(r.label)}</td>"
                f"<td>{len(r.raw)}</td>{raw_cells}"
                f"<td class='resid'>{len(resid)}</td>{res_cells}</tr>")

    rows = "".join(row(r) for r in reports)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Swag Shop CVE Audit — upstream vs Chainguard</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  margin:0;background:#0f1115;color:#e6e6e6}}
 .wrap{{max-width:980px;margin:0 auto;padding:40px 24px}}
 h1{{font-size:26px;margin:0 0 4px}} .sub{{color:#9aa0aa;margin:0 0 26px}}
 .hero{{display:flex;gap:16px;margin:22px 0}}
 .card{{flex:1;background:#171a21;border:1px solid #262b36;border-radius:12px;
  padding:20px;text-align:center}}
 .big{{font-size:42px;font-weight:700}} .lbl{{color:#9aa0aa;font-size:12px;
  text-transform:uppercase;letter-spacing:.05em}}
 .down{{color:#4ade80}} code{{background:#1c2029;padding:1px 5px;border-radius:4px}}
 table{{width:100%;border-collapse:collapse;background:#171a21;
  border:1px solid #262b36;border-radius:12px;overflow:hidden}}
 th,td{{padding:10px 12px;text-align:center;border-bottom:1px solid #262b36}}
 th{{background:#1c2029;color:#9aa0aa;font-size:12px;text-transform:uppercase}}
 td.img{{text-align:left;font-weight:600}} td.resid{{font-weight:700}}
 .sev-critical{{color:#f87171;font-weight:700}} .sev-high{{color:#fb923c}}
 .sev-medium{{color:#facc15}} .sev-low{{color:#a3e635}} .sev-zero{{color:#3f4652}}
 .foot{{color:#6b7280;font-size:12px;margin-top:24px;line-height:1.5}}
</style></head><body><div class="wrap">
<h1>Same app. Two base images.</h1>
<p class="sub">Chainguard swag shop · independent grype scan ·
 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
<div class="hero">
 <div class="card"><div class="big">{up_total}</div><div class="lbl">Upstream CVEs</div></div>
 <div class="card"><div class="big down">{cg_total}</div><div class="lbl">Chainguard residual</div></div>
 <div class="card"><div class="big down">{pct:.0f}%</div><div class="lbl">CVE surface reduced</div></div>
</div>
<p>We didn't triage {up_total} CVEs. We changed one line of the Dockerfile —
<code>FROM python:3.12-slim</code> → <code>FROM cgr.dev/&lt;org&gt;/python</code> —
and the rest stopped existing. No application code changed.</p>
<table><thead>
<tr><th rowspan=2 style="text-align:left">Image</th><th colspan=5>Raw scan</th>
<th colspan=5>VEX-aware residual</th></tr>
<tr><th>Total</th><th>Crit</th><th>High</th><th>Med</th><th>Low</th>
<th>Total</th><th>Crit</th><th>High</th><th>Med</th><th>Low</th></tr>
</thead><tbody>{rows}</tbody></table>
<p class="foot">Raw = grype against the image as built. VEX-aware = grype
--vex with Chainguard's public OpenVEX documents, dropping findings marked
status:&nbsp;fixed, so the residual is the surface your team still owns — not
the raw NVD match list. Reproduce: <code>python3 scripts/cve_report.py</code>.
Generated by scripts/cve_report.py.</p>
</div></body></html>"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--upstream-img", default="swag-shop:upstream")
    p.add_argument("--chainguard-img", default="swag-shop:chainguard")
    p.add_argument("--upstream-dockerfile", default="Dockerfile.upstream")
    p.add_argument("--chainguard-dockerfile", default="Dockerfile")
    p.add_argument("--no-build", action="store_true",
                   help="assume images already exist; skip docker build")
    p.add_argument("--no-vex", action="store_true")
    p.add_argument("--out", default="cve-audit-report.html")
    p.add_argument("--use-cache", action="store_true")
    args = p.parse_args()

    if args.use_cache:
        cached = json.loads(Path(CACHE_FILE).read_text())
        reports = [ImageReport(**r) for r in cached["reports"]]
    else:
        if not args.no_build:
            err = build_image(args.upstream_dockerfile, args.upstream_img)
            if err:
                print(f"warn: upstream build issue: {err[:200]}", file=sys.stderr)
            err = build_image(args.chainguard_dockerfile, args.chainguard_img)
            if err:
                print(f"warn: chainguard build issue: {err[:200]}", file=sys.stderr)
        reports = [
            scan("upstream (python:3.12-slim + PyPI)", args.upstream_img, False),
            scan("chainguard (cgr.dev python + Libraries)", args.chainguard_img,
                 not args.no_vex),
        ]
        Path(CACHE_FILE).write_text(json.dumps(
            {"reports": [asdict(r) for r in reports]}, indent=1))

    Path(args.out).write_text(render(reports))
    print(f"Wrote {args.out}")
    for r in reports:
        resid = len(r.residual) if r.residual else len(r.raw)
        print(f"  {r.label}: raw={len(r.raw)} residual={resid}"
              + (f" ERROR={r.error}" if r.error else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
