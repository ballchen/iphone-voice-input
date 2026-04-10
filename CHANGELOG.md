# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-04-10

### Fixed
- mobile keyboard UX on iPhone: action bar now stays visible above the keyboard
- improved viewport handling with `visualViewport` updates and focus visibility behavior

## [1.0.9] - 2026-04-10

### Fixed
- stabilized Win32 input APIs with stricter ctypes signatures and structures
- improved clipboard reliability and added PowerShell clipboard fallback
- reduced unintended fallback to key-by-key typing under IME-sensitive scenarios

## [1.0.8] - 2026-04-10

### Changed
- prioritized forced paste input path before lower-level key injection fallbacks
- added runtime logging for which input method was used

## [1.0.7] - 2026-04-09

### Fixed
- added Unicode `SendInput` path to bypass active IME key mapping where possible

## [1.0.6] - 2026-04-09

### Fixed
- introduced IME-safe clipboard paste strategy with fallback handling

## [1.0.5] - 2026-04-09

### Fixed
- bundled Socket.IO client script locally to avoid loader/runtime mismatch
- fixed frontend initialization order bug causing client runtime errors

## [1.0.4] - 2026-04-09

### Fixed
- improved Socket.IO client connection compatibility and stale PWA cache behavior

## [1.0.3] - 2026-04-09

### Fixed
- hardened local server startup diagnostics and error visibility
- added log folder and local test page shortcuts

## [1.0.2] - 2026-04-09

### Fixed
- improved LAN URL detection for multi-NIC environments
- added multi-URL QR and copy actions for easier mobile connection troubleshooting

## [1.0.1] - 2026-04-09

### Fixed
- fixed packaged EXE startup issue caused by missing Engine.IO threading driver

## [1.0.0] - 2026-04-09

### Added
- initial Windows release packaging workflow with GitHub Releases ZIP assets
