#!/usr/bin/env python3
"""
runner.py: Comprehensive test harness for Disaster Relief Logistics DB.
Executes Q01-Q20 against PostgreSQL 16 container, comparing outputs against
independently generated CSV references in tests/expected/.
Reports PASS / FAIL / NOT ATTEMPTED per item.
"""

import os
import sys
import subprocess
import csv
import io

# ANSI color escape codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_RED = "\033[31m"
COLOR_BOLD = "\033[1m"
COLOR_CYAN = "\033[36m"

def run_psql_file(rel_path):
    cmd = [
        "docker", "compose", "exec", "-T", "db",
        "psql", "-U", "postgres", "-d", "disaster_relief",
        "--csv", "--quiet", "-v", "ON_ERROR_STOP=1", "-f", f"/{rel_path}"
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def parse_csv_string(csv_text):
    if not csv_text:
        return [], []
    f = io.StringIO(csv_text)
    reader = csv.reader(f)
    try:
        header = next(reader, None)
        if not header:
            return [], []
        rows = list(reader)
        return [h.strip() for h in header], rows
    except Exception:
        return [], []

def load_expected_csv(path):
    if not os.path.exists(path):
        return None, None
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        rows = list(reader)
        return [h.strip() for h in header] if header else [], rows

def compare_rows(actual_rows, expected_rows):
    if len(actual_rows) != len(expected_rows):
        return False, f"Row count mismatch: expected {len(expected_rows)}, got {len(actual_rows)}"
    
    # Compare row-by-row or set-based comparison
    # Normalize values (e.g. float strings)
    def normalize_val(v):
        v = v.strip()
        try:
            return f"{float(v):.2f}"
        except ValueError:
            return v.lower()

    norm_actual = [tuple(normalize_val(x) for x in r) for r in actual_rows]
    norm_expected = [tuple(normalize_val(x) for x in r) for r in expected_rows]

    # Check direct order match or multiset match
    if norm_actual == norm_expected:
        return True, "Match"

    sorted_act = sorted(norm_actual)
    sorted_exp = sorted(norm_expected)
    if sorted_act == sorted_exp:
        return True, "Match (unordered)"

    diff_sample = []
    for idx, (a, e) in enumerate(zip(sorted_act, sorted_exp)):
        if a != e:
            diff_sample.append(f"Row {idx+1}: got {a} != expected {e}")
            if len(diff_sample) >= 3:
                break
    return False, "; ".join(diff_sample) if diff_sample else "Content mismatch"

def main():
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}=== Disaster Relief Logistics DB - Test Suite ==={COLOR_RESET}\n")

    queries_dir = os.path.join(os.path.dirname(__file__), "..", "db", "queries")
    expected_dir = os.path.join(os.path.dirname(__file__), "expected")

    query_files = sorted([f for f in os.listdir(queries_dir) if f.endswith(".sql")])
    if not query_files:
        print(f"{COLOR_RED}Error: No query files found in db/queries/{COLOR_RESET}")
        sys.exit(1)

    results = []
    pass_cnt = 0
    fail_cnt = 0
    not_attempted_cnt = 0

    print(f"{COLOR_BOLD}{'Query ID':<10} | {'Status':<16} | {'Details':<50}{COLOR_RESET}")
    print("-" * 80)

    for q_file in query_files:
        q_id = q_file.replace(".sql", "")
        rel_sql_path = f"db/queries/{q_file}"
        exp_path = os.path.join(expected_dir, f"{q_id}.csv")

        retcode, out, err = run_psql_file(rel_sql_path)
        if retcode != 0:
            status = f"{COLOR_RED}FAIL{COLOR_RESET}"
            fail_cnt += 1
            details = f"SQL error: {err[:45]}"
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "FAIL", details))
            continue

        act_cols, act_rows = parse_csv_string(out)

        # Check if stub
        if act_cols == ["not_attempted"] or (act_rows and act_rows[0] == ["TODO"]):
            status = f"{COLOR_YELLOW}NOT ATTEMPTED{COLOR_RESET}"
            not_attempted_cnt += 1
            details = "Stub active ('TODO')"
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "NOT ATTEMPTED", details))
            continue

        exp_cols, exp_rows = load_expected_csv(exp_path)
        if exp_cols is None:
            status = f"{COLOR_RED}FAIL{COLOR_RESET}"
            fail_cnt += 1
            details = f"Missing reference file tests/expected/{q_id}.csv"
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "FAIL", details))
            continue

        # Check column names
        if [c.lower() for c in act_cols] != [c.lower() for c in exp_cols]:
            status = f"{COLOR_RED}FAIL{COLOR_RESET}"
            fail_cnt += 1
            details = f"Column mismatch: got {act_cols}, expected {exp_cols}"
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "FAIL", details))
            continue

        # Check rows
        is_ok, msg = compare_rows(act_rows, exp_rows)
        if is_ok:
            status = f"{COLOR_GREEN}PASS{COLOR_RESET}"
            pass_cnt += 1
            details = f"{len(act_rows)} rows verified"
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "PASS", details))
        else:
            status = f"{COLOR_RED}FAIL{COLOR_RESET}"
            fail_cnt += 1
            details = msg[:48]
            print(f"{q_id:<10} | {status:<25} | {details:<50}")
            results.append((q_id, "FAIL", details))

    print("-" * 80)
    print(f"\n{COLOR_BOLD}Summary:{COLOR_RESET}")
    print(f"  Total Queries : {len(query_files)}")
    print(f"  {COLOR_GREEN}Passed        : {pass_cnt}{COLOR_RESET}")
    print(f"  {COLOR_RED}Failed        : {fail_cnt}{COLOR_RESET}")
    print(f"  {COLOR_YELLOW}Not Attempted : {not_attempted_cnt}{COLOR_RESET}\n")

    if fail_cnt > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
