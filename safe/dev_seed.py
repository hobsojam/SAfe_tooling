"""Seed realistic PI planning data for local development.

Activated by setting SAFE_SEED_DEV=1. Only runs when the database is
empty (no ARTs exist), so it is safe to call on every startup.
"""

from datetime import date

from safe.models.art import ART, Team
from safe.models.backlog import Feature, Story
from safe.models.dependency import Dependency, DependencyStatus
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
        status=DependencyStatus.MITIGATED,
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
        status=DependencyStatus.OWNED,
    )
    for d in [d1, d2, d3, d4, d5]:
        repos.dependencies.save(d)
