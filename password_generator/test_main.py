"""Tests for the password generator. Run them with:  python -m unittest -v"""

import contextlib
import io
import math
import subprocess
import sys
import unittest
from pathlib import Path

import main

MAIN_PATH = Path(__file__).with_name("main.py")
REPEAT = 300  # the generator is random, so each check is repeated many times


def run_cli(*argv):
    """Run main() with the given arguments and return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class BuildPoolsTests(unittest.TestCase):
    def test_default_uses_all_four_sets(self):
        self.assertEqual(
            main.build_pools(),
            [main.LOWERCASE, main.UPPERCASE, main.DIGITS, main.SYMBOLS],
        )

    def test_lowercase_is_always_included(self):
        self.assertEqual(main.build_pools(False, False, False), [main.LOWERCASE])

    def test_options_remove_sets(self):
        self.assertNotIn(main.UPPERCASE, main.build_pools(use_uppercase=False))
        self.assertNotIn(main.DIGITS, main.build_pools(use_digits=False))
        self.assertNotIn(main.SYMBOLS, main.build_pools(use_symbols=False))


class GeneratePasswordTests(unittest.TestCase):
    def test_length_is_exact_for_every_allowed_length(self):
        pools = main.build_pools()
        for length in range(main.MIN_LENGTH, main.MAX_LENGTH + 1):
            self.assertEqual(len(main.generate_password(length, pools)), length)

    def test_contains_at_least_one_character_of_every_set(self):
        pools = main.build_pools()
        for _ in range(REPEAT):
            # The shortest allowed password is the hardest case for this rule.
            password = main.generate_password(main.MIN_LENGTH, pools)
            for pool in pools:
                self.assertTrue(any(c in pool for c in password), password)

    def test_never_uses_characters_outside_the_chosen_sets(self):
        pools = main.build_pools(use_uppercase=False, use_symbols=False)
        allowed = set(main.LOWERCASE + main.DIGITS)
        for _ in range(REPEAT):
            self.assertLessEqual(set(main.generate_password(20, pools)), allowed)

    def test_letters_only(self):
        pools = main.build_pools(use_digits=False, use_symbols=False)
        for _ in range(REPEAT):
            self.assertTrue(main.generate_password(12, pools).isalpha())

    def test_length_shorter_than_number_of_sets_is_rejected(self):
        with self.assertRaises(ValueError):
            main.generate_password(3, main.build_pools())

    def test_passwords_are_different_each_time(self):
        pools = main.build_pools()
        passwords = {main.generate_password(16, pools) for _ in range(REPEAT)}
        self.assertEqual(len(passwords), REPEAT)

    def test_every_character_can_appear_in_every_position(self):
        # A quick check that the shuffle works: with 1 guaranteed digit and
        # 1 filler letter, a digit must show up in both positions sometimes.
        pools = [main.LOWERCASE, main.DIGITS]
        first_is_digit = {
            main.generate_password(2, pools)[0] in main.DIGITS for _ in range(REPEAT)
        }
        self.assertEqual(first_is_digit, {True, False})


class StrengthTests(unittest.TestCase):
    def test_entropy_matches_the_formula(self):
        self.assertAlmostEqual(
            main.entropy_bits(10, [main.LOWERCASE]), 10 * math.log2(26)
        )
        self.assertAlmostEqual(
            main.entropy_bits(16, main.build_pools()), 16 * math.log2(26 + 26 + 10 + 23)
        )

    def test_longer_means_stronger(self):
        pools = main.build_pools()
        self.assertGreater(main.entropy_bits(20, pools), main.entropy_bits(10, pools))

    def test_label_thresholds(self):
        self.assertEqual(main.strength_label(0), "Weak")
        self.assertEqual(main.strength_label(39.9), "Weak")
        self.assertEqual(main.strength_label(40), "Fair")
        self.assertEqual(main.strength_label(59.9), "Fair")
        self.assertEqual(main.strength_label(60), "Strong")
        self.assertEqual(main.strength_label(79.9), "Strong")
        self.assertEqual(main.strength_label(80), "Very strong")

    def test_default_password_is_rated_very_strong(self):
        bits = main.entropy_bits(main.DEFAULT_LENGTH, main.build_pools())
        self.assertEqual(main.strength_label(bits), "Very strong")


class CommandLineTests(unittest.TestCase):
    def test_default_prints_one_16_character_password(self):
        code, out, err = run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertEqual(len(out.strip()), main.DEFAULT_LENGTH)
        self.assertIn("Strength: Very strong", err)

    def test_strength_goes_to_stderr_not_stdout(self):
        _, out, err = run_cli()
        self.assertNotIn("Strength", out)
        self.assertIn("Strength", err)

    def test_length_and_count_options(self):
        code, out, _ = run_cli("-l", "24", "-c", "5")
        lines = out.splitlines()
        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 5)
        self.assertTrue(all(len(line) == 24 for line in lines))
        self.assertEqual(len(set(lines)), 5)

    def test_long_option_names(self):
        _, out, _ = run_cli("--length", "8", "--count", "2")
        self.assertEqual([len(line) for line in out.splitlines()], [8, 8])

    def test_flags_remove_character_sets(self):
        _, out, _ = run_cli(
            "--no-upper", "--no-digits", "--no-symbols", "-l", "30", "-c", "20"
        )
        for line in out.splitlines():
            self.assertTrue(line.islower() and line.isalpha(), line)

    def test_bounds_are_accepted(self):
        for length in (main.MIN_LENGTH, main.MAX_LENGTH):
            code, out, _ = run_cli("-l", str(length))
            self.assertEqual((code, len(out.strip())), (0, length))
        code, out, _ = run_cli("-c", str(main.MAX_COUNT))
        self.assertEqual((code, len(out.splitlines())), (0, main.MAX_COUNT))

    def test_invalid_values_exit_with_code_2(self):
        bad_arguments = [
            ["-l", "3"],
            ["-l", "129"],
            ["-l", "0"],
            ["-l", "-5"],
            ["-l", "abc"],
            ["-l", "12.5"],
            ["-l"],
            ["-c", "0"],
            ["-c", "51"],
            ["-c", "-1"],
            ["--bogus"],
        ]
        for arguments in bad_arguments:
            with self.subTest(arguments=arguments):
                with (
                    contextlib.redirect_stderr(io.StringIO()),
                    self.assertRaises(SystemExit) as context,
                ):
                    main.main(arguments)
                self.assertEqual(context.exception.code, 2)

    def test_closed_pipe_exits_quietly(self):
        # Simulates `python main.py | head -n 1`: the reader goes away before
        # anything is written. That is normal use, so there must be no traceback.
        command = [sys.executable, str(MAIN_PATH), "-c", "50", "-l", "128"]
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            process.stdout.close()
            stderr = process.stderr.read().decode()
            exit_code = process.wait(timeout=30)
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn("BrokenPipeError", stderr)
        self.assertEqual(exit_code, 0)

    @unittest.skipUnless(Path("/dev/full").exists(), "needs /dev/full (Linux)")
    def test_write_error_prints_a_message_not_a_traceback(self):
        # /dev/full always fails with "No space left on device".
        command = [sys.executable, str(MAIN_PATH)]
        with open("/dev/full", "w") as full:
            result = subprocess.run(
                command, stdout=full, stderr=subprocess.PIPE, timeout=30, check=False
            )
        stderr = result.stderr.decode()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error: cannot write output", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_invalid_values_print_a_message_and_no_password(self):
        out, err = io.StringIO(), io.StringIO()
        with (
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
            self.assertRaises(SystemExit),
        ):
            main.main(["-l", "3"])
        self.assertEqual(out.getvalue(), "")
        self.assertIn("length must be between 4 and 128", err.getvalue())


if __name__ == "__main__":
    unittest.main()
