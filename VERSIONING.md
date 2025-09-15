# Field Station - Versioning Guide

## Current Version: v0.1

## Versioning Strategy

Field Station follows **Semantic Versioning** (SemVer) with the format `MAJOR.MINOR.PATCH`:

### Version Number Meaning

- **MAJOR** (X.0.0): Breaking changes or milestone releases
- **MINOR** (0.X.0): New features, backwards compatible  
- **PATCH** (0.0.X): Bug fixes, small tweaks

### Development Phases

#### Pre-1.0 (Development Phase)
- **v0.1**: Basic playable prototype with core farming mechanics
- **v0.2**: Major feature addition (weather system, new crops, etc.)
- **v0.3**: Another major feature (market expansion, achievements, etc.)
- **v0.4+**: Continue adding planned features

#### 1.0+ (Stable Release Phase)
- **v1.0.0**: First stable, feature-complete public release
- **v1.1.0**: New features added to stable base
- **v1.0.1**: Bug fixes to stable release

## When to Increment Versions

### Patch Version (0.1.0 → 0.1.1)
- Bug fixes
- UI/UX improvements
- Performance optimizations
- Balance adjustments
- No new features

### Minor Version (0.1.0 → 0.2.0)
- New crops or farming mechanics
- New game systems (weather, seasons, etc.)
- New UI screens or major interface changes
- Save file format changes (with backward compatibility)

### Major Version (0.9.0 → 1.0.0)
- First stable public release
- Breaking changes to save file format
- Complete rewrites or architecture changes
- Removal of major features

## Red Flags for v1.0

Don't release v1.0 if:
- Core features are still being added
- Major bugs remain unfixed
- Save file format changes frequently
- No public testing has occurred
- Documentation is incomplete

## Version Release Checklist

Before incrementing version:
- [ ] Update version in all relevant files
- [ ] Test save file compatibility
- [ ] Update documentation
- [ ] Run full test suite
- [ ] Update changelog/release notes

## File Locations to Update

When changing versions, update these files:
- `field_station.py` (UI display and save format)
- `field-station.desktop` (launcher version)
- `README.md` (current version display)
- Documentation headers (*.md files)
- HTML mockups (if applicable)