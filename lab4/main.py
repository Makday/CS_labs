import secrets

K_PLUS_BITS = 56

PC2 = [14, 17, 11, 24,  1,  5,
        3, 28, 15,  6, 21, 10,
       23, 19, 12,  4, 26,  8,
       16,  7, 27, 20, 13,  2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

def split_c_d(key: int, len: int = 28):
    mask = ((1 << len) - 1) # is same as 1111_1111_1111_1111_1111_1111_1111
    c = key >> len
    d = key & mask
    return (c,d)

def left_shift(block: int, len: int = 28) -> int:
    mask = (1 << len) - 1
    first_bit = block >> (len - 1)
    return ((block << 1) & mask) | first_bit

SINGLE_SHIFT_ROUNDS = {1, 2, 9, 16}

def left_shift_schedule(c: int, d: int):
    blocks = []
    for i in range(1,17):
        c = left_shift(c)
        d = left_shift(d)
        if i not in SINGLE_SHIFT_ROUNDS:
            c = left_shift(c)
            d = left_shift(d)

        blocks.append((c,d))
    return blocks

def get_bit(seq: int, pos: int, len: int = 56) -> int:
    return (seq >> (len - pos)) & 1

def permute(key: int, table, len: int = 56) -> int:
    subkey = 0
    for pos in table:
        subkey = (subkey << 1) | get_bit(key, pos, len)
    return subkey

def generate_subkeys(blocks, table, len: int = 56):
    subkeys = []
    for block in blocks:
        c,d = block
        combined = c << (len//2) | d
        subkey = permute(combined, table, len)
        subkeys.append(subkey)
    return subkeys

def _show_k_plus(k_plus: int) -> None:
    """Display k_plus in all forms."""
    bits = f"{k_plus:0{K_PLUS_BITS}b}"
    grouped = "_".join(bits[i:i + 7] for i in range(0, K_PLUS_BITS, 7))
    raw = k_plus.to_bytes(K_PLUS_BITS // 8, "big")
    print("\n--- k_plus ---")
    print(f"Binary (56 bits)  : {grouped}")
    print(f"Integer           : {k_plus}")
    print(f"Hex               : 0x{k_plus:014X}")
    print(f"Text (7 chars)    : {raw.decode('latin-1')!r}")
    print("--------------\n")


def read_k_plus() -> int:
    """Read (or generate) a 56-bit k_plus. Returns it as an int."""
    while True:
        print("How do you want to provide k_plus?")
        print("  1) Binary string (56 bits, '_' and spaces allowed)")
        print("  2) Integer (decimal, or 0x.. hex, or 0b.. binary prefix)")
        print("  3) Text (exactly 7 characters = 56 bits)")
        print("  4) Generate randomly")
        choice = input("Choice [1-4]: ").strip()

        try:
            if choice == "1":
                s = input("Binary: ").replace("_", "").replace(" ", "")
                if not s or set(s) - {"0", "1"}:
                    raise ValueError("Only the characters 0 and 1 are allowed.")
                if len(s) != K_PLUS_BITS:
                    raise ValueError(f"Got {len(s)} bits, expected {K_PLUS_BITS}.")
                k_plus = int(s, 2)

            elif choice == "2":
                s = input("Integer: ").strip().replace("_", "")
                k_plus = int(s, 0)  # base 0 understands 0x / 0b prefixes
                if not 0 <= k_plus < (1 << K_PLUS_BITS):
                    raise ValueError(f"Value must be between 0 and 2^{K_PLUS_BITS} - 1.")

            elif choice == "3":
                s = input("Text (7 characters): ")
                raw = s.encode("utf-8")
                if len(raw) != K_PLUS_BITS // 8:
                    raise ValueError(
                        f"Got {len(raw)} bytes, expected {K_PLUS_BITS // 8} "
                        "(non-ASCII characters take more than 1 byte)."
                    )
                k_plus = int.from_bytes(raw, "big")

            elif choice == "4":
                k_plus = secrets.randbits(K_PLUS_BITS)
                print("Generated a random k_plus.")

            else:
                raise ValueError("Please choose 1, 2, 3 or 4.")

        except ValueError as e:
            print(f"Invalid input: {e}\n")
            continue

        assert 0 <= k_plus < (1 << K_PLUS_BITS)
        _show_k_plus(k_plus)
        return k_plus

def show_table(name: str, table, cols: int) -> None:
    print(f"\n--- {name} ---")
    for i in range(0, len(table), cols):
        print(" ".join(f"{x:2d}" for x in table[i:i + cols]))
    print()

if __name__ == "__main__":
    #k_plus = int("1111000_0110011_0010101_0101111_0101010_1011001_1001111_0001111",2)
    k_plus = read_k_plus()

    # Tables used in the flow
    show_table("Left-shift schedule (rounds 1-16)",
               [1 if i in SINGLE_SHIFT_ROUNDS else 2 for i in range(1, 17)], 16)
    show_table("PC-2 (56 -> 48 bits)", PC2, 6)

    # Step 1: split k_plus into C0 / D0
    c, d = split_c_d(k_plus)
    print(f"C0 = {c:028b}")
    print(f"D0 = {d:028b}\n")

    # Step 2: shifted C_n / D_n for each round
    c_d_list = left_shift_schedule(c, d)
    for i, (ci, di) in enumerate(c_d_list, 1):
        shifts = 1 if i in SINGLE_SHIFT_ROUNDS else 2
        print(f"Round {i:2d} (left shift by {shifts})")
        print(f"  C{i:<2d}  = {ci:028b}")
        print(f"  D{i:<2d}  = {di:028b}")
        print(f"  C{i}D{i} = {ci:028b}{di:028b}")

    # Step 3: apply PC-2 to each C_nD_n to get K_n
    print("\n--- Subkeys (PC-2 applied to CnDn) ---")
    subkeys = generate_subkeys(c_d_list, PC2)
    for i, subkey in enumerate(subkeys, 1):
        print(f"K{i:<2d} = {subkey:048b}")