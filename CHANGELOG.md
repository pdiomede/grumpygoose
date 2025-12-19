# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md file to track project changes
- `generate_static.py` script to generate self-contained static HTML dashboard
- Static HTML generation with embedded CSS and data (no Flask server required)
- Timestamp display showing when the dashboard was last generated

### Changed
- Repository renamed from `goose` to `grumpygoose`
- Dashboard title updated from "GOOSE" to "THE GRUMPY GOOSE"

## [1.0.0] - Initial Release

### Added
- Flask-based dashboard for monitoring The Graph Council's responsiveness
- Snapshot proposal tracking for `council.graphprotocol.eth` space
- Safe multisig transaction tracking for Arbitrum address `0x8C6de8F8D562f3382417340A6994601eE08D3809`
- Time to quorum metrics (6 of 10 signatures)
- Individual council member response time tracking
- Participation leaderboard (top 10 most active members)
- Council member name resolution from CSV directory
- SQLite database for data persistence
- The Graph official branding and styling
- One-command setup script (`setup.py`)
- Documentation (README.md, PRD.md, agents.md, claude.md)

### Features
- Real-time dashboard displaying governance metrics
- Response time breakdown by platform (Snapshot vs Safe)
- Human-readable member identification format: "Name (0xab..cd)"
- Time format in days with decimal precision

[Unreleased]: https://github.com/pdiomede/grumpygoose/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pdiomede/grumpygoose/releases/tag/v1.0.0

