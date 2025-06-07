# generate_invites.py
import secrets
import sys
from app.db.session import SessionLocal
from app.db.models import InviteCode

# --- How many codes to generate ---
NUM_CODES_TO_GENERATE = 50


def generate_and_store_codes():
    """
    Generates a batch of unique, cryptographically-secure invite codes
    and stores them in the database.
    """
    db = SessionLocal()
    print(f"Generating {NUM_CODES_TO_GENERATE} new invite codes...")

    new_codes = []
    for _ in range(NUM_CODES_TO_GENERATE):
        # Generate a 16-character secure hex code (e.g., 'a1b2c3d4e5f67890')
        new_code_str = secrets.token_hex(8)
        new_codes.append(InviteCode(code=new_code_str, is_used=False))

    try:
        db.add_all(new_codes)
        db.commit()
        print("-" * 30)
        print("Successfully added codes to the database. Distribute these codes:")
        print("-" * 30)
        for code in new_codes:
            print(code.code)
        print("-" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Allows generating a different number of codes from the command line
    # Example: python generate_invites.py 10
    if len(sys.argv) > 1:
        try:
            NUM_CODES_TO_GENERATE = int(sys.argv[1])
        except ValueError:
            print("Please provide a valid number.")
            sys.exit(1)

    generate_and_store_codes()