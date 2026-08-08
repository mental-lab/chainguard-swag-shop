# SLO compliance — "vulnerabilities must be triaged under N days" -> violation.
#
# Operates on the remediation records in security-evidence/remediation-records/
# (the audit trail), flagging any remediation that breached its severity SLO.
#
#   opa eval -d policy/vex/ -d security-evidence/records.json \
#     --format pretty 'data.remediation.slo.violation'
package remediation.slo

import rego.v1

# SLO hours by severity (mirrors security/remediation-policy.yaml).
slo_hours := {"CRITICAL": 24, "HIGH": 168, "MEDIUM": 720}

# A record breaches its SLO if detected -> closed exceeds the severity window.
over_slo contains record if {
	some record in input.records
	hours := slo_hours[upper(record.severity)]
	detected := time.parse_rfc3339_ns(record.detected)
	closed := time.parse_rfc3339_ns(record.closed)
	elapsed_hours := ((closed - detected) / 1000000000) / 3600
	elapsed_hours > hours
}

# Unclosed records still within their window are fine; past it is a violation.
open_over_slo contains record if {
	some record in input.records
	not record.closed
	hours := slo_hours[upper(record.severity)]
	detected := time.parse_rfc3339_ns(record.detected)
	elapsed_hours := ((time.now_ns() - detected) / 1000000000) / 3600
	elapsed_hours > hours
}

violation contains {"description": description, "key": "remediation_over_slo", "msg": msg} if {
	count(over_slo) > 0
	msg := "Remediations exceeded severity SLO"
	description := sprintf("%d remediation(s) closed after their SLO: %s", [
		count(over_slo),
		concat(", ", [r.ticket | some r in over_slo]),
	])
}

violation contains {"description": description, "key": "open_remediation_over_slo", "msg": msg} if {
	count(open_over_slo) > 0
	msg := "Open remediations past SLO"
	description := sprintf("%d open remediation(s) are past their SLO: %s", [
		count(open_over_slo),
		concat(", ", [r.ticket | some r in open_over_slo]),
	])
}
