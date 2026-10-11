"""Password Generator: create strong random passwords from the terminal.

Usage:
    python main.py                  one 16-character password
    python main.py -l 24            a 24-character password
    python main.py -c 5             five passwords
    python main.py --no-symbols     letters and digits only
    python main.py --no-digits --no-symbols   letters only

The passwords are printed to the screen, one per line. A strength estimate is
printed separately, so you can pipe the passwords somewhere else safely.
"""

import argparse
import math
import os
import secrets
import string
import sys

# The character sets a password can be built from.
LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"

DEFAULT_LENGTH = 16
MIN_LENGTH = 4  # room for one character of each of the 4 sets
MAX_LENGTH = 128
MAX_COUNT = 50


def build_pools(use_uppercase=True, use_digits=True, use_symbols=True):
    """Return the list of character sets the password may use.

    Lowercase letters are always included, so the list is never empty.
    """
    pools = [LOWERCASE]
    if use_uppercase:
        pools.append(UPPERCASE)
    if use_digits:
        pools.append(DIGITS)
    if use_symbols:
        pools.append(SYMBOLS)
    return pools


def generate_password(length, pools):
    """Build one random password of the given length.

    It always contains at least one character from every set in `pools`,
    so "use digits" really means the password has a digit in it.
    """
    if length < len(pools):
        raise ValueError(
            f"length must be at least {len(pools)} for these character sets"
        )

    # Step 1: one guaranteed character from each set.
    characters = [secrets.choice(pool) for pool in pools]

    # Step 2: fill the remaining places from all sets together.
    everything = "".join(pools)
    for _ in range(length - len(characters)):
        characters.append(secrets.choice(everything))

    # Step 3: shuffle, so the guaranteed characters are not always at the start.
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def entropy_bits(length, pools):
    """Estimate how hard the password is to guess, in bits.

    Each character picked from N possible characters adds log2(N) bits.
    Every extra bit doubles the number of guesses an attacker needs.
    """
    pool_size = len("".join(pools))
    return length * math.log2(pool_size)


def strength_label(bits):
    """Turn the entropy estimate into a word."""
    if bits < 40:
        return "Weak"
    if bits < 60:
        return "Fair"
    if bits < 80:
        return "Strong"
    return "Very strong"


def print_lines(lines):
    """Print each line and return True if all went well.

    With `python main.py -c 50 | head -n 1`, `head` quits after the first line.
    Printing more then raises BrokenPipeError. That is normal use, so we stop
    quietly and still return True. Any other write error (for example a full
    disk) prints a message and returns False.
    """
    try:
        for line in lines:
            print(line, flush=True)
    except OSError as error:
        # Python would raise the error again while shutting down, so point stdout
        # at /dev/null first. This is the recipe from the Python documentation.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        if isinstance(error, BrokenPipeError):
            return True
        print(f"Error: cannot write output: {error}", file=sys.stderr)
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate strong random passwords.")
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=DEFAULT_LENGTH,
        help=f"password length, {MIN_LENGTH}-{MAX_LENGTH} (default: {DEFAULT_LENGTH})",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        help=f"how many passwords to generate, 1-{MAX_COUNT} (default: 1)",
    )
    # store_false: giving the flag turns a feature OFF.
    # Without the flag the value stays True.
    parser.add_argument(
        "--no-upper",
        dest="use_uppercase",
        action="store_false",
        help="leave out uppercase letters",
    )
    parser.add_argument(
        "--no-digits", dest="use_digits", action="store_false", help="leave out digits"
    )
    parser.add_argument(
        "--no-symbols",
        dest="use_symbols",
        action="store_false",
        help="leave out symbols",
    )
    args = parser.parse_args(argv)

    if not MIN_LENGTH <= args.length <= MAX_LENGTH:
        parser.error(f"length must be between {MIN_LENGTH} and {MAX_LENGTH}")
    if not 1 <= args.count <= MAX_COUNT:
        parser.error(f"count must be between 1 and {MAX_COUNT}")

    pools = build_pools(args.use_uppercase, args.use_digits, args.use_symbols)

    passwords = (generate_password(args.length, pools) for _ in range(args.count))
    if not print_lines(passwords):
        return 1

    bits = entropy_bits(args.length, pools)
    print(f"Strength: {strength_label(bits)} (about {bits:.0f} bits)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
