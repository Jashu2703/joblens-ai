#!/usr/bin/env python3
"""
JobLens AI — Database Seed Script
Run this after starting the backend to populate the job database.

Usage:
  python scripts/seed.py
  python scripts/seed.py --url http://localhost:8000 --email admin@test.com --password test123
"""
import argparse
import httpx
import sys

def seed(base_url: str, email: str, password: str):
    print(f"\nJobLens AI — Seed Script")
    print(f"Target: {base_url}\n")

    # Register or login
    print("1. Creating test user...")
    try:
        r = httpx.post(f"{base_url}/api/auth/register", json={
            "email": email, "name": "Admin User", "password": password
        }, timeout=10)
        if r.status_code == 201:
            token = r.json()["access_token"]
            print(f"   ✓ User created: {email}")
        elif r.status_code == 400:
            print(f"   → User exists, logging in...")
            r2 = httpx.post(f"{base_url}/api/auth/login", json={"email": email, "password": password}, timeout=10)
            r2.raise_for_status()
            token = r2.json()["access_token"]
            print(f"   ✓ Logged in: {email}")
        else:
            r.raise_for_status()
    except Exception as e:
        print(f"   ✗ Auth error: {e}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # Seed jobs
    print("\n2. Seeding job database...")
    try:
        r = httpx.post(f"{base_url}/api/jobs/seed/now", headers=headers, timeout=60)
        r.raise_for_status()
        print(f"   ✓ {r.json()['message']}")
    except Exception as e:
        print(f"   ✗ Seeding error: {e}")

    # Check stats
    print("\n3. Checking database stats...")
    try:
        r = httpx.get(f"{base_url}/api/jobs/stats", timeout=10)
        stats = r.json()
        print(f"   ✓ Total jobs: {stats['total_jobs']}")
        print(f"   ✓ Full-time: {stats['full_time']}")
        print(f"   ✓ Internships: {stats['internships']}")
    except Exception as e:
        print(f"   ✗ Stats error: {e}")

    print(f"\n✅ Done! Visit {base_url}/docs to explore the API.")
    print(f"   Frontend: http://localhost:3000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed JobLens AI database")
    parser.add_argument("--url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--email", default="admin@joblens.ai", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    args = parser.parse_args()
    seed(args.url, args.email, args.password)
