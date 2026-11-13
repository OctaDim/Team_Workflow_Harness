# Actual state

Establish relevant requested conditions; verify actual:
- Service worker/cache: identify participation. Fresh-load checks need fresh
  conditions; update/offline/cache tests retain required mechanisms. No
  unconditional unregister/clear.
- Storage: establish relevant keys/values; distinguish defaults from persistence.
  Do not reset between steps testing preservation.
- Theme: account for system preference/app overrides; check effective styles/state.
  Flags/media preference alone prove no applied theme.
- Viewport: measure actual page width/height, scale when material; window/mobile
  flags are insufficient.

Reset only necessary authorized test state, never user/other-run data automatically.
Mismatches leave the claimed scenario unverified; classify cause separately.
