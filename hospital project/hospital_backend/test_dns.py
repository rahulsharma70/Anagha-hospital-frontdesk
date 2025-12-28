"""
Test DNS resolution for Supabase hostnames
"""
import socket

hosts_to_test = [
    "db.lrzlkoxqwtzwmbehfngn.supabase.co",
    "aws-0-us-east-1.pooler.supabase.com",
    "lrzlkoxqwtzwmbehfngn.supabase.co"
]

print("=" * 70)
print("DNS Resolution Test")
print("=" * 70)

for host in hosts_to_test:
    print(f"\nTesting: {host}")
    try:
        ip = socket.gethostbyname(host)
        print(f"  ✓ Resolved to: {ip}")
    except socket.gaierror as e:
        print(f"  ✗ DNS resolution failed: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("Recommendation:")
print("If all hostnames fail, use Connection Pooling from Supabase Dashboard")
print("=" * 70)



