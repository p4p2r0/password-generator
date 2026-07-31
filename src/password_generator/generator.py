from __future__ import annotations

import math
import secrets
import string

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?~"
# visual look-alikes (il1Lo0O) plus shell/CSV-hostile punctuation
AMBIGUOUS = "il1LoO0|`'\";:,."

QUANTUM_SAFE_MARGIN_BITS = 256


class PoolExhaustedError(ValueError):
    pass


def build_pool(
    use_lower: bool = True,
    use_upper: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> tuple[str, ...]:
    groups = []
    if use_lower:
        groups.append(LOWER)
    if use_upper:
        groups.append(UPPER)
    if use_digits:
        groups.append(DIGITS)
    if use_symbols:
        groups.append(SYMBOLS)

    if not groups:
        raise PoolExhaustedError("At least one character category must be enabled.")

    if exclude_ambiguous:
        groups = [
            "".join(c for c in g if c not in AMBIGUOUS) or g
            for g in groups
        ]

    return tuple(groups)


def entropy_bits(pool_size: int, length: int) -> float:
    return length * math.log2(pool_size)


def min_length_for_bits(pool_size: int, target_bits: float) -> int:
    return math.ceil(target_bits / math.log2(pool_size))


def generate_password(
    length: int,
    groups: tuple[str, ...],
    require_each_group: bool = True,
) -> str:
    full_pool = "".join(groups)

    if length < 1:
        raise ValueError(f"length must be >= 1, got {length}")

    if require_each_group and length < len(groups):
        raise ValueError(
            f"length ({length}) is too short to guarantee one char from each "
            f"of the {len(groups)} enabled categories"
        )

    if require_each_group:
        chosen = [secrets.choice(g) for g in groups]
        remaining = length - len(chosen)
        chosen += [secrets.choice(full_pool) for _ in range(remaining)]
        # Fisher-Yates shuffle using the CSPRNG, not random.shuffle
        for i in range(len(chosen) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chosen[i], chosen[j] = chosen[j], chosen[i]
        return "".join(chosen)

    return "".join(secrets.choice(full_pool) for _ in range(length))