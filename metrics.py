"""
Metrics calculation for GOOSE
Computes time to quorum, individual response times, and participation rates
"""

import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH, QUORUM_THRESHOLD
from database import get_connection


def get_time_to_quorum_stats(platform=None, days=None):
    """
    Calculate time to quorum statistics
    Returns: dict with avg, median, min, max in hours
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build query based on platform
    if platform == 'snapshot':
        table = 'proposals'
        time_filter = ""
        if days:
            cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
            time_filter = f"AND created_at >= {cutoff}"

        query = f"""
            SELECT
                (quorum_reached_at - created_at) as time_to_quorum
            FROM proposals
            WHERE quorum_reached_at IS NOT NULL
            {time_filter}
        """
    elif platform == 'safe':
        table = 'transactions'
        time_filter = ""
        if days:
            cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
            time_filter = f"AND created_at >= {cutoff}"

        query = f"""
            SELECT
                (quorum_reached_at - created_at) as time_to_quorum
            FROM transactions
            WHERE quorum_reached_at IS NOT NULL
            {time_filter}
        """
    else:
        # Both platforms
        time_filter_snapshot = ""
        time_filter_safe = ""
        if days:
            cutoff = int((datetime.now() - timedelta(days=days)).timestamp())
            time_filter_snapshot = f"AND created_at >= {cutoff}"
            time_filter_safe = f"AND created_at >= {cutoff}"

        query = f"""
            SELECT time_to_quorum FROM (
                SELECT (quorum_reached_at - created_at) as time_to_quorum
                FROM proposals
                WHERE quorum_reached_at IS NOT NULL
                {time_filter_snapshot}
                UNION ALL
                SELECT (quorum_reached_at - created_at) as time_to_quorum
                FROM transactions
                WHERE quorum_reached_at IS NOT NULL
                {time_filter_safe}
            )
        """

    cursor.execute(query)
    times = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not times:
        return None

    # Convert to hours
    times_hours = [t / 3600 for t in times]
    times_hours.sort()

    stats = {
        'avg': sum(times_hours) / len(times_hours),
        'median': times_hours[len(times_hours) // 2],
        'min': min(times_hours),
        'max': max(times_hours),
        'count': len(times_hours)
    }

    return stats


def get_member_response_times():
    """
    Calculate average response time for each member
    Returns: list of dicts with member address, avg response time (overall and by platform), participation count
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get response times from Snapshot
    cursor.execute("""
        SELECT
            v.voter_address,
            AVG(v.voted_at - p.created_at) as avg_response_time,
            COUNT(*) as vote_count
        FROM votes v
        JOIN proposals p ON v.item_id = p.id
        WHERE v.platform = 'snapshot'
        GROUP BY v.voter_address
    """)
    snapshot_data = {row[0]: {'response_time': row[1], 'count': row[2]} for row in cursor.fetchall()}

    # Get response times from Safe
    cursor.execute("""
        SELECT
            v.voter_address,
            AVG(v.voted_at - t.created_at) as avg_response_time,
            COUNT(*) as vote_count
        FROM votes v
        JOIN transactions t ON v.item_id = t.id
        WHERE v.platform = 'safe'
        GROUP BY v.voter_address
    """)
    safe_data = {row[0]: {'response_time': row[1], 'count': row[2]} for row in cursor.fetchall()}

    # Combine data
    all_members = set(list(snapshot_data.keys()) + list(safe_data.keys()))
    member_stats = []

    for member in all_members:
        snapshot_time = snapshot_data.get(member, {}).get('response_time', 0)
        snapshot_count = snapshot_data.get(member, {}).get('count', 0)
        safe_time = safe_data.get(member, {}).get('response_time', 0)
        safe_count = safe_data.get(member, {}).get('count', 0)

        total_time = (snapshot_time * snapshot_count + safe_time * safe_count)
        total_count = snapshot_count + safe_count

        avg_time = total_time / total_count if total_count > 0 else 0

        member_stats.append({
            'address': member,
            'avg_response_time_hours': avg_time / 3600,
            'snapshot_response_time_hours': snapshot_time / 3600 if snapshot_time else None,
            'safe_response_time_hours': safe_time / 3600 if safe_time else None,
            'snapshot_votes': snapshot_count,
            'safe_votes': safe_count,
            'total_votes': total_count
        })

    conn.close()

    # Sort by average response time (fastest first)
    member_stats.sort(key=lambda x: x['avg_response_time_hours'])

    return member_stats


def get_participation_rate():
    """
    Calculate participation rate for each member
    Returns: list of dicts with member address, participation rate, and vote counts
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Total number of proposals
    cursor.execute("SELECT COUNT(*) FROM proposals")
    total_proposals = cursor.fetchone()[0]

    # Total number of transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]

    total_items = total_proposals + total_transactions

    if total_items == 0:
        return []

    # Get vote counts per member
    cursor.execute("""
        SELECT
            voter_address,
            SUM(CASE WHEN platform = 'snapshot' THEN 1 ELSE 0 END) as snapshot_votes,
            SUM(CASE WHEN platform = 'safe' THEN 1 ELSE 0 END) as safe_votes,
            COUNT(*) as total_votes
        FROM votes
        GROUP BY voter_address
    """)

    member_stats = []
    for row in cursor.fetchall():
        address = row[0]
        snapshot_votes = row[1]
        safe_votes = row[2]
        total_votes = row[3]

        participation_rate = (total_votes / total_items) * 100

        member_stats.append({
            'address': address,
            'participation_rate': participation_rate,
            'snapshot_votes': snapshot_votes,
            'safe_votes': safe_votes,
            'total_votes': total_votes,
            'total_items': total_items
        })

    conn.close()

    # Sort by participation rate (highest first)
    member_stats.sort(key=lambda x: x['participation_rate'], reverse=True)

    return member_stats


def get_time_series_data(days=90, interval='week'):
    """
    Get time series data for time to quorum over a period
    Returns: list of dicts with timestamp and avg time to quorum
    """
    conn = get_connection()
    cursor = conn.cursor()

    cutoff = int((datetime.now() - timedelta(days=days)).timestamp())

    if interval == 'day':
        grouping = 86400  # 1 day in seconds
    elif interval == 'week':
        grouping = 604800  # 1 week in seconds
    else:  # month
        grouping = 2592000  # 30 days in seconds

    query = f"""
        SELECT
            (created_at / {grouping}) * {grouping} as period,
            AVG(quorum_reached_at - created_at) as avg_time_to_quorum,
            COUNT(*) as count
        FROM (
            SELECT created_at, quorum_reached_at
            FROM proposals
            WHERE quorum_reached_at IS NOT NULL AND created_at >= {cutoff}
            UNION ALL
            SELECT created_at, quorum_reached_at
            FROM transactions
            WHERE quorum_reached_at IS NOT NULL AND created_at >= {cutoff}
        )
        GROUP BY period
        ORDER BY period
    """

    cursor.execute(query)
    data = []
    for row in cursor.fetchall():
        data.append({
            'timestamp': row[0],
            'date': datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d'),
            'avg_hours': row[1] / 3600,
            'count': row[2]
        })

    conn.close()
    return data


def get_summary_stats():
    """Get overall summary statistics"""
    conn = get_connection()
    cursor = conn.cursor()

    # Total proposals
    cursor.execute("SELECT COUNT(*) FROM proposals")
    total_proposals = cursor.fetchone()[0]

    # Total transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]

    # Total votes
    cursor.execute("SELECT COUNT(*) FROM votes")
    total_votes = cursor.fetchone()[0]

    # Unique voters
    cursor.execute("SELECT COUNT(DISTINCT voter_address) FROM votes")
    unique_voters = cursor.fetchone()[0]

    conn.close()

    return {
        'total_proposals': total_proposals,
        'total_transactions': total_transactions,
        'total_items': total_proposals + total_transactions,
        'total_votes': total_votes,
        'unique_voters': unique_voters
    }


if __name__ == "__main__":
    # Test metrics
    print("=== Time to Quorum Stats ===")
    stats = get_time_to_quorum_stats()
    if stats:
        print(f"Average: {stats['avg']:.2f} hours")
        print(f"Median: {stats['median']:.2f} hours")
        print(f"Min: {stats['min']:.2f} hours")
        print(f"Max: {stats['max']:.2f} hours")

    print("\n=== Member Response Times ===")
    members = get_member_response_times()
    for m in members[:5]:
        print(f"{m['address'][:10]}... - {m['avg_response_time_hours']:.2f} hours")

    print("\n=== Participation Rates ===")
    participation = get_participation_rate()
    for p in participation[:5]:
        print(f"{p['address'][:10]}... - {p['participation_rate']:.1f}%")
