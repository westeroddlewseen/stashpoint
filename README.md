# stashpoint

A CLI tool for saving and restoring named sets of environment variables across projects.

---

## Installation

```bash
pip install stashpoint
```

Or install from source:

```bash
pip install git+https://github.com/yourname/stashpoint.git
```

---

## Usage

Save the current environment variables as a named stash:

```bash
stashpoint save myproject
```

Restore a previously saved stash:

```bash
stashpoint load myproject
```

List all saved stashes:

```bash
stashpoint list
```

Delete a stash:

```bash
stashpoint delete myproject
```

Stashes are stored locally in `~/.stashpoint/` and can be shared across projects or machines.

---

## Example Workflow

```bash
# Save staging credentials
export API_KEY=abc123
export DB_URL=postgres://staging-host/db
stashpoint save staging

# Later, restore them in any project
stashpoint load staging
```

---

## License

MIT © [yourname](https://github.com/yourname)