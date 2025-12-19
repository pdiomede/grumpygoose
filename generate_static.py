"""
Generate static HTML dashboard for THE GRUMPY GOOSE
This script generates a self-contained HTML file with all data embedded
"""

import os
from datetime import datetime
from metrics import (
    get_time_to_quorum_stats,
    get_member_response_times,
    get_participation_rate,
    get_summary_stats
)
from database import get_member_display_name


def format_hours(hours):
    """Format hours to readable format"""
    if hours < 1:
        return f"{int(round(hours * 60))} min"
    elif hours < 24:
        return f"{hours:.1f}h"
    else:
        days = hours / 24
        return f"{days:.1f} days"


def read_css():
    """Read the CSS file"""
    css_path = os.path.join('static', 'style.css')
    with open(css_path, 'r') as f:
        return f.read()


def generate_html():
    """Generate static HTML with embedded data"""
    
    # Fetch all data
    print("Fetching data from database...")
    summary = get_summary_stats()
    quorum_all = get_time_to_quorum_stats()
    quorum_snapshot = get_time_to_quorum_stats(platform='snapshot')
    quorum_safe = get_time_to_quorum_stats(platform='safe')
    participation = get_participation_rate()
    response_times = get_member_response_times()
    
    # Create response time lookup
    response_dict = {member['address']: member for member in response_times}
    
    # Combine leaderboard data (top 10 by participation)
    leaderboard = []
    for member in participation[:10]:
        address = member['address']
        response_data = response_dict.get(address, {})
        
        leaderboard.append({
            'address': address,
            'display_name': get_member_display_name(address),
            'participation_rate': member['participation_rate'],
            'snapshot_votes': member['snapshot_votes'],
            'safe_votes': member['safe_votes'],
            'total_votes': member['total_votes'],
            'avg_response_time_hours': response_data.get('avg_response_time_hours', 0),
            'snapshot_response_time_hours': response_data.get('snapshot_response_time_hours'),
            'safe_response_time_hours': response_data.get('safe_response_time_hours')
        })
    
    # Read CSS
    css_content = read_css()
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE GRUMPY GOOSE 🪿 - Governance Oversight & Operational Speed Evaluator</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🪿 THE GRUMPY GOOSE</h1>
            <p class="subtitle">Governance Oversight & Operational Speed Evaluator</p>
            <p class="subtitle" style="font-size: 0.9em; margin-top: 10px; opacity: 0.7;">
                Last updated: {timestamp}
            </p>
        </header>

        <section class="summary-cards">
            <div class="card">
                <h3>Total Proposals</h3>
                <div class="stat">{summary['total_proposals']}</div>
            </div>
            <div class="card">
                <h3>Total Transactions</h3>
                <div class="stat">{summary['total_transactions']}</div>
            </div>
            <div class="card">
                <h3>Total Votes</h3>
                <div class="stat">{summary['total_votes']}</div>
            </div>
            <div class="card">
                <h3>Active Members</h3>
                <div class="stat">{summary['unique_voters']}</div>
            </div>
        </section>

        <section class="metrics-section">
            <h2>⏱️ Time to Quorum (6 of 10 signatures)</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>All Platforms</h4>
                    <div class="metric-stats">
"""
    
    # Add quorum stats for all platforms
    if quorum_all:
        html += f"""
                        <div class="metric-row">
                            <span>Average:</span>
                            <span class="value">{format_hours(quorum_all['avg'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Median:</span>
                            <span class="value">{format_hours(quorum_all['median'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Min:</span>
                            <span class="value">{format_hours(quorum_all['min'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Max:</span>
                            <span class="value">{format_hours(quorum_all['max'])}</span>
                        </div>
"""
    else:
        html += """
                        <div class="metric-row">
                            <span>No data available</span>
                        </div>
"""
    
    html += """
                    </div>
                </div>

                <div class="metric-card">
                    <h4>Snapshot</h4>
                    <div class="metric-stats">
"""
    
    # Add quorum stats for Snapshot
    if quorum_snapshot:
        html += f"""
                        <div class="metric-row">
                            <span>Average:</span>
                            <span class="value">{format_hours(quorum_snapshot['avg'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Median:</span>
                            <span class="value">{format_hours(quorum_snapshot['median'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Min:</span>
                            <span class="value">{format_hours(quorum_snapshot['min'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Max:</span>
                            <span class="value">{format_hours(quorum_snapshot['max'])}</span>
                        </div>
"""
    else:
        html += """
                        <div class="metric-row">
                            <span>No data available</span>
                        </div>
"""
    
    html += """
                    </div>
                </div>

                <div class="metric-card">
                    <h4>Safe Multisig</h4>
                    <div class="metric-stats">
"""
    
    # Add quorum stats for Safe
    if quorum_safe:
        html += f"""
                        <div class="metric-row">
                            <span>Average:</span>
                            <span class="value">{format_hours(quorum_safe['avg'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Median:</span>
                            <span class="value">{format_hours(quorum_safe['median'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Min:</span>
                            <span class="value">{format_hours(quorum_safe['min'])}</span>
                        </div>
                        <div class="metric-row">
                            <span>Max:</span>
                            <span class="value">{format_hours(quorum_safe['max'])}</span>
                        </div>
"""
    else:
        html += """
                        <div class="metric-row">
                            <span>No data available</span>
                        </div>
"""
    
    html += """
                    </div>
                </div>
            </div>

        </section>

        <section class="leaderboard-section">
            <h2>🏆 Leaderboard</h2>
            <div class="leaderboard">
"""
    
    # Add leaderboard items
    for index, member in enumerate(leaderboard):
        # Build response time breakdown
        response_breakdown = ''
        if member['snapshot_response_time_hours'] is not None and member['safe_response_time_hours'] is not None:
            response_breakdown = f'<div class="stat-breakdown">Snapshot: {format_hours(member["snapshot_response_time_hours"])} | Safe: {format_hours(member["safe_response_time_hours"])}</div>'
        elif member['snapshot_response_time_hours'] is not None:
            response_breakdown = f'<div class="stat-breakdown">Snapshot: {format_hours(member["snapshot_response_time_hours"])}</div>'
        elif member['safe_response_time_hours'] is not None:
            response_breakdown = f'<div class="stat-breakdown">Safe: {format_hours(member["safe_response_time_hours"])}</div>'
        
        top_three_class = 'top-three' if index < 3 else ''
        
        html += f"""
                <div class="leaderboard-item {top_three_class}">
                    <div class="rank">{index + 1}</div>
                    <div class="member-info">
                        <div class="address">{member['display_name']}</div>
                        <div class="details">
                            Snapshot: {member['snapshot_votes']} | Safe: {member['safe_votes']} | Total: {member['total_votes']}
                        </div>
                    </div>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Participation</div>
                            <div class="stat-value">{member['participation_rate']:.1f}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Avg Response</div>
                            <div class="stat-value">{format_hours(member['avg_response_time_hours'])}</div>
                            {response_breakdown}
                        </div>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </section>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Main function to generate and save static HTML"""
    print("=" * 60)
    print("🪿 THE GRUMPY GOOSE - Static HTML Generator")
    print("=" * 60)
    
    try:
        html_content = generate_html()
        
        # Write to index.html
        output_path = 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✓ Static HTML generated successfully!")
        print(f"  Output file: {output_path}")
        print(f"  File size: {len(html_content) / 1024:.1f} KB")
        print("\nYou can now serve this file with any static web server.")
        print("Example: python -m http.server 8080")
        
    except Exception as e:
        print(f"\n✗ Error generating static HTML: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

