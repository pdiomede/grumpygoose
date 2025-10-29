"""
Snapshot Data Collector for GOOSE
Fetches proposals and votes from Snapshot GraphQL API
"""

import requests
from datetime import datetime
from config import SNAPSHOT_SPACE, SNAPSHOT_API_URL, QUORUM_THRESHOLD
from database import save_proposal, save_vote, save_member, get_connection


def fetch_proposals(limit=100):
    """Fetch proposals from Snapshot"""
    query = """
    query Proposals($space: String!, $first: Int!) {
      proposals(
        first: $first,
        where: { space: $space },
        orderBy: "created",
        orderDirection: desc
      ) {
        id
        title
        body
        start
        end
        state
        created
        author
        votes
      }
    }
    """

    variables = {
        "space": SNAPSHOT_SPACE,
        "first": limit
    }

    response = requests.post(
        SNAPSHOT_API_URL,
        json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("proposals", [])
    else:
        print(f"Error fetching proposals: {response.status_code}")
        return []


def fetch_votes_for_proposal(proposal_id):
    """Fetch all votes for a specific proposal"""
    query = """
    query Votes($proposal: String!) {
      votes(
        first: 1000,
        where: { proposal: $proposal }
      ) {
        id
        voter
        created
        choice
        vp
      }
    }
    """

    variables = {
        "proposal": proposal_id
    }

    response = requests.post(
        SNAPSHOT_API_URL,
        json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("votes", [])
    else:
        print(f"Error fetching votes for {proposal_id}: {response.status_code}")
        return []


def calculate_quorum_time(proposal_id, created_at):
    """Calculate when quorum was reached for a proposal"""
    votes = fetch_votes_for_proposal(proposal_id)

    if len(votes) < QUORUM_THRESHOLD:
        return None

    # Sort votes by timestamp
    sorted_votes = sorted(votes, key=lambda x: x['created'])

    # The time when the 6th vote was cast
    if len(sorted_votes) >= QUORUM_THRESHOLD:
        return sorted_votes[QUORUM_THRESHOLD - 1]['created']

    return None


def collect_snapshot_data():
    """Main function to collect all Snapshot data"""
    print("Fetching Snapshot proposals...")
    proposals = fetch_proposals()

    print(f"Found {len(proposals)} proposals")

    for proposal in proposals:
        print(f"Processing proposal: {proposal['title'][:50]}...")

        # Calculate quorum time
        quorum_time = calculate_quorum_time(proposal['id'], proposal['created'])

        # Save proposal
        proposal_data = {
            'id': proposal['id'],
            'title': proposal['title'],
            'created_at': proposal['created'],
            'start_time': proposal['start'],
            'end_time': proposal['end'],
            'state': proposal['state'],
            'quorum_reached_at': quorum_time
        }
        save_proposal(proposal_data)

        # Save author as member
        save_member(proposal['author'])

        # Fetch and save votes
        votes = fetch_votes_for_proposal(proposal['id'])
        for vote in votes:
            save_vote(
                item_id=proposal['id'],
                voter_address=vote['voter'],
                voted_at=vote['created'],
                platform='snapshot'
            )
            save_member(vote['voter'])

    print("Snapshot data collection complete!")


if __name__ == "__main__":
    from database import init_db
    init_db()
    collect_snapshot_data()
