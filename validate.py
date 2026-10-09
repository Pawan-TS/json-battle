import sys
import json
import os
import glob
from pathlib import Path

def validate_fighter(data_str: str, config: dict, expected_handle: str = None, filename: str = None) -> list:
    problems = []
    
    try:
        fighter = json.loads(data_str)
    except json.JSONDecodeError as e:
        problems.append({
            "severity": "error",
            "field": "JSON",
            "message": f"Syntax error at line {e.lineno}, column {e.colno}. Hint: Check for trailing commas or single quotes instead of double quotes."
        })
        return problems

    if not isinstance(fighter, dict):
        problems.append({
            "severity": "error",
            "field": "JSON",
            "message": "Top-level JSON structure must be an object (dictionary)."
        })
        return problems

    required_keys = {
        "name": str,
        "hp": int,
        "attack": int,
        "defense": int,
        "catchphrase": str
    }
    optional_keys = {
        "victory_quote": str,
        "archetype": str
    }

    for key in fighter.keys():
        if key not in required_keys and key not in optional_keys:
            problems.append({
                "severity": "warning",
                "field": key,
                "message": f"Unknown key '{key}'. This is allowed but won't be used."
            })

    for key, expected_type in required_keys.items():
        if key not in fighter:
            problems.append({
                "severity": "error",
                "field": key,
                "message": f"Missing required key '{key}'."
            })
            continue

        val = fighter[key]
        if expected_type == int:
            if isinstance(val, bool):
                problems.append({"severity": "error", "field": key, "message": f"'{key}' must be a whole number, not a boolean."})
            elif isinstance(val, float):
                problems.append({"severity": "error", "field": key, "message": f"'{key}' must be a whole number, not a decimal/float."})
            elif not isinstance(val, int):
                problems.append({"severity": "error", "field": key, "message": f"'{key}' must be a number."})
        elif expected_type == str:
            if not isinstance(val, str):
                problems.append({"severity": "error", "field": key, "message": f"'{key}' must be a string."})
            elif len(val.strip()) == 0:
                problems.append({"severity": "error", "field": key, "message": f"'{key}' cannot be empty."})

    for key, expected_type in optional_keys.items():
        if key in fighter:
            val = fighter[key]
            if expected_type == str and not isinstance(val, str):
                problems.append({"severity": "error", "field": key, "message": f"'{key}' must be a string."})

    stats_total = 0
    valid_stats = True
    for stat_name in ["hp", "attack", "defense"]:
        if stat_name in fighter and isinstance(fighter[stat_name], int) and not isinstance(fighter[stat_name], bool):
            val = fighter[stat_name]
            stats_total += val
            min_val = config.get(stat_name, {}).get("min", 0)
            max_val = config.get(stat_name, {}).get("max", 0)
            if val < min_val or val > max_val:
                problems.append({"severity": "error", "field": stat_name, "message": f"'{stat_name}' must be between {min_val} and {max_val}."})
        else:
            valid_stats = False

    if valid_stats:
        cap = config.get("stat_total_cap", 150)
        if stats_total > cap:
            over = stats_total - cap
            problems.append({"severity": "error", "field": "stats", "message": f"Total stats (hp + attack + defense) cannot exceed {cap}. Current total is {stats_total} ({over} over limit)."})

    if "name" in fighter and isinstance(fighter["name"], str):
        name_max = config.get("name_max_length", 24)
        if len(fighter["name"]) > name_max:
            problems.append({"severity": "error", "field": "name", "message": f"'name' is too long (max {name_max} characters)."})

    if "catchphrase" in fighter and isinstance(fighter["catchphrase"], str):
        catchphrase_max = config.get("catchphrase_max_length", 80)
        if len(fighter["catchphrase"]) > catchphrase_max:
            problems.append({"severity": "error", "field": "catchphrase", "message": f"'catchphrase' is too long (max {catchphrase_max} characters)."})
            
    if expected_handle and filename:
        stem = Path(filename).stem
        if stem.lower() != expected_handle.lower():
            if expected_handle.lower() not in [h.lower() for h in config.get("organizer_handles", [])]:
                problems.append({"severity": "error", "field": "filename", "message": f"Filename '{stem}' does not match GitHub handle '{expected_handle}'."})

    return problems

def main():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("ERROR: config.json not found.")
        sys.exit(1)

    expected_handle = None
    files_to_check = []
    args = sys.argv[1:]

    if len(args) >= 3 and args[0] == "--pr":
        files_to_check = [args[1]]
        expected_handle = args[2]
    elif len(args) > 0:
        files_to_check = args
    else:
        files_to_check = [f for f in glob.glob("fighters/*.json") if not os.path.basename(f).startswith("_")]

    all_passed = True
    for filepath in files_to_check:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"FAIL: {filepath} (File not found)")
            all_passed = False
            continue

        problems = validate_fighter(content, config, expected_handle, os.path.basename(filepath))
        
        errors = [p for p in problems if p["severity"] == "error"]
        warnings = [p for p in problems if p["severity"] == "warning"]

        if errors:
            all_passed = False
            print(f"FAIL: {filepath}")
            for p in errors:
                print(f"  - ERROR ({p['field']}): {p['message']}")
            for p in warnings:
                print(f"  - WARNING ({p['field']}): {p['message']}")
        else:
            status = "PASS" if not warnings else "PASS (with warnings)"
            print(f"{status}: {filepath}")
            for p in warnings:
                print(f"  - WARNING ({p['field']}): {p['message']}")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
