# Flutter Web Pilot Runbook

## Scope

This runbook delivers the existing RecyclerOS RC1 Flutter path to Chris Hall's
iPhone through GitHub Pages. It does not create another vertical slice, embed a
credential, or authorize production or real customer data.

The login shell is public at:

`https://cmhall6117-jpg.github.io/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/`

Authentication, tenant membership, and every tenant-owned mutation remain
enforced by the Railway API. The bearer token is held only in the running app's
memory and is discarded when the page is closed or refreshed.

## Deployment Controls

- `.github/workflows/flutter-pilot-web.yml` builds from `main` only.
- The Railway API URL and Pages URL come from the credential-free pilot contract.
- The build receives no GitHub or Railway secret.
- Railway allows browser requests only from
  `https://cmhall6117-jpg.github.io`.
- The Pages artifact is scanned for password environment names and PostgreSQL
  connection strings before deployment.
- Pull requests upload a seven-day build artifact but cannot deploy Pages.

## Preflight

1. Confirm the Flutter Pilot Web workflow passed for the deployed commit.
2. Confirm the Pages URL uses HTTPS and loads the RecyclerOS Pro sign-in view.
3. Confirm Railway liveness and readiness return HTTP 200.
4. Confirm an OPTIONS request from the exact Pages origin is allowed.
5. Confirm an OPTIONS request from an unrelated origin is rejected.
6. Retrieve the operator credential from the approved password manager. Do not
   paste it into chat, screenshots, source control, or defect evidence.

### Deployed Build Freshness

If an expected control is missing after a successful Pages deployment, first
verify the public `main.dart.js` returns HTTP 200 and contains a marker unique to
the deployed feature. On Safari, remove website data only for
`cmhall6117-jpg.github.io`, fully close Safari, and reopen the Pages URL with a
commit-specific query value. Sign in again before continuing the test.

Clearing website data or closing the old tab discards the in-memory client token
but does not prove that the old server session was revoked. Perform the logout
acceptance step from the newly authenticated session.

## iPhone Field Session

Use Safari on Chris Hall's approved iPhone. Private Browsing remains acceptable,
but the deployed RC1 client must provide a server-revoking Sign out command.

The RC1 browser session is held in memory. If iOS reloads or evicts the tab, the
app must return to sign-in. Sign in and select the workspace again; do not enter
operational data into a form that reopened without those steps.

1. Open the Pages URL and confirm the address bar shows HTTPS.
2. Sign in as `operator@effortlesssmoke.com` with the sealed operator password.
3. Select the Effortless Smoke organization and Local Operations workspace.
4. Open Mission Control.
5. Create an opportunity labeled `IPHONE-PILOT-<date-time>` with synthetic data.
6. Create the vehicle record.
7. Review all three procurement scenarios.
8. Add the vehicle to the pick list and mark it available.
9. Start and complete Focus Point using synthetic part selections.
10. Complete inventory intake with a synthetic storage location.
11. Record the created opportunity, vehicle, and inventory codes.
12. Return to Mission Control and use Sign out.
13. Confirm the app returns to Sign in and does not reopen an operational screen
    when using browser back navigation.
14. Close the Safari tab and clear the site data after evidence is captured.

Do not use a real VIN, customer identity, payment detail, shipment, marketplace
credential, SSO credential, or AI credential.

## Evidence

Record the following without showing the password or browser authorization
header:

- device model and iOS version
- Pages workflow run and deployed Git commit
- session start and completion timestamps
- tenant organization and workspace names
- synthetic opportunity, vehicle, and inventory codes
- result of each working-path step
- successful Sign out and return to the Sign in screen
- screenshots after login with any sensitive fields excluded
- defects with screen, action, expected result, and observed result

`DEF-RAILWAY-006` was closed on August 28, 2026 after the stage evidence, logout
implementation CI, Pages deployment, and iPhone Sign out result were committed
for review. Repeat this runbook for future release candidates; its completion
does not authorize a second tester or production traffic.

## Rollback

1. Disable the GitHub Pages deployment or restore its last known-good artifact.
2. Remove the Pages origin from `RECYCLEROS_CORS_ORIGINS` in Railway if browser
   access must be closed.
3. Confirm unrelated browser origins remain rejected.
4. Keep the Railway API and PostgreSQL volume intact unless a separate rollback
   or recovery change is approved.
