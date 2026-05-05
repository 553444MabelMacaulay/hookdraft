# hookdraft

A minimal webhook testing and replay server with request diffing and payload history.

---

## Installation

```bash
pip install hookdraft
```

Or install from source:

```bash
git clone https://github.com/yourname/hookdraft.git && cd hookdraft && pip install -e .
```

---

## Usage

Start the local webhook server:

```bash
hookdraft serve --port 8080
```

hookdraft will listen for incoming webhook requests and log every payload to its history. You can then replay, diff, or inspect past requests using the CLI:

```bash
# List captured requests
hookdraft history

# Replay the most recent request
hookdraft replay --last

# Diff two captured payloads by ID
hookdraft diff <id1> <id2>
```

Or use it directly in Python:

```python
from hookdraft import Server

server = Server(port=8080)
server.start()

# Access payload history
for entry in server.history:
    print(entry.method, entry.path, entry.body)
```

---

## Features

- Instant local webhook endpoint — no tunneling required
- Full request history with timestamps and headers
- Side-by-side payload diffing between any two captured requests
- One-command replay to re-send payloads to any target URL

---

## License

MIT © 2024 Your Name