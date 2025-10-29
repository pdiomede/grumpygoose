"""
GOOSE Flask Application
Simple web dashboard for governance metrics
"""

from flask import Flask, render_template, jsonify
from metrics import (
    get_time_to_quorum_stats,
    get_member_response_times,
    get_participation_rate,
    get_time_series_data,
    get_summary_stats
)
from database import get_member_display_name

app = Flask(__name__)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/summary')
def api_summary():
    """Get summary statistics"""
    return jsonify(get_summary_stats())


@app.route('/api/time-to-quorum')
def api_time_to_quorum():
    """Get time to quorum statistics"""
    stats_all = get_time_to_quorum_stats()
    stats_snapshot = get_time_to_quorum_stats(platform='snapshot')
    stats_safe = get_time_to_quorum_stats(platform='safe')

    return jsonify({
        'all': stats_all,
        'snapshot': stats_snapshot,
        'safe': stats_safe
    })


@app.route('/api/response-times')
def api_response_times():
    """Get member response times"""
    return jsonify(get_member_response_times())


@app.route('/api/participation')
def api_participation():
    """Get participation rates - top 10"""
    participation = get_participation_rate()
    return jsonify(participation[:10])  # Top 10 only


@app.route('/api/leaderboard')
def api_leaderboard():
    """Get combined leaderboard with participation and response times"""
    participation = get_participation_rate()
    response_times = get_member_response_times()

    # Create a dict for quick lookup of response times
    response_dict = {member['address']: member for member in response_times}

    # Combine the data
    combined = []
    for member in participation[:10]:  # Top 10 by participation
        address = member['address']
        response_data = response_dict.get(address, {})

        combined.append({
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

    return jsonify(combined)


@app.route('/api/refresh')
def api_refresh():
    """Trigger data refresh"""
    # Import collectors
    from collectors.snapshot import collect_snapshot_data
    from collectors.safe import collect_safe_data

    try:
        collect_snapshot_data()
        collect_safe_data()
        return jsonify({'status': 'success', 'message': 'Data refreshed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
