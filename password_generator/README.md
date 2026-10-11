# 🔐 Python Password Generator — A Beginner-Friendly Python Learning Project

A simple command-line tool that creates strong random passwords and tells you how
strong they are. It is small enough to read in one sitting, and it teaches a few
things every Python programmer should know — most of all, why passwords must come
from `secrets` and not from `random`.

---

## Features

| Feature | Description |
|---|---|
| **Random passwords** | Generates a password of any length from 4 to 128 characters (default 16) |
| **Several at once** | Use `--count` to generate up to 50 passwords in one go |
| **Choose the characters** | Lowercase letters are always used. Turn off uppercase, digits, or symbols with a flag |
| **Every chosen set is used** | If digits are on, the password always contains at least one digit (same for uppercase and symbols) |
| **Strength estimate** | Shows a rating (Weak, Fair, Strong, Very strong) and the estimated bits of entropy |
| **Pipe-friendly** | Passwords go to the screen only; the strength message is kept separate |
| **Clear errors** | Invalid options give a short message instead of a crash |
| **No dependencies** | Uses only Python's standard library |
| **Unit tests** | 24 built-in tests using `unittest` |

---

## How to Run

### Prerequisites

Python 3.11 or newer:

```bash
python --version
```

On some systems the command is `python3`. If Python is not installed, get it from [python.org](https://www.python.org/downloads/).

There is nothing else to install.

### Run the App

```bash
cd password_generator
python main.py
```

### Run the Tests

```bash
python -m unittest -v
```

---

## How to Use

```
python main.py [-l LENGTH] [-c COUNT] [--no-upper] [--no-digits] [--no-symbols]
```

| Option | Description |
|---|---|
| `-l`, `--length` | Password length, 4 to 128 (default: 16) |
| `-c`, `--count` | How many passwords to generate, 1 to 50 (default: 1) |
| `--no-upper` | Leave out uppercase letters |
| `--no-digits` | Leave out digits |
| `--no-symbols` | Leave out symbols |
| `-h`, `--help` | Show the help message |

**A default password:**

```bash
python main.py
```

```
c;3g?GZ?ziaoh9b2
Strength: Very strong (about 103 bits)
```

**Three longer passwords:**

```bash
python main.py -l 24 -c 3
```

```
2p4ws:iK=)+.[@;w7-Ni5G)d
y%,NDR0(_60v_U5$Bzl:pfv&
}AS$Nk!IIOv%=J+{1_Ns{9_B
Strength: Very strong (about 154 bits)
```

**Letters and digits only** (for sites that do not accept symbols):

```bash
python main.py --no-symbols -l 12
```

```
2GVX8Mgsd49c
Strength: Strong (about 71 bits)
```

**Letters only:**

```bash
python main.py --no-upper --no-digits --no-symbols -l 10
```

```
ikahaehcpc
Strength: Fair (about 47 bits)
```

Your passwords will be different every time — that is the point.

**Use it in a pipeline.** The passwords are printed to standard output and the strength message to standard error, so only the passwords get passed on:

```bash
python main.py -c 5 > passwords.txt
python main.py -c 50 | head -n 3
```

**Exit codes:** `0` on success, `1` if the output cannot be written, `2` if an option is invalid.

---

## How the Strength Is Estimated

Every character chosen from a set of N possible characters adds `log2(N)` bits of
entropy. The default set has 85 characters (26 + 26 + 10 + 23 symbols), so each
character adds about 6.4 bits, and a 16-character password has about 103 bits.

Every extra bit doubles the number of guesses an attacker needs.

| Bits | Rating |
|---|---|
| Below 40 | Weak |
| 40 to 59 | Fair |
| 60 to 79 | Strong |
| 80 or more | Very strong |

This is an estimate for passwords made by this tool. It does not apply to passwords a
person invented, because humans are not random.

---

## Project Structure

```
password_generator/
├── main.py            # The whole program
├── test_main.py       # Unit tests
├── pyproject.toml     # Project configuration
└── README.md          # This documentation
```

---

## Python Concepts Covered

### 1. `secrets` vs `random`
```python
import secrets

secrets.choice("abc123")   # safe for passwords
```
The `random` module is predictable: if someone learns a few of its outputs, they can
work out the next ones. The `secrets` module uses the operating system's secure
random source and is meant for passwords, tokens, and keys. Never use `random` for
anything secret.

---

### 2. Constants from `string`
```python
import string

string.ascii_lowercase   # 'abcdefghijklmnopqrstuvwxyz'
string.digits            # '0123456789'
```
The `string` module already has the character sets you need, so you do not have to
type them out.

---

### 3. Functions That Do One Thing
```python
def build_pools(...): ...        # which characters may be used
def generate_password(...): ...  # make one password
def entropy_bits(...): ...       # estimate the strength
def strength_label(...): ...     # turn bits into a word
```
Small functions are easy to understand and easy to test. `main()` only connects them.

---

### 4. Building a Password in Three Steps
```python
characters = [secrets.choice(pool) for pool in pools]   # 1. one from each set
characters += [secrets.choice(everything) for _ in range(rest)]   # 2. fill up
secrets.SystemRandom().shuffle(characters)               # 3. shuffle
```
Picking at random alone could produce a password with no digit even when digits are
allowed. Taking one guaranteed character from each set first, and shuffling at the
end, fixes that. This is also a list comprehension: a short way to build a list.

---

### 5. Command-Line Options with `argparse`
```python
parser.add_argument("-l", "--length", type=int, default=16)
parser.add_argument("--no-digits", dest="use_digits", action="store_false")
```
`argparse` reads the options, converts `--length 24` into the number `24`, creates
`--help` for you, and prints a clear message when something is wrong.
`action="store_false"` makes a flag that turns a feature off.

---

### 6. Standard Output vs Standard Error
```python
print(password)                         # stdout: the result
print("Strength: ...", file=sys.stderr) # stderr: extra information
```
Results go to stdout and messages for the person go to stderr. That is why
`python main.py > passwords.txt` saves only the passwords.

---

### 7. Exit Codes and Handling a Closed Pipe
```python
except OSError as error:
    ...
```
A program tells the shell whether it worked through its exit code (`0` means success).
With `python main.py -c 50 | head -n 1`, `head` stops reading after one line. Printing
more would raise `BrokenPipeError`, which is normal use, so `print_lines()` stops
quietly instead of showing a traceback.

---

### 8. Unit Testing with `unittest`
```python
def test_contains_at_least_one_character_of_every_set(self):
    for _ in range(300):
        password = main.generate_password(4, pools)
        ...
```
Because the output is random, it cannot be tested against one fixed answer. Instead
the tests check *properties*: the length is exact, every chosen set is present, and
no unwanted characters appear. Each check is repeated hundreds of times, because a
single lucky run proves very little.

---

## Safety Tips

- Use a different password for every account, and keep them in a password manager.
- The passwords stay visible in your terminal scrollback. Clear it after copying.
- This tool never stores or sends anything — it only prints.

---

## Next Steps

After understanding this project, you can try:

1. **Copy to clipboard** — add a `--copy` option (the `pyperclip` package can help)
2. **Avoid look-alike characters** — add `--no-ambiguous` to skip `0`, `O`, `1`, `l`, and `I`
3. **Passphrases** — build passwords from random words, like `correct-horse-battery-staple`
4. **Password checker** — add a command that rates a password you type in
5. **Custom symbols** — add `--symbols "!@#"` for sites that allow only some symbols
