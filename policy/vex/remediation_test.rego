# Tests for remediation.rego. Run: opa test policy/vex/ -v
package remediation_test

import rego.v1

import data.remediation

# ── fixtures (the shop's real dependency surface: Flask/Werkzeug/gunicorn) ──
scan_with_fix := {"Results": [{
	"Target": "requirements.txt",
	"Vulnerabilities": [{
		"VulnerabilityID": "CVE-2024-49767",
		"Severity": "HIGH",
		"PkgName": "werkzeug",
		"InstalledVersion": "3.1.8",
	}],
}]}

scan_no_fix_facing := {"Results": [{
	"Target": "requirements.txt",
	"Vulnerabilities": [{
		"VulnerabilityID": "CVE-2099-0001",
		"Severity": "CRITICAL",
		"PkgName": "flask",
		"InstalledVersion": "3.1.3",
	}],
}]}

mock_assets := {"assets": {"assets": {
	"swag-shop": {"internet_exposed": true, "tier": "tier-1"},
}}}

mock_vex := {"vex_cache": {
	"pkg:pypi/werkzeug": {"CVE-2024-49767": ["pkg:pypi/werkzeug@3.1.8%2Bcgr.1"]},
}}

# ── tests ────────────────────────────────────────────────────────────────────
test_backport_recommended_when_fix_exists if {
	rec := remediation.recommendation["CVE-2024-49767"]
		with input as scan_with_fix
		with data.assets as mock_assets.assets
		with data.vex_cache as mock_vex.vex_cache
	rec.action == "backport"
	rec.fix == "pkg:pypi/werkzeug@3.1.8%2Bcgr.1"
}

test_gate_denies_internet_facing_with_available_fix if {
	deny := remediation.deny
		with input as scan_with_fix
		with data.assets as mock_assets.assets
		with data.vex_cache as mock_vex.vex_cache
	count(deny) == 1
}

test_upgrade_or_replace_when_no_fix_but_facing if {
	rec := remediation.recommendation["CVE-2099-0001"]
		with input as scan_no_fix_facing
		with data.assets as mock_assets.assets
		with data.vex_cache as {}
	rec.action == "upgrade-or-replace"
}

test_no_gate_when_no_fix_available if {
	deny := remediation.deny
		with input as scan_no_fix_facing
		with data.assets as mock_assets.assets
		with data.vex_cache as {}
	count(deny) == 0
}
