# 🪿 THE GRUMPY GOOSE
**Governance Oversight & Operational Speed Evaluator**

A lightweight static dashboard for monitoring The Graph Council's responsiveness across Snapshot proposals and Safe multisig transactions.

## 📋 Overview

THE GRUMPY GOOSE tracks how quickly The Graph Council reaches quorum (6 of 10 signatures) and measures individual member response times. The dashboard displays time to quorum metrics, participation rates, and response times with council member names.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database and collect data
python setup.py

# Generate static HTML dashboard
python generate_static.py
```

Open **index.html** in your browser to view the dashboard.

## 📊 Key Features

- **Time to Quorum**: Track how long proposals/transactions take to reach 6 signatures
- **Response Times**: Individual member speed metrics with platform breakdown
- **Participation Leaderboard**: Top 10 most active council members
- **Council Names**: Human-readable member identification from CSV directory
- **The Graph Branding**: Official colors, typography, and design guidelines

## 📈 Metrics Tracked

- **Snapshot Proposals**: `council.graphprotocol.eth` space
- **Safe Multisig**: Arbitrum one address `0x8C6de8F8D562f3382417340A6994601eE08D3809`
- **Time Format**: Days with decimal precision (e.g., "8.5 days")
- **Member Display**: "Name (0xab..cd)" format

## 🛠️ Tech Stack

- **Backend**: Python + SQLite
- **Frontend**: Static HTML/CSS (self-contained, no server required)
- **Data APIs**: Snapshot GraphQL, Safe Transaction Service
- **Branding**: The Graph official brand guidelines

## 📁 Project Structure

```
grumpygoose/
├── generate_static.py    # Static HTML generator
├── config.py             # Configuration settings
├── database.py           # Database management
├── metrics.py            # Metrics calculations
├── council_lookup.py     # Council member name resolution
├── council_members.csv   # Council directory
├── collectors/
│   ├── snapshot.py      # Snapshot data collector
│   └── safe.py          # Safe multisig collector
├── static/
│   └── style.css        # The Graph branding
├── setup.py             # One-command setup
└── index.html           # Generated static dashboard
```

## 📚 Documentation

- **[CLAUDE.md](./claude.md)** - Architecture and development documentation
- **[AGENTS.md](./agents.md)** - Agent operations and automation guide

## 🔧 Configuration

Edit `config.py` to customize:
- Snapshot space and Safe multisig address
- Quorum threshold (default: 6 of 10)
- Database path and API endpoints

## 📝 License

Made with 🪿 for The Graph Council governance oversight.