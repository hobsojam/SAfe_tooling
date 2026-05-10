"""Seed realistic PI planning data for local development.

Activated by setting SAFE_SEED_DEV=1. Only runs when the database is
empty (no ARTs exist), so it is safe to call on every startup.
"""

from datetime import date

from safe.models.art import ART, Team
from safe.models.backlog import Feature, Story
from safe.models.dependency import Dependency, DependencyStatus
from safe.models.objectives import PIObjective
from safe.models.pi import PI, Iteration, PIStatus
from safe.models.risk import Risk, ROAMStatus
from safe.store.repos import Repos


def seed(repos: Repos) -> None:
    if repos.arts.get_all():
        return  # already seeded

    # --- ART ---
    art = ART(name="Platform ART")
    repos.arts.save(art)

    # --- Teams ---
    alpha = Team(name="Alpha", member_count=6, art_id=art.id)
    beta = Team(name="Beta", member_count=5, art_id=art.id)
    gamma = Team(name="Gamma", member_count=7, art_id=art.id)
    delta = Team(name="Delta", member_count=4, art_id=art.id)
    for t in [alpha, beta, gamma, delta]:
        repos.teams.save(t)
    art = art.model_copy(update={"team_ids": [alpha.id, beta.id, gamma.id, delta.id]})
    repos.arts.save(art)

    # --- Iterations ---
    i1 = Iteration(pi_id="", number=1, start_date=date(2026, 1, 5), end_date=date(2026, 1, 16))
    i2 = Iteration(pi_id="", number=2, start_date=date(2026, 1, 19), end_date=date(2026, 1, 30))
    i3 = Iteration(pi_id="", number=3, start_date=date(2026, 2, 2), end_date=date(2026, 2, 13))
    i4 = Iteration(pi_id="", number=4, start_date=date(2026, 2, 16), end_date=date(2026, 2, 27))
    ip = Iteration(
        pi_id="", number=5, start_date=date(2026, 3, 2), end_date=date(2026, 3, 13), is_ip=True
    )

    # --- PI ---
    pi = PI(
        name="PI 2026.1",
        art_id=art.id,
        start_date=date(2026, 1, 5),
        end_date=date(2026, 3, 13),
        status=PIStatus.ACTIVE,
        iteration_ids=[i1.id, i2.id, i3.id, i4.id, ip.id],
    )
    for it in [i1, i2, i3, i4, ip]:
        repos.iterations.save(it.model_copy(update={"pi_id": pi.id}))
    repos.pis.save(pi)

    # --- Features ---
    auth = Feature(
        name="Auth Service",
        pi_id=pi.id,
        team_id=alpha.id,
        user_business_value=8,
        time_criticality=5,
        risk_reduction_opportunity_enablement=3,
        job_size=3,
    )
    sso = Feature(
        name="SSO Integration",
        pi_id=pi.id,
        team_id=alpha.id,
        user_business_value=5,
        time_criticality=8,
        risk_reduction_opportunity_enablement=2,
        job_size=5,
    )
    observability = Feature(
        name="Observability Dashboard",
        pi_id=pi.id,
        team_id=beta.id,
        user_business_value=6,
        time_criticality=3,
        risk_reduction_opportunity_enablement=8,
        job_size=4,
    )
    pipeline = Feature(
        name="CI/CD Pipeline Upgrade",
        pi_id=pi.id,
        team_id=beta.id,
        user_business_value=4,
        time_criticality=2,
        risk_reduction_opportunity_enablement=5,
        job_size=2,
    )
    data_lake = Feature(
        name="Data Lake Integration",
        pi_id=pi.id,
        team_id=gamma.id,
        user_business_value=7,
        time_criticality=4,
        risk_reduction_opportunity_enablement=6,
        job_size=5,
    )
    api_gateway = Feature(
        name="API Gateway",
        pi_id=pi.id,
        team_id=delta.id,
        user_business_value=9,
        time_criticality=7,
        risk_reduction_opportunity_enablement=4,
        job_size=3,
    )
    for f in [auth, sso, observability, pipeline, data_lake, api_gateway]:
        repos.features.save(f)

    # --- Stories (drives Board placement) ---
    def story(name: str, feature_id: str, team_id: str, points: int, iteration_id: str) -> Story:
        return Story(
            name=name,
            feature_id=feature_id,
            team_id=team_id,
            points=points,
            iteration_id=iteration_id,
        )

    stories = [
        story("Login flow", auth.id, alpha.id, 3, i1.id),
        story("Token refresh", auth.id, alpha.id, 2, i1.id),
        story("Password reset", auth.id, alpha.id, 2, i2.id),
        story("SAML handshake", sso.id, alpha.id, 5, i2.id),
        story("IdP configuration UI", sso.id, alpha.id, 3, i3.id),
        story("Metrics pipeline", observability.id, beta.id, 4, i1.id),
        story("Grafana dashboards", observability.id, beta.id, 3, i2.id),
        story("Alerting rules", observability.id, beta.id, 2, i3.id),
        story("Runner upgrade", pipeline.id, beta.id, 3, i3.id),
        story("Cache layer", pipeline.id, beta.id, 2, i4.id),
        story("Schema registry", data_lake.id, gamma.id, 3, i2.id),
        story("Ingestion pipeline", data_lake.id, gamma.id, 4, i3.id),
        story("Rate limiting", api_gateway.id, delta.id, 3, i1.id),
        story("Auth middleware", api_gateway.id, delta.id, 4, i2.id),
    ]
    for s in stories:
        repos.stories.save(s)

    # --- Risks ---
    r1 = Risk(
        description="Auth service external dependency may be unavailable during Iteration 1",
        pi_id=pi.id,
        team_id=alpha.id,
        owner="Alice",
    )
    r2 = Risk(
        description="SAML library upgrade introduces breaking changes",
        pi_id=pi.id,
        team_id=alpha.id,
        owner="Bob",
        roam_status=ROAMStatus.MITIGATED,
        mitigation_notes="Pinned to v2.x; upgrade deferred to next PI",
    )
    r3 = Risk(
        description="Grafana Cloud trial expires mid-PI",
        pi_id=pi.id,
        team_id=beta.id,
        owner="Carol",
        roam_status=ROAMStatus.OWNED,
    )
    for r in [r1, r2, r3]:
        repos.risks.save(r)

    # --- Dependencies ---
    # from_feature_id = consumer (the feature that HAS the dependency)
    # to_feature_id   = provider (the feature that must FULFIL the dependency first)
    d1 = Dependency(
        description="Auth API contract must be finalised before SSO integration begins",
        pi_id=pi.id,
        from_feature_id=sso.id,
        to_feature_id=auth.id,
        owner="Alice",
        needed_by_date=date(2026, 1, 16),
        status=DependencyStatus.RESOLVED,
        resolution_notes="Contract agreed in Iteration 1 kick-off",
    )
    d2 = Dependency(
        description="Observability metrics endpoint needed by CI/CD pipeline health checks",
        pi_id=pi.id,
        from_feature_id=pipeline.id,
        to_feature_id=observability.id,
        owner="Carol",
        needed_by_date=date(2026, 2, 13),
        status=DependencyStatus.IDENTIFIED,
    )
    d3 = Dependency(
        description="Auth service token validation endpoint needed by Observability team",
        pi_id=pi.id,
        from_feature_id=observability.id,
        to_feature_id=auth.id,
        owner="Bob",
        needed_by_date=date(2026, 1, 30),
        status=DependencyStatus.IN_PROGRESS,
        resolution_notes="Interface agreed; implementation tracked via story",
    )
    d4 = Dependency(
        description="API Gateway auth middleware requires Auth Service token endpoint",
        pi_id=pi.id,
        from_feature_id=api_gateway.id,
        to_feature_id=auth.id,
        owner="Alice",
        needed_by_date=date(2026, 1, 30),
        status=DependencyStatus.IDENTIFIED,
    )
    d5 = Dependency(
        description="Data Lake ingestion pipeline needs CI/CD deployment pipeline",
        pi_id=pi.id,
        from_feature_id=data_lake.id,
        to_feature_id=pipeline.id,
        owner="Carol",
        needed_by_date=date(2026, 2, 13),
        status=DependencyStatus.ACKNOWLEDGED,
    )
    for d in [d1, d2, d3, d4, d5]:
        repos.dependencies.save(d)

    # ── Bulk data for pagination testing (>25 rows on every table) ──────────
    teams = [alpha, beta, gamma, delta]

    bulk_feature_specs = [
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
    ]
    bulk_features = []
    for idx, (name, ubv, tc, rroe, js) in enumerate(bulk_feature_specs):
        f = Feature(
            name=name,
            pi_id=pi.id,
            team_id=teams[idx % len(teams)].id,
            user_business_value=ubv,
            time_criticality=tc,
            risk_reduction_opportunity_enablement=rroe,
            job_size=js,
        )
        repos.features.save(f)
        bulk_features.append(f)

    bulk_story_specs = [
        ("Implement search indexing pipeline", 3),
        ("Add full-text query API endpoint", 5),
        ("Set up push notification routing", 2),
        ("Implement delivery retry logic", 3),
        ("Write audit event schema", 2),
        ("Persist audit events to object storage", 3),
        ("Build audit log query API", 4),
        ("Migrate user profile schema to v2", 5),
        ("Add bulk user import endpoint", 3),
        ("Define mobile auth token format", 2),
        ("Implement mobile API rate limiting", 3),
        ("Build GraphQL schema stitching layer", 5),
        ("Add federation gateway health checks", 2),
        ("Publish event bus message envelope spec", 2),
        ("Implement at-least-once delivery guarantee", 4),
        ("Build config service REST API", 3),
        ("Add config change audit trail", 2),
        ("Implement flag evaluation SDK", 4),
        ("Build flag management UI", 3),
        ("Add per-route rate limit configuration", 3),
        ("Implement sliding window rate limit algorithm", 4),
        ("Write canary routing rules engine", 5),
        ("Implement traffic split percentage controls", 3),
        ("Automate blue-green DNS switchover", 4),
        ("Add rollback trigger on error budget breach", 3),
        ("Deploy Envoy sidecar to all namespaces", 5),
        ("Configure mutual TLS across mesh", 3),
        ("Instrument all services with OTel spans", 4),
        ("Build trace search UI", 3),
        ("Automate certificate rotation workflow", 4),
    ]
    iters = [i1, i2, i3, i4]
    for idx, (name, points) in enumerate(bulk_story_specs):
        feature = bulk_features[idx % len(bulk_features)]
        s = Story(
            name=name,
            feature_id=feature.id,
            team_id=teams[idx % len(teams)].id,
            points=points,
            iteration_id=iters[idx % len(iters)].id,
        )
        repos.stories.save(s)

    bulk_risk_specs = [
        ("Team capacity reduced due to unexpected attrition", ROAMStatus.UNROAMED, "Alice"),
        ("Third-party certificate authority renewal delay", ROAMStatus.OWNED, "Bob"),
        ("Legacy database migration may cause downtime", ROAMStatus.ACCEPTED, "Carol"),
        ("Vendor API deprecation without notice", ROAMStatus.UNROAMED, "Dave"),
        ("Cloud provider outage risk in Iteration 2", ROAMStatus.MITIGATED, "Alice"),
        ("Regulatory audit scheduled during IP iteration", ROAMStatus.OWNED, "Bob"),
        ("Key engineer leaving mid-PI", ROAMStatus.UNROAMED, "Carol"),
        ("Load test environment not ready in time", ROAMStatus.ACCEPTED, "Dave"),
        ("Security scan reveals critical CVE in dependency", ROAMStatus.UNROAMED, "Alice"),
        ("Integration partner delayed sign-off", ROAMStatus.MITIGATED, "Bob"),
        ("Feature flag service instability under load", ROAMStatus.OWNED, "Carol"),
        ("DNS propagation delays for new endpoints", ROAMStatus.RESOLVED, "Dave"),
        ("Mobile OS update breaks auth flow", ROAMStatus.UNROAMED, "Alice"),
        ("Data residency requirement change from legal", ROAMStatus.OWNED, "Bob"),
        ("Inconsistent test coverage in payment module", ROAMStatus.ACCEPTED, "Carol"),
        ("Container registry rate limit exceeded in CI", ROAMStatus.MITIGATED, "Dave"),
        ("Performance regression in search service", ROAMStatus.UNROAMED, "Alice"),
        ("Cross-team sprint sync scheduling conflict", ROAMStatus.RESOLVED, "Bob"),
        ("Secrets rotation breaking downstream services", ROAMStatus.OWNED, "Carol"),
        ("Backup restore procedure not yet tested", ROAMStatus.UNROAMED, "Dave"),
        ("Kafka rebalancing during peak traffic window", ROAMStatus.ACCEPTED, "Alice"),
        ("SSO provider SLA degraded for 48 hours", ROAMStatus.MITIGATED, "Bob"),
        ("GDPR requirements impact data lake schema", ROAMStatus.OWNED, "Carol"),
        ("Product owner unavailable for three sprints", ROAMStatus.UNROAMED, "Dave"),
        ("CI pipeline flakiness delaying releases", ROAMStatus.ACCEPTED, "Alice"),
        ("API gateway TLS handshake timeout under load", ROAMStatus.UNROAMED, "Bob"),
        ("Infrastructure as code drift detected", ROAMStatus.OWNED, "Carol"),
    ]
    for idx, (desc, status, owner) in enumerate(bulk_risk_specs):
        repos.risks.save(
            Risk(
                description=desc,
                pi_id=pi.id,
                team_id=teams[idx % len(teams)].id,
                roam_status=status,
                owner=owner,
            )
        )

    bulk_objective_specs = [
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
    for idx, (desc, is_stretch, planned_bv) in enumerate(bulk_objective_specs):
        repos.objectives.save(
            PIObjective(
                description=desc,
                pi_id=pi.id,
                team_id=teams[idx % len(teams)].id,
                planned_business_value=planned_bv,
                is_stretch=is_stretch,
            )
        )

    bulk_dep_descriptions = [
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
    ]
    n = len(bulk_features)
    owners = ["Alice", "Bob", "Carol", "Dave"]
    # Only 4 bulk features act as dependency targets so that, combined with the
    # 3 original targets (auth, observability, pipeline), exactly 7 distinct
    # features have dependencies pointing to them across the full dataset.
    _dep_targets = bulk_features[:4]
    for idx, desc in enumerate(bulk_dep_descriptions):
        from_f = bulk_features[idx % n]
        to_f = _dep_targets[idx % len(_dep_targets)]
        if to_f.id == from_f.id:
            to_f = _dep_targets[(idx + 1) % len(_dep_targets)]
        repos.dependencies.save(
            Dependency(
                description=desc,
                pi_id=pi.id,
                from_feature_id=from_f.id,
                to_feature_id=to_f.id,
                owner=owners[idx % len(owners)],
                status=DependencyStatus.IDENTIFIED,
            )
        )
