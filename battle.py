import sys
import json
import glob
import os
import random
import time
import argparse
from validate import validate_fighter

def load_fighters(config):
    fighters = []
    for filepath in glob.glob("fighters/*.json"):
        if os.path.basename(filepath).startswith("_"):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            problems = validate_fighter(content, config)
            errors = [p for p in problems if p["severity"] == "error"]
            if errors:
                print(f"Skipping {filepath} due to errors:")
                for e in errors:
                    print(f"  - {e['field']}: {e['message']}")
            else:
                fighter = json.loads(content)
                fighter["_id"] = os.path.basename(filepath)
                fighter["_max_hp"] = fighter["hp"]
                fighters.append(fighter)
        except Exception as e:
            print(f"Skipping {filepath} due to read error: {e}")
    return fighters

def simulate_match(f1, f2, config, rng):
    events = []
    events.append({"type": "enter", "fighter": f1["name"], "catchphrase": f1.get("catchphrase", "")})
    events.append({"type": "enter", "fighter": f2["name"], "catchphrase": f2.get("catchphrase", "")})
    
    hp1 = f1["hp"]
    hp2 = f2["hp"]
    
    max_rounds = config.get("max_rounds", 50)
    variance = config.get("damage_variance", 0.15)
    def_eff = config.get("defense_effectiveness", 0.5)
    
    for r in range(1, max_rounds + 1):
        if f1["attack"] > f2["attack"]:
            first, second = f1, f2
            first_hp, second_hp = hp1, hp2
            is_f1_first = True
        elif f2["attack"] > f1["attack"]:
            first, second = f2, f1
            first_hp, second_hp = hp2, hp1
            is_f1_first = False
        else:
            if rng.choice([True, False]):
                first, second = f1, f2
                first_hp, second_hp = hp1, hp2
                is_f1_first = True
            else:
                first, second = f2, f1
                first_hp, second_hp = hp2, hp1
                is_f1_first = False
                
        def strike(attacker, defender, def_hp):
            base = attacker["attack"] - defender["defense"] * def_eff
            base = max(1, round(base))
            mult = rng.uniform(1 - variance, 1 + variance)
            dmg = max(1, round(base * mult))
            def_hp -= dmg
            return dmg, def_hp
            
        dmg, second_hp = strike(first, second, second_hp)
        events.append({"type": "strike", "round": r, "attacker": first["name"], "damage": dmg, "defender": second["name"], "defender_hp": second_hp})
        
        if second_hp <= 0:
            winner = first
            break
            
        dmg, first_hp = strike(second, first, first_hp)
        events.append({"type": "strike", "round": r, "attacker": second["name"], "damage": dmg, "defender": first["name"], "defender_hp": first_hp})
        
        if first_hp <= 0:
            winner = second
            break
            
        if is_f1_first:
            hp1, hp2 = first_hp, second_hp
        else:
            hp2, hp1 = first_hp, second_hp
            
    else:
        pct1 = hp1 / f1["_max_hp"]
        pct2 = hp2 / f2["_max_hp"]
        if pct1 > pct2:
            winner = f1
        elif pct2 > pct1:
            winner = f2
        else:
            winner = f1 if rng.choice([True, False]) else f2
        events.append({"type": "timeout", "winner": winner["name"]})
        
    quote = winner.get("victory_quote", winner.get("catchphrase", ""))
    events.append({"type": "winner", "fighter": winner["name"], "quote": quote})
    
    return winner, events

def power_of_two(n):
    p = 1
    while p < n:
        p *= 2
    return p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between rounds")
    parser.add_argument("--plain", action="store_true", help="Disable colors and delays")
    parser.add_argument("--fast", action="store_true", help="Print only match results")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randint(0, 999999999)
    rng = random.Random(seed)
    
    print(f"Tournament Seed: {seed}")
    
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("ERROR: config.json not found.")
        sys.exit(1)

    fighters = load_fighters(config)
    
    if not fighters:
        print("No valid fighters found. Exiting.")
        sys.exit(0)
        
    if len(fighters) == 1:
        print(f"Only one fighter entered! The champion is {fighters[0]['name']}!")
        sys.exit(0)

    rng.shuffle(fighters)
    
    num_slots = power_of_two(len(fighters))
    byes_needed = num_slots - len(fighters)
    
    temp_bracket = []
    idx = 0
    while byes_needed > 0:
        temp_bracket.append(fighters[idx])
        temp_bracket.append(None)
        idx += 1
        byes_needed -= 1
    while idx < len(fighters):
        temp_bracket.append(fighters[idx])
        idx += 1
        
    bracket = temp_bracket
    
    plain_mode = args.plain or "NO_COLOR" in os.environ or not sys.stdout.isatty()
    delay = args.delay if not plain_mode and not args.fast else 0
    
    c_red = "" if plain_mode else "\033[91m"
    c_green = "" if plain_mode else "\033[92m"
    c_yellow = "" if plain_mode else "\033[93m"
    c_cyan = "" if plain_mode else "\033[96m"
    c_reset = "" if plain_mode else "\033[0m"
    
    round_num = 1
    while len(bracket) > 1:
        if not args.fast:
            print(f"\n{c_yellow}{'='*30}\nBRACKET ROUND {round_num}\n{'='*30}{c_reset}\n")
        next_bracket = []
        for i in range(0, len(bracket), 2):
            f1 = bracket[i]
            f2 = bracket[i+1]
            if f1 is None and f2 is None:
                next_bracket.append(None)
            elif f1 is None:
                next_bracket.append(f2)
                if not args.fast:
                    print(f"{f2['name']} gets a BYE this round.")
            elif f2 is None:
                next_bracket.append(f1)
                if not args.fast:
                    print(f"{f1['name']} gets a BYE this round.")
            else:
                if not args.fast:
                    print(f"\n--- MATCH: {c_cyan}{f1['name']}{c_reset} vs {c_cyan}{f2['name']}{c_reset} ---")
                    time.sleep(delay)
                winner, events = simulate_match(f1, f2, config, rng)
                next_bracket.append(winner)
                
                if args.fast:
                    print(f"{f1['name']} vs {f2['name']} -> Winner: {winner['name']}")
                else:
                    for e in events:
                        if e["type"] == "enter":
                            print(f"> {e['fighter']} enters: \"{e['catchphrase']}\"")
                            time.sleep(delay)
                        elif e["type"] == "strike":
                            hp = max(0, e["defender_hp"])
                            print(f"[Round {e['round']}] {c_red}{e['attacker']}{c_reset} strikes {c_green}{e['defender']}{c_reset} for {e['damage']} damage! ({e['defender']} HP: {hp})")
                            time.sleep(delay / 2)
                        elif e["type"] == "timeout":
                            print(f"Time limit reached! {c_yellow}{e['winner']}{c_reset} wins by HP percentage!")
                            time.sleep(delay)
                        elif e["type"] == "winner":
                            print(f"*** {c_cyan}{e['fighter']} wins!{c_reset} \"{e['quote']}\" ***")
                            time.sleep(delay)
        bracket = next_bracket
        round_num += 1
        
    champion = bracket[0]
    print(f"\n{c_yellow}" + "*"*40)
    print(f"THE CHAMPION IS {champion['name']}!")
    print(f"\"{champion.get('victory_quote', champion.get('catchphrase', ''))}\"")
    print("*"*40 + f"{c_reset}\n")

if __name__ == "__main__":
    main()
