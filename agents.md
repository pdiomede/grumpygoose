# GOOSE 🪿 - Agent Capabilities

## Overview

GOOSE is designed as a self-contained governance analytics tool that can be easily managed by autonomous agents. This document outlines the agent-friendly operations and automation capabilities.

## Agent-Managed Operations

### Data Collection Automation

#### Automated Refresh Process
```bash
# Full data refresh
python setup.py

# Individual platform updates
python collectors/snapshot.py
python collectors/safe.py

# Member name updates
python -c "from database import update_member_names; update_member_names()"
```

#### Scheduled Collection (Cron Jobs)
```bash
# Every 4 hours - Update all data
0 */4 * * * cd /path/to/goose && source venv/bin/activate && python setup.py

# Daily - Council member updates
0 9 * * * cd /path/to/goose && source venv/bin/activate && python -c "from database import update_member_names; update_member_names()"
```

### Monitoring & Alerting

#### Health Check Endpoints
- `GET /api/summary` - Verify data freshness and statistics
- `GET /api/time-to-quorum` - Check metrics calculation
- `GET /api/leaderboard` - Validate member data integration

#### Automated Health Monitoring
```python
import requests
import sys

def health_check():
    try:
        # Test API endpoints
        summary = requests.get('http://localhost:8080/api/summary', timeout=10)
        quorum = requests.get('http://localhost:8080/api/time-to-quorum', timeout=10)
        leaderboard = requests.get('http://localhost:8080/api/leaderboard', timeout=10)

        if summary.status_code == 200 and quorum.status_code == 200 and leaderboard.status_code == 200:
            data = summary.json()
            if data['total_votes'] > 0:  # Verify data exists
                return True, "All systems operational"
            else:
                return False, "No data in database"
        else:
            return False, "API endpoints not responding"
    except Exception as e:
        return False, f"Health check failed: {e}"

status, message = health_check()
if not status:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"OK: {message}")
```

### Database Management

#### Automated Backups
```bash
# Daily database backup
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp goose.db "$BACKUP_DIR/goose_backup_$TIMESTAMP.db"

# Keep last 7 days
find $BACKUP_DIR -name "goose_backup_*.db" -mtime +7 -delete
```

#### Database Restoration
```bash
# Restore from backup
cp /path/to/backups/goose_backup_YYYYMMDD_HHMMSS.db goose.db

# Full reset (caution: deletes all data)
rm goose.db
python database.py
python setup.py
```

### API Integration for External Agents

#### Metrics Export
```python
# Export data in JSON format for external processing
import requests
import json

# Get latest metrics
summary = requests.get('http://localhost:8080/api/summary').json()
quorum = requests.get('http://localhost:8080/api/time-to-quorum').json()
leaderboard = requests.get('http://localhost:8080/api/leaderboard').json()

# Combine for export
export_data = {
    "timestamp": datetime.now().isoformat(),
    "summary": summary,
    "quorum_metrics": quorum,
    "leaderboard": leaderboard
}

with open('goose_export.json', 'w') as f:
    json.dump(export_data, f, indent=2)
```

#### Data Push to External Systems
```python
# Push metrics to monitoring systems or dashboards
def push_metrics_to_monitoring(data):
    """Push metrics to external monitoring system"""
    # Example: Prometheus format
    metrics = []
    for member in data['leaderboard']:
        metrics.append(f"graph_council_participation_rate{{member=\"{member['display_name']}\"}} {member['participation_rate']}")
        metrics.append(f"graph_council_response_time{{member=\"{member['display_name']}\"}} {member['avg_response_time_hours']}")

    # Push to monitoring endpoint
    # requests.post('http://monitoring-system/api/metrics', data='\n'.join(metrics))
```

### Deployment & Scaling

#### Docker Containerization
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "app.py"]
```

#### Container Orchestration
```yaml
# docker-compose.yml
version: '3.8'
services:
  goose:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./goose.db:/app/goose.db
      - ./council_members.csv:/app/council_members.csv
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

## Autonomous Agent Capabilities

### Self-Healing Operations

#### Automatic Recovery from API Failures
```python
# Built into collectors - automatic retry logic
def fetch_with_retry(url, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 429:
                time.sleep(backoff_factor ** attempt)
                continue
            return response
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff_factor ** attempt)
```

#### Data Validation & Repair
```python
# Automatic data validation in metrics.py
def validate_metrics(data):
    """Validate metrics data for consistency"""
    if not data or len(data) == 0:
        raise ValueError("Empty metrics data")

    for item in data:
        if item['avg_response_time_hours'] < 0:
            raise ValueError(f"Negative response time: {item}")
        if item['participation_rate'] < 0 or item['participation_rate'] > 100:
            raise ValueError(f"Invalid participation rate: {item}")

    return True
```

### Configuration Management

#### Environment-Based Configuration
```python
# Supports configuration via environment variables
import os
from dotenv import load_dotenv

load_dotenv()

# Override config.py with environment variables
SNAPSHOT_SPACE = os.getenv('SNAPSHOT_SPACE', 'council.graphprotocol.eth')
SAFE_ADDRESS = os.getenv('SAFE_ADDRESS', '0x8C6de8F8D562f3382417340A6994601eE08D3809')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'goose.db')
```

## Agent Communication Protocol

### Standardized Responses
- **Success**: HTTP 200 with JSON data
- **Data Not Available**: HTTP 200 with empty arrays
- **Errors**: HTTP 5xx with error messages
- **Rate Limited**: HTTP 429 (automatic retry built-in)

### Data Formats
- All timestamps in ISO 8601 format
- Response times in decimal hours (backend) / days (frontend)
- Addresses in full format with checksums
- Percentages as decimal numbers (0-100)

## Security for Autonomous Operations

### API Rate Limiting
- Built-in exponential backoff for rate limit handling
- Configurable retry attempts and delays
- Graceful degradation when APIs are unavailable

### Data Integrity
- SQLite foreign key constraints
- Input validation for all API calls
- Backup and recovery procedures documented

## Performance Optimization

### Caching Strategy
- Council member names cached in memory
- Database connection pooling
- Efficient SQL queries with proper indexing

### Resource Management
- Lightweight Flask server (suitable for agent management)
- Minimal memory footprint (< 50MB typical)
- CPU usage minimal (data collection bursts only)

## Troubleshooting for Agents

### Common Issues & Solutions

#### API Rate Limits
```bash
# Symptom: 429 errors in logs
# Solution: Built-in retry logic, check collector output
python collectors/snapshot.py  # Monitor for retry patterns
```

#### Database Corruption
```bash
# Symptom: API returns empty data
# Solution: Reinitialize database
rm goose.db
python database.py
python setup.py
```

#### Council Member Updates
```bash
# Symptom: Names not showing in leaderboard
# Solution: Update member names
python -c "from database import update_member_names; update_member_names()"
```

## Log Management

#### Structured Logging
```python
import logging

# Configure agent-friendly logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('goose.log'),
        logging.StreamHandler()
    ]
)
```

#### Log Rotation
```bash
# Logrotate configuration
/path/to/goose/goose.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

This agent-centric design enables autonomous operation, monitoring, and maintenance of the GOOSE governance analytics system.