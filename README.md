# JSON Auto-Battler Arena

Welcome to the JSON Auto-Battler Arena! This is a simple, zero-dependency Python engine where participants submit their custom JSON fighters to battle it out in a simulated tournament.

## Quick Start

1. **Fork** this repository.
2. **Copy** `fighters/_template.json` to `fighters/<your-github-handle>.json`. Do not edit the template!
3. **Edit** your new JSON file to customize your fighter.
4. **Validate** your fighter by running `python validate.py` in your terminal.
5. **Commit** your file and **open a Pull Request** to the main repository.

## Stat Rules

Your fighter's stats must adhere to the following limits. The total of `hp + attack + defense` cannot exceed **150**.

| Stat | Minimum | Maximum |
|---|---|---|
| `hp` (Health Points) | 10 | 100 |
| `attack` | 1 | 50 |
| `defense` | 0 | 50 |

## Archetypes

Need inspiration? Check out these common fighter builds:
- **Glass Cannon:** Maximize attack, minimize defense. Hope you strike first!
- **Tank (Unmovable Object):** Maximize HP and defense. Outlast your opponent.
- **Balanced Brawler:** A healthy mix of all stats to adapt to any fight.

## Troubleshooting

- **JSON Syntax Errors:** Make sure you aren't using single quotes (`'`), and watch out for trailing commas at the end of lists or objects.
- **Editing the wrong file:** Only edit your specific `<your-github-handle>.json` file in the `fighters/` directory. Do not modify `_template.json` or `config.json`.
- **PR includes more than one file:** Ensure your pull request only contains your single JSON file. Revert any accidental changes to other files before submitting.
