"""
Council Member Lookup
Handles loading and mapping council member names from CSV
"""

import csv
import os

# Cache for council member data
_council_cache = None


def load_council_members():
    """Load council members from CSV file"""
    global _council_cache

    if _council_cache is not None:
        return _council_cache

    members = {}
    csv_path = os.path.join(os.path.dirname(__file__), 'council_members.csv')

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('Name', '').strip()
                address = row.get('Address', '').strip()
                ens = row.get('ENS', '').strip()
                status = row.get('Status', '').strip()

                if not name or not address:
                    continue

                # Clean address (remove network prefixes if present)
                if ':' in address:
                    address = address.split(':')[1]

                # Normalize address (lowercase for consistency)
                address = address.lower()

                members[address] = {
                    'name': name,
                    'ens': ens,
                    'status': status
                }

        _council_cache = members
        print(f"Loaded {len(members)} council members from CSV")

    except FileNotFoundError:
        print("Council members CSV file not found")
        _council_cache = {}
    except Exception as e:
        print(f"Error loading council members: {e}")
        _council_cache = {}

    return _council_cache


def get_member_info(address):
    """Get member info for a given address"""
    if not address:
        return None

    # Normalize address for lookup
    lookup_address = address.lower()

    members = load_council_members()
    return members.get(lookup_address)


def format_member_name(address):
    """Format member display name as 'Name (0xab..xyz)'"""
    member_info = get_member_info(address)

    if member_info and member_info['name']:
        name = member_info['name']
        short_address = f"{address[:6]}...{address[-4:]}"
        return f"{name} ({short_address})"
    else:
        # Fallback to short address only
        return f"{address[:6]}...{address[-4:]}"


def update_member_names_in_db():
    """Update database with council member names"""
    import database
    from database import get_connection

    members = load_council_members()
    conn = get_connection()
    cursor = conn.cursor()

    updated_count = 0
    for address, info in members.items():
        # Use the full address as stored in the database
        full_address = address
        cursor.execute("""
            INSERT OR REPLACE INTO members (address, ens_name)
            VALUES (?, ?)
        """, (full_address, info['ens'] if info['ens'] else info['name']))
        updated_count += 1

    conn.commit()
    conn.close()

    print(f"Updated {updated_count} member names in database")
    return updated_count


if __name__ == "__main__":
    # Test the loading
    members = load_council_members()
    print(f"Loaded {len(members)} council members")

    # Test lookup
    test_address = "0x37BC95e38235Ec42F185E945922a4E2C9795B391"
    info = get_member_info(test_address)
    print(f"Info for {test_address}: {info}")
    print(f"Formatted: {format_member_name(test_address)}")