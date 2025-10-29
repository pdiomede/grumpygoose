"""
Database setup and management for GOOSE
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Proposals table (Snapshot)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at INTEGER,
            start_time INTEGER,
            end_time INTEGER,
            state TEXT,
            quorum_reached_at INTEGER,
            platform TEXT DEFAULT 'snapshot'
        )
    """)

    # Transactions table (Safe)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            safe_tx_hash TEXT UNIQUE,
            created_at INTEGER,
            executed_at INTEGER,
            quorum_reached_at INTEGER,
            nonce INTEGER,
            platform TEXT DEFAULT 'safe'
        )
    """)

    # Votes table (for both Snapshot votes and Safe signatures)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            voter_address TEXT,
            voted_at INTEGER,
            platform TEXT,
            UNIQUE(item_id, voter_address, platform)
        )
    """)

    # Members table (to track council members)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            address TEXT PRIMARY KEY,
            ens_name TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully")


def get_connection():
    """Get a database connection"""
    return sqlite3.connect(DATABASE_PATH)


def save_proposal(proposal_data):
    """Save a Snapshot proposal to the database"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO proposals
        (id, title, created_at, start_time, end_time, state, quorum_reached_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        proposal_data['id'],
        proposal_data['title'],
        proposal_data['created_at'],
        proposal_data['start_time'],
        proposal_data['end_time'],
        proposal_data['state'],
        proposal_data.get('quorum_reached_at')
    ))

    conn.commit()
    conn.close()


def save_transaction(tx_data):
    """Save a Safe transaction to the database"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO transactions
        (id, safe_tx_hash, created_at, executed_at, quorum_reached_at, nonce)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        tx_data['id'],
        tx_data['safe_tx_hash'],
        tx_data['created_at'],
        tx_data.get('executed_at'),
        tx_data.get('quorum_reached_at'),
        tx_data['nonce']
    ))

    conn.commit()
    conn.close()


def save_vote(item_id, voter_address, voted_at, platform):
    """Save a vote or signature"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO votes
            (item_id, voter_address, voted_at, platform)
            VALUES (?, ?, ?, ?)
        """, (item_id, voter_address, voted_at, platform))

        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Vote already exists
    finally:
        conn.close()


def save_member(address, ens_name=None):
    """Save or update a council member"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO members (address, ens_name)
        VALUES (?, ?)
    """, (address, ens_name))

    conn.commit()
    conn.close()


def update_member_names():
    """Update database with council member names from CSV"""
    import council_lookup
    return council_lookup.update_member_names_in_db()


def get_member_display_name(address):
    """Get formatted display name for a member address"""
    import council_lookup
    return council_lookup.format_member_name(address)


if __name__ == "__main__":
    init_db()
