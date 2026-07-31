# password-generator

Cryptographically secure password generator.

## Why

Weak or reused passwords are still one of the most common ways accounts get broken into. This tool generates passwords with real, measurable cryptographic strength — using the OS's secure random source instead of a predictable PRNG, strong enough to resist both classical brute-force and quantum-assisted attacks — as a local CLI with no browser, no extension, and no third-party service involved.

## How it works

1. Build a character pool from the enabled categories (lowercase, uppercase, digits, symbols), optionally stripping visually-ambiguous or shell-hostile characters (`il1LoO0` and friends).
2. Pick one character from each enabled category first, so the result satisfies typical "must contain a symbol" policies.
3. Fill the remaining length with `secrets.choice()` picks from the full pool — `secrets` draws from the OS's cryptographically secure random source, unlike `random`, which is a statistical PRNG predictable to an attacker who can model its internal state.
4. Fisher-Yates shuffle the result using `secrets.randbelow()` — not `random.shuffle()` — so the guaranteed characters aren't clustered at the front.
5. Optionally copy the result to the clipboard instead of printing it, then hand a copy to a detached background process over stdin (never argv, since argv is visible via `ps`) that clears the clipboard after a timeout — but only if the clipboard still contains what was set, so it won't clobber something else you copy in the meantime.
6. Entropy can be sized against quantum brute-force, not just classical: Grover's algorithm only gives a quadratic (not exponential) speedup against brute-force search, so doubling the entropy budget compensates for it — 256 bits of entropy preserves ~128 bits of effective security even against that speedup, the same margin AES-256 relies on for quantum resistance.

## Usage

```
usage: password-generator [-h] [-l LENGTH] [-n COUNT] [--no-lower]
                          [--no-upper] [--no-digits] [--no-symbols]
                          [--exclude-ambiguous] [--no-guarantee] [--paranoid]
                          [--show-entropy] [-c]
                          [--clipboard-timeout CLIPBOARD_TIMEOUT]

Generate cryptographically secure passwords using the OS CSPRNG.

options:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
  -n COUNT, --count COUNT
  --no-lower
  --no-upper
  --no-digits
  --no-symbols
  --exclude-ambiguous
  --no-guarantee        don't force at least one char from each enabled
                        category
  --paranoid            auto-set length so entropy >= 256 bits
  --show-entropy
  -c, --clipboard       copy the password to the clipboard instead of printing
                        it
  --clipboard-timeout CLIPBOARD_TIMEOUT
                        seconds before the clipboard is auto-cleared, 0 to
                        disable (default 20)
```

### Examples

```bash
password-generator                             # 32-char password, all categories
password-generator -l 64 -n 5                  # five 64-char passwords
password-generator --paranoid --show-entropy   # auto-length for >=256 bits, print entropy
password-generator --exclude-ambiguous         # drop chars like l/1/I/O/0
password-generator -c                          # copy to clipboard, clear after 20s
password-generator -c --clipboard-timeout 0    # copy, never auto-clear
```

## Installation

Requirements: Python 3.10+, [`uv`](https://docs.astral.sh/uv/), and, if on Linux, `xclip` or `xsel` (for clipboard support).

```bash
uv tool install git+https://github.com/p4p2r0/password-generator
```

## License

This project is licensed under the [MIT License](LICENSE)
