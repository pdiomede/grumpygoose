# GOOSE 🪿 - Claude Assistant Documentation

**Governance Oversight & Operational Speed Evaluator**

## Overview

GOOSE is a Python Flask dashboard that monitors and analyzes the responsiveness of The Graph Council members across Snapshot proposals and Safe multisig transactions.

## Architecture

### Backend Components

#### Core Files
- `app.py` - Main Flask application with API endpoints
- `config.py` - Configuration settings (API URLs, thresholds)
- `database.py` - SQLite database management and initialization
- `metrics.py` - Metrics calculation logic (response times, participation rates)

#### Data Collectors
- `collectors/snapshot.py` - Fetches proposals and votes from Snapshot GraphQL API
- `collectors/safe.py` - Fetches multisig transactions from Safe Transaction Service API

#### Council Management
- `council_lookup.py` - CSV-based council member name resolution
- `council_members.csv` - Council member directory with names and addresses
- `setup.py` - One-command database initialization and data collection

### Frontend Components
- `templates/index.html` - Single-page dashboard with no frameworks
- `static/style.css` - The Graph brand-compliant styling

## Data Flow

1. **Data Collection**: Snapshot & Safe APIs → SQLite database
2. **Metrics Calculation**: SQL queries → Response time & participation metrics
3. **API Layer**: Flask endpoints → JSON data for frontend
4. **Visualization**: HTML/CSS/JS → Interactive dashboard

## Key Features

### Time to Quorum Metrics
- Duration from proposal/transaction creation to 6th signature
- Platform-specific breakdowns (Snapshot vs Safe)
- Statistics: average, median, min, max

### Member Response Times
- Individual average response times
- Platform-specific breakdown
- Participation rate tracking

### Leaderboard
- Top 10 council members by participation
- Council names with formatted addresses
- Response time statistics

## Configuration

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and collect data
python setup.py

# Start dashboard
python app.py
```

### Key Settings (config.py)
- `SNAPSHOT_SPACE = "council.graphprotocol.eth"`
- `SAFE_ADDRESS = "0x8C6de8F8D562f3382417340A6994601eE08D3809"`
- `QUORUM_THRESHOLD = 6`
- `TOTAL_MEMBERS = 10`

## API Endpoints

- `GET /api/summary` - Overall statistics
- `GET /api/time-to-quorum` - Time to quorum metrics by platform
- `GET /api/leaderboard` - Top 10 council members with full metrics
- `GET /api/refresh` - Trigger manual data refresh

## Database Schema

### Tables
- `proposals` - Snapshot proposals with quorum tracking
- `transactions` - Safe multisig transactions
- `votes` - Individual votes/signatures across both platforms
- `members` - Council member information with names

## Brand Compliance

The dashboard follows The Graph brand guidelines:
- Colors: Graph Purple (#6F4CFF), Galaxy Dark (#0C0A1D), etc.
- Typography: Poppins font (alternative to Euclid Circular A)
- Visual style matching official branding

## Development Notes

### Dependencies
- **Flask 3.0.0** - Web framework
- **requests 2.31.0** - HTTP requests for API calls
- **python-dotenv 1.0.0** - Environment variable support
- **SQLite3** - Built-in database

### Testing
```bash
# Test individual components
python metrics.py                    # Test metrics calculation
python council_lookup.py            # Test council name resolution
python collectors/snapshot.py       # Test data collection
python collectors/safe.py          # Test safe data collection
```

## Performance

- Dashboard loads in < 2 seconds
- Data refresh on-demand (no real-time polling)
- Efficient SQL queries with indexed columns
- Static frontend with minimal JavaScript

## Security

- Read-only access to public APIs
- No user authentication required
- Local SQLite database storage
- No external dependencies on sensitive data

## Maintenance

- Run `python setup.py` to refresh all data
- Update `council_members.csv` when council membership changes
- Monitor API rate limits (429 errors from Snapshot)
- Regular database backups via `goose.db` file