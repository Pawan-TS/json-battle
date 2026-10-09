# JSON Auto-Battler Arena

Welcome to the **JSON Auto-Battler Arena**! A lightweight, zero-dependency battle simulator where participants create custom fighters using simple JSON files and pit them against each other in an automated knockout tournament.

Includes both a **Python CLI engine** and an interactive **Web UI Tournament Visualizer**.

---

## Quick Start for Participants

1. **Fork** this repository.
2. **Copy the template** into `fighters/<your-github-handle>.json`:
   ```bash
   cp fighters/_template.json fighters/<your-github-handle>.json
   ```
   > **Note:** Do not modify `fighters/_template.json` or `config.json`.
3. **Customize your fighter** in `fighters/<your-github-handle>.json`:
   ```json
   {
     "name": "Shadow Blade",
     "hp": 60,
     "attack": 45,
     "defense": 45,
     "catchphrase": "Now you see me, now you don't!",
     "victory_quote": "A clean cut.",
     "archetype": "Balanced Brawler"
   }
   ```
4. **Validate** your fighter locally:
   ```bash
   python validate.py
   ```
5. **Commit and open a Pull Request** to the main repository!

---

## Fighter Specification & Stat Limits

Your fighter's stats must strictly comply with the arena rules:

- **Total Stat Cap:** `hp + attack + defense` **≤ 150**
- **Field Constraints:**

| Field | Type | Required | Constraints / Limits | Description |
|---|---|---|---|---|
| `name` | `string` | **Yes** | 1 – 24 characters | Fighter's display name |
| `hp` | `integer` | **Yes** | 10 – 100 | Starting Health Points |
| `attack` | `integer` | **Yes** | 1 – 50 | Base attack power |
| `defense` | `integer` | **Yes** | 0 – 50 | Armor / damage mitigation |
| `catchphrase` | `string` | **Yes** | 1 – 80 characters | Spoken when entering battle |
| `victory_quote` | `string` | No | 1 – 80 characters | Spoken when winning the match |
| `archetype` | `string` | No | Optional tag | e.g. Glass Cannon, Tank, Brawler |

---

## Combat Mechanics

The battle engine simulates turn-based rounds until one fighter is knocked out (HP reaches 0) or maximum rounds are reached:

1. **Initiative:**
   - The fighter with the higher `attack` strikes first each round.
   - Tied attack stats result in a 50/50 coin toss for turn order.
2. **Armor Mitigation (Diminishing Returns):**
   - Defense provides smooth damage reduction rather than flat subtraction:
     $$\text{Mitigation} = \frac{\text{Defense}}{\text{Defense} + 50}$$
   - Base damage is $\text{Attack} \times (1 - \text{Mitigation})$, with a minimum of 1 damage.
3. **Damage Variance:**
   - Final damage includes a $\pm 15\%$ random multiplier.
4. **Timeout / Tie-Breaker:**
   - If both fighters survive past 50 rounds, the winner is determined by **highest remaining HP percentage** ($\frac{\text{Current HP}}{\text{Max HP}}$).

---

## Archetype Inspiration

Need inspiration for your build? Here are classic strategies (all total 150 stats):

- 🗡️ **Glass Cannon** (`hp: 50`, `attack: 50`, `defense: 50` or `hp: 50`, `attack: 50`, `defense: 0`): Strike first with devastating power.
- 🛡️ **Unmovable Tank** (`hp: 100`, `attack: 10`, `defense: 40`): Massive HP pool and heavy armor to outlast anyone.
- ⚖️ **Balanced Brawler** (`hp: 60`, `attack: 45`, `defense: 45`): Solid balance of offensive power and survivability.

---

## Running the Arena

### 1. Web UI Tournament Visualizer (Recommended)
Start the local server:
```bash
python server.py
# or npm start
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser to view the interactive tournament bracket, real-time battle animations, sound effects, and sandbox simulator.

### 2. CLI Battle Engine
Run a single-elimination tournament directly in your terminal:
```bash
python battle.py
```

**CLI Options:**
- `--seed <int>`: Set a tournament seed for deterministic, reproducible bracket & rolls.
- `--delay <float>`: Adjust seconds between battle log events (default: `1.0`).
- `--fast`: Fast-forward and only print match winners.
- `--plain`: Disable ANSI colors and delay (ideal for CI / non-interactive shells).

### 3. Fighter Validator
Validate all fighters in `fighters/`:
```bash
python validate.py
```

Validate a specific PR fighter and handle:
```bash
python validate.py --pr fighters/<github-handle>.json <github-handle>
```

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
