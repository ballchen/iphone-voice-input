# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- no unreleased changes yet

## [1.1.1] - 2026-04-10

### Changed
- cleaned up documentation structure by moving version history details into this changelog
- simplified `README.md` and `WINDOWS_INSTALL_GUIDE.md` to focus on current usage and troubleshooting

## [1.1.0] - 2026-04-10

### Fixed
- fixed iPhone keyboard UX so action buttons stay visible above the software keyboard
- improved mobile viewport handling with `visualViewport` updates and focus visibility behavior

## [1.0.9] - 2026-04-10

### Fixed
- stabilized Win32 input APIs with stricter ctypes signatures and structure mappings
- improved clipboard reliability and added PowerShell clipboard fallback
- reduced unintended fallback to key-by-key typing under IME-sensitive scenarios

## [1.0.8] - 2026-04-10

### Changed
- prioritized forced paste input path before lower-level key injection fallbacks
- added runtime logging for selected input method

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

[Unreleased]: https://github.com/ballchen/iphone-voice-input/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/ballchen/iphone-voice-input/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.9...v1.1.0
[1.0.9]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.8...v1.0.9
[1.0.8]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.7...v1.0.8
[1.0.7]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/ballchen/iphone-voice-input/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ballchen/iphone-voice-input/releases/tag/v1.0.0
