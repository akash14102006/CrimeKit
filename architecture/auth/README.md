# Authentication & Authorization — Design Scaffold

Purpose
-------
Scaffold and rationale for authentication, authorization, and identity management for CrimeKit.

Goals
-----
- Secure authentication (OAuth2 / OpenID Connect patterns) for machine and human actors.
- Short-lived access tokens + refresh tokens.
- Central RBAC and attribute-based access controls for case/evidence resources.
- Audit trails for authentication events and administrative actions.
- Support for SSO (SAML/OIDC) for government integrations.

Recommended patterns
--------------------
- Use a proven identity provider for production (Auth0, Azure AD, Keycloak), with a fallback self-hosted option (Keycloak).
- Token strategy: JWT access tokens (short TTL, e.g., 5–15 min) + refresh tokens stored in secure DB or KMS-encrypted store and rotated.
- Passwords: store bcrypt/argon2 hashed passwords; enforce MFA for privileged roles.
- RBAC: `roles` table + `permissions` mapping. Use middleware to enforce permissions on APIs.

Flows
-----
1. User login (OIDC/SAML preferred) — create user record on first login, map groups to roles.
2. Machine-to-machine (M2M) — client credentials flow with scoped API keys and rotation.
3. Session refresh — refresh token rotation and revocation list.
4. Admin actions — require elevated tokens and event logging.

Security & Compliance
---------------------
- Enforce least privilege.  
- All tokens and secrets in a secrets manager (Vault/KeyVault/Secret Manager).  
- All auth events (login, failed login, token revoke) must be forwarded to audit logs and SIEM.  

Integrations
------------
- Identity: OIDC / SAML connectors to government IdP (per agency).  
- MFA: integrate with TOTP or hardware tokens for sensitive roles.  
- Compliance: map PII handling requirements into DB encryption-at-rest and field-level encryption when required.

Next steps (scaffolded files in repo)
------------------------------------
- `api/openapi/auth.yaml` — OpenAPI skeleton for auth endpoints.
- `db/schema/postgres/schema.sql` — canonical schema draft (users, roles, cases, evidence) including pgvector extension for AI features.
- `migrations/README.md` — migration tooling guidance (Alembic/Flyway placeholders).

Owners
------
Auth team, Security, and DB team must review and approve before implementation.
