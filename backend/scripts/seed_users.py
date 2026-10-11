"""
Script: Seed and Migrate User Credentials to PBKDF2 Hashed Storage
Migrates demo users and registered users to secure PBKDF2-HMAC-SHA256 hashed storage.
Passwords are never stored in plaintext.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.db import SessionLocal
from backend.app.models.review import UserORM
from backend.app.core.security import hash_password
from backend.app.core.config import settings

def seed_and_migrate_users():
    db = SessionLocal()
    try:
        admin_pass = settings.DEMO_ADMIN_PASSWORD or "AdminPass2026!"
        user_pass = settings.DEMO_USER_PASSWORD or "UserPass2026!"

        default_users = [
            {
                "user_id": "usr_001",
                "username": "admin",
                "password_plain": admin_pass,
                "role": "admin",
                "display_name": "Executive Operations Director",
                "title": "System Administrator & Fleet Director",
                "email": "admin@restaurantops.ai",
                "department": "Executive Leadership",
                "status": "Active"
            },
            {
                "user_id": "usr_002",
                "username": "user",
                "password_plain": user_pass,
                "role": "user",
                "display_name": "Operations Analyst",
                "title": "Restaurant Shift & Ops Manager",
                "email": "user@restaurantops.ai",
                "department": "Store Operations",
                "status": "Active"
            },
            {
                "user_id": "usr_003",
                "username": "sarah.jenkins",
                "password_plain": "SarahManager2026!",
                "role": "store_manager",
                "display_name": "Sarah Jenkins",
                "title": "General Manager",
                "email": "sarah.jenkins@restaurantops.ai",
                "department": "Store Operations",
                "status": "Active"
            },
            {
                "user_id": "usr_004",
                "username": "david.kim",
                "password_plain": "DavidOps2026!",
                "role": "operations_analyst",
                "display_name": "David Kim",
                "title": "Senior Operations Analyst",
                "email": "david.kim@restaurantops.ai",
                "department": "Fleet Intelligence",
                "status": "Active"
            },
            {
                "user_id": "usr_005",
                "username": "marcus.vance",
                "password_plain": "MarcusShift2026!",
                "role": "store_manager",
                "display_name": "Marcus Vance",
                "title": "Kitchen Operations Lead",
                "email": "marcus.vance@restaurantops.ai",
                "department": "Culinary Operations",
                "status": "Active"
            },
            {
                "user_id": "usr_006",
                "username": "elena.rostova",
                "password_plain": "ElenaAnalyst2026!",
                "role": "user",
                "display_name": "Elena Rostova",
                "title": "Quality Assurance Analyst",
                "email": "elena.rostova@restaurantops.ai",
                "department": "Customer Experience",
                "status": "Active"
            }
        ]

        migrated_count = 0
        for u_data in default_users:
            uname = u_data["username"]
            existing = db.query(UserORM).filter(UserORM.username == uname).first()
            hashed = hash_password(u_data["password_plain"])
            
            if existing:
                existing.password = hashed
                existing.role = u_data["role"]
                existing.display_name = u_data["display_name"]
                existing.title = u_data["title"]
                existing.email = u_data["email"]
                existing.department = u_data["department"]
                existing.status = u_data["status"]
            else:
                new_u = UserORM(
                    user_id=u_data["user_id"],
                    username=uname,
                    password=hashed,
                    role=u_data["role"],
                    display_name=u_data["display_name"],
                    title=u_data["title"],
                    email=u_data["email"],
                    department=u_data["department"],
                    status=u_data["status"],
                    created_at="2026-01-01 00:00:00"
                )
                db.add(new_u)
            migrated_count += 1

        db.commit()
        print(f"Successfully migrated {migrated_count} users to PBKDF2 hashed password storage.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_and_migrate_users()
