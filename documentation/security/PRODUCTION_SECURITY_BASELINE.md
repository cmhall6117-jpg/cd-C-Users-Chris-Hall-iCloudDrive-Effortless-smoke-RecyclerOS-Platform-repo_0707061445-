# Production Security Baseline

## Runtime Controls

- API runs as the non-root `recycleros` user.
- Filesystem is read-only with a bounded temporary filesystem.
- Linux capabilities are dropped and privilege escalation is disabled.
- API is loopback-bound behind an independently managed TLS reverse proxy.
- Proxy addresses and trusted hostnames must be exact; wildcards fail startup.
- Browser origins must be exact HTTPS origins; origin regex access is disabled.
- Interactive API docs and OpenAPI discovery are disabled in production.
- API responses set HSTS, no-store, no-referrer, no-sniff, and frame-deny headers.
- Production startup requires durable PostgreSQL, an exact release SHA, and at
  least one active tenant membership before readiness succeeds.

## Identity And Secrets

- Runtime database credentials are mounted from a secret file and never baked
  into the image or release manifest.
- The first owner is created only by an explicit, confirmed, audited one-shot
  command. The bootstrap password is not mounted into API containers.
- Opaque session digests, expiry, revocation, login throttling, tenant
  memberships, and auth audit events are durable in PostgreSQL.
- Tenant permissions come from server-owned membership records; supplied role
  claims are ignored.

## Release And Data Controls

- Deployment requires an image repository plus immutable SHA-256 digest.
- OCI image metadata records the source commit.
- The release manifest ties commit, image digest, and all migration checksums.
- Applied migration checksums are durable and drift causes migration failure.
- Restore requires an exact database confirmation; production restore also
  requires the matching backup checksum manifest.

## External Controls Required Before Launch

The repository does not provide cloud IAM, registry signing, a WAF, managed TLS,
central logs, alert delivery, database encryption policy, point-in-time recovery,
secret rotation, vulnerability management, legal approval, or on-call staffing.
Each must be configured and evidenced in the target production environment.

Live SSO, payment, marketplace, shipping, and AI credentials remain outside RC1
scope and must not be enabled as part of production preparation.
