#!/usr/bin/env python3
"""Run all tests."""
import subprocess, sys

tests = [
    ("Connection", "tests/test_connection.py"),
    ("Storage", "tests/test_storage.py"),
    ("Search", "tests/test_search.py"),
]

passed = failed = 0
for name, path in tests:
    print(f"\n--- {name} ---")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout.strip())
    if result.returncode == 0:
        passed += 1
    else:
        failed += 1
        if result.stderr: print("STDERR:", result.stderr.strip())

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
