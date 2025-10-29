"""
Safe Multisig Data Collector for GOOSE
Fetches transactions and signatures from Safe Transaction Service API
"""

import requests
from datetime import datetime
from config import SAFE_ADDRESS, SAFE_API_URL, QUORUM_THRESHOLD
from database import save_transaction, save_vote, save_member, get_connection


def fetch_multisig_transactions(limit=100):
    """Fetch multisig transactions from Safe API"""
    url = f"{SAFE_API_URL}/safes/{SAFE_ADDRESS}/multisig-transactions/"

    params = {
        "limit": limit,
        "ordering": "-nonce"  # Most recent first
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"Error fetching transactions: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching Safe transactions: {e}")
        return []


def parse_timestamp(timestamp_str):
    """Convert ISO timestamp to Unix timestamp"""
    if not timestamp_str:
        return None
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except:
        return None


def calculate_quorum_time_safe(confirmations, submission_date):
    """Calculate when quorum was reached for a Safe transaction"""
    if len(confirmations) < QUORUM_THRESHOLD:
        return None

    # Sort confirmations by timestamp
    sorted_confirmations = sorted(
        confirmations,
        key=lambda x: parse_timestamp(x.get('submissionDate', submission_date)) or 0
    )

    # The time when the 6th confirmation was added
    if len(sorted_confirmations) >= QUORUM_THRESHOLD:
        quorum_confirmation = sorted_confirmations[QUORUM_THRESHOLD - 1]
        return parse_timestamp(quorum_confirmation.get('submissionDate', submission_date))

    return None


def collect_safe_data():
    """Main function to collect all Safe multisig data"""
    print("Fetching Safe multisig transactions...")
    transactions = fetch_multisig_transactions()

    print(f"Found {len(transactions)} transactions")

    for tx in transactions:
        safe_tx_hash = tx.get('safeTxHash')
        nonce = tx.get('nonce')
        submission_date = tx.get('submissionDate')
        execution_date = tx.get('executionDate')
        confirmations = tx.get('confirmations', [])

        print(f"Processing transaction nonce {nonce}...")

        # Calculate quorum time
        quorum_time = calculate_quorum_time_safe(confirmations, submission_date)

        # Save transaction
        tx_data = {
            'id': safe_tx_hash,
            'safe_tx_hash': safe_tx_hash,
            'created_at': parse_timestamp(submission_date),
            'executed_at': parse_timestamp(execution_date),
            'quorum_reached_at': quorum_time,
            'nonce': nonce
        }
        save_transaction(tx_data)

        # Save confirmations as votes
        for confirmation in confirmations:
            owner = confirmation.get('owner')
            submission = confirmation.get('submissionDate', submission_date)

            save_vote(
                item_id=safe_tx_hash,
                voter_address=owner,
                voted_at=parse_timestamp(submission),
                platform='safe'
            )
            save_member(owner)

    print("Safe data collection complete!")


if __name__ == "__main__":
    from database import init_db
    init_db()
    collect_safe_data()
