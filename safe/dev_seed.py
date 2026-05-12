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
    # iteration_id is the board placement (majority story-point iteration from seed stories below)
    auth = Feature(
        name="Auth Service",
        pi_id=pi.id,
        team_id=alpha.id,
        iteration_id=i1.id,  # i1: 5pts, i2: 2pts
        user_business_value=8,
        time_criticality=5,
        risk_reduction_opportunity_enablement=3,
        job_size=3,
    )
    sso = Feature(
        name="SSO Integration",
        pi_id=pi.id,
        team_id=alpha.id,
        iteration_id=i2.id,  # i2: 5pts, i3: 3pts
        user_business_value=5,
        time_criticality=8,
        risk_reduction_opportunity_enablement=2,
        job_size=5,
    )
    observability = Feature(
        name="Observability Dashboard",
        pi_id=pi.id,
        team_id=beta.id,
        iteration_id=i1.id,  # i1: 4pts, i2: 3pts, i3: 2pts
        user_business_value=6,
        time_criticality=3,
        risk_reduction_opportunity_enablement=8,
        job_size=4,
    )
    pipeline = Feature(
        name="CI/CD Pipeline Upgrade",
        pi_id=pi.id,
        team_id=beta.id,
        iteration_id=i3.id,  # i3: 3pts, i4: 2pts
        user_business_value=4,
        time_criticality=2,
        risk_reduction_opportunity_enablement=5,
        job_size=2,
    )
    data_lake = Feature(
        name="Data Lake Integration",
        pi_id=pi.id,
        team_id=gamma.id,
        iteration_id=i3.id,  # i2: 3pts, i3: 4pts
        user_business_value=7,
        time_criticality=4,
        risk_reduction_opportunity_enablement=6,
        job_size=5,
    )
    api_gateway = Feature(
        name="API Gateway",
        pi_id=pi.id,
        team_id=delta.id,
        iteration_id=i2.id,  # i1: 3pts, i2: 4pts
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

    # --- PI Objectives ---
    obj1 = PIObjective(
        description="Deliver Auth Service v2 with token refresh and password reset",
        team_id=alpha.id,
        pi_id=pi.id,
        planned_business_value=10,
        actual_business_value=10,
    )
    obj2 = PIObjective(
        description="Roll out Observability Dashboard to all ART teams",
        team_id=beta.id,
        pi_id=pi.id,
        planned_business_value=8,
        actual_business_value=7,
    )
    obj3 = PIObjective(
        description="Complete SSO integration with SAML and IdP configuration",
        team_id=alpha.id,
        pi_id=pi.id,
        planned_business_value=7,
        actual_business_value=None,
        is_stretch=False,
    )
    obj4 = PIObjective(
        description="Ingest first production dataset into Data Lake",
        team_id=gamma.id,
        pi_id=pi.id,
        planned_business_value=9,
        actual_business_value=None,
    )
    obj5 = PIObjective(
        description="Exploratory API Gateway rate-limiting proof of concept",
        team_id=delta.id,
        pi_id=pi.id,
        planned_business_value=5,
        actual_business_value=None,
        is_stretch=True,
    )
    for obj in [obj1, obj2, obj3, obj4, obj5]:
        repos.objectives.save(obj)

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

    # --- PI 2026.2 (planning) ---
    j1 = Iteration(pi_id="", number=1, start_date=date(2026, 3, 30), end_date=date(2026, 4, 10))
    j2 = Iteration(pi_id="", number=2, start_date=date(2026, 4, 13), end_date=date(2026, 4, 24))
    j3 = Iteration(pi_id="", number=3, start_date=date(2026, 4, 27), end_date=date(2026, 5, 8))
    j4 = Iteration(pi_id="", number=4, start_date=date(2026, 5, 11), end_date=date(2026, 5, 22))
    jp = Iteration(
        pi_id="", number=5, start_date=date(2026, 5, 25), end_date=date(2026, 6, 5), is_ip=True
    )
    pi2 = PI(
        name="PI 2026.2",
        art_id=art.id,
        start_date=date(2026, 3, 30),
        end_date=date(2026, 6, 5),
        status=PIStatus.PLANNING,
        iteration_ids=[j1.id, j2.id, j3.id, j4.id, jp.id],
    )
    for it in [j1, j2, j3, j4, jp]:
        repos.iterations.save(it.model_copy(update={"pi_id": pi2.id}))
    repos.pis.save(pi2)

    # --- PI 2026.2 Features ---
    mobile_app = Feature(
        name="Mobile App MVP",
        pi_id=pi2.id,
        team_id=alpha.id,
        iteration_id=j1.id,
        user_business_value=9,
        time_criticality=8,
        risk_reduction_opportunity_enablement=3,
        job_size=5,
    )
    notifications = Feature(
        name="Notification Service",
        pi_id=pi2.id,
        team_id=beta.id,
        iteration_id=j1.id,
        user_business_value=6,
        time_criticality=5,
        risk_reduction_opportunity_enablement=4,
        job_size=3,
    )
    search = Feature(
        name="Search & Discovery",
        pi_id=pi2.id,
        team_id=gamma.id,
        iteration_id=j2.id,
        user_business_value=7,
        time_criticality=4,
        risk_reduction_opportunity_enablement=5,
        job_size=4,
    )
    user_profile = Feature(
        name="User Profile & Preferences",
        pi_id=pi2.id,
        team_id=alpha.id,
        iteration_id=j2.id,
        user_business_value=5,
        time_criticality=3,
        risk_reduction_opportunity_enablement=2,
        job_size=2,
    )
    billing = Feature(
        name="Billing & Subscriptions",
        pi_id=pi2.id,
        team_id=delta.id,
        iteration_id=j3.id,
        user_business_value=8,
        time_criticality=6,
        risk_reduction_opportunity_enablement=7,
        job_size=5,
    )
    for f in [mobile_app, notifications, search, user_profile, billing]:
        repos.features.save(f)

    # --- PI 2026.2 Stories ---
    pi2_stories = [
        story("App scaffolding", mobile_app.id, alpha.id, 3, j1.id),
        story("Auth integration", mobile_app.id, alpha.id, 3, j1.id),
        story("Offline mode", mobile_app.id, alpha.id, 3, j2.id),
        story("Email templates", notifications.id, beta.id, 3, j1.id),
        story("Push notifications", notifications.id, beta.id, 4, j1.id),
        story("Delivery tracking", notifications.id, beta.id, 2, j2.id),
        story("Search indexing", search.id, gamma.id, 5, j2.id),
        story("Faceted filters", search.id, gamma.id, 3, j2.id),
        story("Typeahead API", search.id, gamma.id, 2, j3.id),
        story("Profile CRUD", user_profile.id, alpha.id, 2, j2.id),
        story("Avatar upload", user_profile.id, alpha.id, 3, j2.id),
        story("Preferences API", user_profile.id, alpha.id, 3, j3.id),
        story("Payment gateway integration", billing.id, delta.id, 5, j3.id),
        story("Subscription tiers", billing.id, delta.id, 3, j3.id),
        story("Invoice generation", billing.id, delta.id, 3, j4.id),
    ]
    for s in pi2_stories:
        repos.stories.save(s)

    # --- PI 2026.2 Objectives ---
    for obj in [
        PIObjective(
            description="Ship Mobile App MVP to beta users",
            team_id=alpha.id,
            pi_id=pi2.id,
            planned_business_value=9,
        ),
        PIObjective(
            description="Launch Notification Service to all ART teams",
            team_id=beta.id,
            pi_id=pi2.id,
            planned_business_value=8,
        ),
        PIObjective(
            description="Enable full-text search across the platform",
            team_id=gamma.id,
            pi_id=pi2.id,
            planned_business_value=7,
        ),
        PIObjective(
            description="Explore billing automation proof of concept",
            team_id=delta.id,
            pi_id=pi2.id,
            planned_business_value=5,
            is_stretch=True,
        ),
    ]:
        repos.objectives.save(obj)

    # --- PI 2026.2 Risks ---
    for r in [
        Risk(
            description="Mobile SDK compatibility with older Android versions unverified",
            pi_id=pi2.id,
            team_id=alpha.id,
            owner="Alice",
        ),
        Risk(
            description="Payment gateway vendor contract not yet signed",
            pi_id=pi2.id,
            team_id=delta.id,
            owner="Dave",
            roam_status=ROAMStatus.OWNED,
        ),
    ]:
        repos.risks.save(r)

    # --- PI 2026.2 Dependencies ---
    for dep in [
        Dependency(
            description="Mobile App requires Notification Service push endpoint",
            pi_id=pi2.id,
            from_feature_id=mobile_app.id,
            to_feature_id=notifications.id,
            owner="Alice",
            needed_by_date=date(2026, 4, 10),
            status=DependencyStatus.IDENTIFIED,
        ),
        Dependency(
            description="Billing system requires User Profile service API",
            pi_id=pi2.id,
            from_feature_id=billing.id,
            to_feature_id=user_profile.id,
            owner="Dave",
            needed_by_date=date(2026, 4, 24),
            status=DependencyStatus.ACKNOWLEDGED,
        ),
    ]:
        repos.dependencies.save(dep)
