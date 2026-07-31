from __future__ import annotations

import argparse
import sys

from . import clipboard, generator

DEFAULT_LENGTH = 32
DEFAULT_CLIPBOARD_TIMEOUT = 20


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="password-generator",
        description="Generate cryptographically secure passwords using the OS CSPRNG.",
    )
    parser.add_argument("-l", "--length", type=int, default=DEFAULT_LENGTH)
    parser.add_argument("-n", "--count", type=int, default=1)
    parser.add_argument("--no-lower", action="store_true")
    parser.add_argument("--no-upper", action="store_true")
    parser.add_argument("--no-digits", action="store_true")
    parser.add_argument("--no-symbols", action="store_true")
    parser.add_argument("--exclude-ambiguous", action="store_true")
    parser.add_argument(
        "--no-guarantee",
        action="store_true",
        help="don't force at least one char from each enabled category",
    )
    parser.add_argument(
        "--paranoid",
        action="store_true",
        help=f"auto-set length so entropy >= {generator.QUANTUM_SAFE_MARGIN_BITS} bits",
    )
    parser.add_argument("--show-entropy", action="store_true")
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="copy the password to the clipboard instead of printing it",
    )
    parser.add_argument(
        "--clipboard-timeout",
        type=float,
        default=DEFAULT_CLIPBOARD_TIMEOUT,
        help=f"seconds before the clipboard is auto-cleared, 0 to disable (default {DEFAULT_CLIPBOARD_TIMEOUT})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    groups = generator.build_pool(
        use_lower=not args.no_lower,
        use_upper=not args.no_upper,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
        exclude_ambiguous=args.exclude_ambiguous,
    )
    pool_size = len(set("".join(groups)))

    length = args.length
    if args.paranoid:
        length = max(
            length,
            generator.min_length_for_bits(pool_size, generator.QUANTUM_SAFE_MARGIN_BITS),
        )

    if args.count < 1:
        print(f"error: --count must be >= 1, got {args.count}", file=sys.stderr)
        return 1

    if args.clipboard and args.count != 1:
        print("error: --clipboard only supports a single password (-n 1)", file=sys.stderr)
        return 1

    try:
        if args.clipboard:
            pw = generator.generate_password(
                length=length,
                groups=groups,
                require_each_group=not args.no_guarantee,
            )
            clipboard.copy_with_autoclear(pw, args.clipboard_timeout)
            if args.clipboard_timeout > 0:
                print(f"password copied to clipboard, clearing in {args.clipboard_timeout:.0f}s", file=sys.stderr)
            else:
                print("password copied to clipboard", file=sys.stderr)
        else:
            for _ in range(args.count):
                pw = generator.generate_password(
                    length=length,
                    groups=groups,
                    require_each_group=not args.no_guarantee,
                )
                print(pw)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except clipboard.ClipboardError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.show_entropy:
        bits = generator.entropy_bits(pool_size, length)
        print(f"\npool size: {pool_size} chars | length: {length} | entropy: {bits:.1f} bits", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())