#!/usr/bin/env python3
"""Seed bulk test data for pagination testing.

Requires the API to be running (safe-api or podman compose up -d --build).
Connects to the PI and teams already in your local DB.

Usage:
    python scripts/seed_pagination.py
    python scripts/seed_pagination.py http://localhost:8000
"""
import json
import sys
import urllib.error
import urllib.request

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode()
        raise SystemExit(f"POST {path} failed {exc.code}: {body_text}") from exc


def get(path: str) -> list:
    with urllib.request.urlopen(f"{BASE_URL}{path}") as resp:
        return json.loads(resp.read())


def pick_pi() -> str:
    pis = get("/pi")
    if not pis:
        raise SystemExit("No PIs found. Run the app and create a PI first.")
    pi = pis[0]
    print(f"Using PI: {pi['name']} ({pi['id']})")
    return pi["id"]


def pick_teams() -> list[str]:
    teams = get("/team")
    if not teams:
        raise SystemExit("No teams found. Create teams via the ART Setup page first.")
    ids = [t["id"] for t in teams]
    print(f"Found {len(ids)} team(s): {', '.join(t['name'] for t in teams)}")
    return ids


def main() -> None:
    print(f"Seeding pagination test data → {BASE_URL}\n")

    pi_id = pick_pi()
    team_ids = pick_teams()

    def team(i: int) -> str:
        return team_ids[i % len(team_ids)]

    # ── 30 features ────────────────────────────────────────────────────────
    features_spec = [
        ("Search Service", 8, 6, 4, 3),
        ("Notification Engine", 7, 5, 5, 4),
        ("Audit Log", 6, 4, 8, 2),
        ("User Management v2", 9, 7, 3, 5),
        ("Mobile API", 8, 8, 2, 6),
        ("GraphQL Gateway", 7, 6, 6, 4),
        ("Event Bus", 9, 5, 7, 5),
        ("Config Service", 5, 3, 9, 2),
        ("Feature Flags", 7, 4, 6, 3),
        ("Rate Limiting v2", 8, 7, 4, 4),
        ("Canary Deployment", 6, 5, 8, 4),
        ("Blue-Green Switchover", 7, 6, 6, 5),
        ("Service Mesh", 8, 4, 7, 6),
        ("Distributed Tracing", 7, 5, 8, 4),
        ("Secret Manager", 9, 8, 5, 3),
        ("Certificate Rotation", 6, 7, 7, 2),
        ("Chaos Engineering", 5, 3, 9, 3),
        ("Load Testing Framework", 6, 4, 7, 3),
        ("Error Budget Dashboards", 7, 5, 6, 3),
        ("SLO Alerting", 8, 6, 5, 4),
        ("Cost Optimisation", 7, 4, 7, 5),
        ("Multi-Region Failover", 9, 8, 6, 7),
        ("Dark Launch Infrastructure", 6, 5, 6, 4),
        ("Schema Migration Tooling", 7, 3, 8, 3),
        ("Bulk Export API", 6, 5, 5, 4),
        ("Webhook Delivery", 8, 7, 4, 4),
        ("Tenant Isolation", 9, 7, 5, 5),
        ("Self-Service Portal", 7, 6, 4, 5),
        ("Developer Hub", 6, 4, 5, 4),
        ("SDK Generation", 5, 3, 6, 3),
    ]
    print(f"Creating {len(features_spec)} features…")
    feature_ids: list[str] = []
    for i, (name, ubv, tc, rroe, js) in enumerate(features_spec):
        f = post(
            "/features",
            {
                "name": name,
                "description": f"Seeded for pagination testing (#{i + 1})",
                "pi_id": pi_id,
                "team_id": team(i),
                "status": "backlog",
                "user_business_value": ubv,
                "time_criticality": tc,
                "risk_reduction_opportunity_enablement": rroe,
                "job_size": js,
            },
        )
        feature_ids.append(f["id"])
    print(f"  ✓ {len(feature_ids)} features created")

    # ── 30 risks ────────────────────────────────────────────────────────────
    risks_spec = [
        ("Team capacity reduced due to unexpected attrition", "unroamed"),
        ("Third-party certificate authority renewal delay", "owned"),
        ("Legacy database migration may cause downtime", "accepted"),
        ("Vendor API deprecation without notice", "unroamed"),
        ("Cloud provider outage risk in Iteration 2", "mitigated"),
        ("Regulatory audit scheduled during IP iteration", "owned"),
        ("Key engineer leaving mid-PI", "unroamed"),
        ("Load test environment not ready in time", "accepted"),
        ("Security scan reveals critical CVE in dependency", "unroamed"),
        ("Integration partner delayed sign-off", "mitigated"),
        ("Feature flag service instability under load", "owned"),
        ("DNS propagation delays for new endpoints", "resolved"),
        ("Mobile OS update breaks auth flow", "unroamed"),
        ("Data residency requirement change from legal", "owned"),
        ("Inconsistent test coverage in payment module", "accepted"),
        ("Container registry rate limit exceeded in CI", "mitigated"),
        ("Performance regression introduced in search service", "unroamed"),
        ("Cross-team sprint sync scheduling conflict", "resolved"),
        ("Secrets rotation breaking downstream services", "owned"),
        ("Backup restore procedure not yet tested", "unroamed"),
        ("Kafka rebalancing during peak traffic window", "accepted"),
        ("SSO provider SLA degraded for 48 hours", "mitigated"),
        ("GDPR requirements impact data lake schema", "owned"),
        ("Product owner unavailable for three sprints", "unroamed"),
        ("CI pipeline flakiness delaying releases", "accepted"),
        ("API gateway TLS handshake timeout under load", "unroamed"),
        ("Infrastructure as code drift detected", "owned"),
        ("Dependency on unreleased upstream library version", "mitigated"),
        ("Cross-region latency exceeding SLO threshold", "unroamed"),
        ("Monitoring gap post-migration window", "accepted"),
    ]
    owners = ["Alice", "Bob", "Carol", "Dave"]
    print(f"Creating {len(risks_spec)} risks…")
    for i, (desc, status) in enumerate(risks_spec):
        post(
            "/risks",
            {
                "description": desc,
                "pi_id": pi_id,
                "team_id": team(i),
                "roam_status": status,
                "owner": owners[i % len(owners)],
                "mitigation_notes": "",
            },
        )
    print(f"  ✓ {len(risks_spec)} risks created")

    # ── 30 objectives ───────────────────────────────────────────────────────
    objectives_spec = [
        ("Ship Search Service v1 to production", False, 8),
        ("Reduce p99 latency below 200ms", False, 9),
        ("Achieve 99.9% uptime for payment flows", False, 10),
        ("Complete API gateway migration", False, 8),
        ("Deliver Mobile API v2", False, 7),
        ("Harden secret management across all services", False, 9),
        ("Enable canary deployments for all services", False, 7),
        ("Complete service mesh rollout", False, 8),
        ("Launch developer hub beta", False, 6),
        ("Implement distributed tracing end-to-end", False, 7),
        ("Automate certificate rotation", False, 8),
        ("Deploy SLO alerting framework", False, 9),
        ("Ship multi-region failover for tier-1 services", False, 10),
        ("Deliver bulk export API for reporting", False, 6),
        ("Complete webhook delivery service", False, 7),
        ("Deploy tenant isolation v1", False, 9),
        ("Launch self-service portal for developers", False, 7),
        ("Deliver SDK generation tooling", False, 5),
        ("Complete cost optimisation initiative", False, 7),
        ("Ship schema migration tooling", False, 6),
        ("Introduce chaos engineering practice", False, 5),
        ("Implement load testing framework", False, 6),
        ("Explore GraphQL federation approach", True, 6),
        ("Prototype dark launch infrastructure", True, 5),
        ("Investigate event sourcing for audit log", True, 4),
        ("POC: feature flag SDK for mobile clients", True, 5),
        ("Research AI-assisted code review tooling", True, 3),
        ("Explore eBPF-based observability", True, 4),
        ("Investigate Wasm serverless runtime", True, 3),
        ("Prototype real-time collaboration features", True, 5),
    ]
    print(f"Creating {len(objectives_spec)} objectives…")
    for i, (desc, is_stretch, planned_bv) in enumerate(objectives_spec):
        post(
            "/objectives",
            {
                "description": desc,
                "team_id": team(i),
                "pi_id": pi_id,
                "planned_business_value": planned_bv,
                "actual_business_value": None,
                "is_stretch": is_stretch,
            },
        )
    print(f"  ✓ {len(objectives_spec)} objectives created")

    # ── 30 dependencies (round-robins over seeded feature_ids) ─────────────
    dep_descriptions = [
        "Notification service requires event bus contract to be stable",
        "Search indexing API needed by user management before GA",
        "Mobile API depends on auth token format from auth service",
        "GraphQL gateway requires typed schemas from all downstream services",
        "Config service API must be stable before feature flags ships",
        "Rate limiter interface required by API gateway team",
        "Canary deployment tooling depends on feature flag service",
        "Blue-green switchover depends on load balancer API contract",
        "Service mesh TLS config needed before secret manager ships",
        "Tracing spans need event bus event IDs standardised",
        "SLO alerting depends on metrics pipeline contract",
        "Cost dashboards require billing API from data lake team",
        "Multi-region failover needs DNS automation API from platform team",
        "Dark launch toggle depends on feature flag SDK v2",
        "Schema migration tooling needs database proxy interface",
        "Bulk export API needs schema registry contract from data team",
        "Webhook delivery depends on event bus reliability guarantees",
        "Tenant isolation depends on identity service group API",
        "Self-service portal requires RBAC API from auth service",
        "Developer hub depends on SDK generation output format",
        "Load testing harness needs production traffic mirror API",
        "Error budget dashboards need SLO definition schema agreed",
        "Certificate rotation depends on secret manager vault API",
        "Chaos engineering depends on health-check endpoint spec",
        "Mobile push notifications depend on notification engine contract",
        "Audit log schema needs event bus message envelope format",
        "CI pipeline needs artifact registry API stabilised",
        "Security scan tooling needs deployment manifest format agreed",
        "GraphQL schema stitching needs all service SDL endpoints",
        "Distributed tracing needs B3 propagation header spec from gateway",
    ]
    n = len(feature_ids)
    print(f"Creating {len(dep_descriptions)} dependencies…")
    for i, desc in enumerate(dep_descriptions):
        from_id = feature_ids[i % n]
        to_id = feature_ids[(i + 1) % n]
        post(
            "/dependencies",
            {
                "description": desc,
                "pi_id": pi_id,
                "from_feature_id": from_id,
                "to_feature_id": to_id,
                "owner": owners[i % len(owners)],
                "needed_by_date": None,
            },
        )
    print(f"  ✓ {len(dep_descriptions)} dependencies created")

    print(
        "\nDone! Refresh the app and navigate to Backlog, Risks, Objectives, or "
        "Dependencies to see pagination in action (25 items per page)."
    )


if __name__ == "__main__":
    main()
