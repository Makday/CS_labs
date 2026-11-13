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

if __name__ == "__main__":
    k_plus = int("1111000_0110011_0010101_0101111_0101010_1011001_1001111_0001111",2)
    c,d = split_c_d(k_plus)
    c_d_list = left_shift_schedule(c, d)
    subkeys = generate_subkeys(c_d_list, PC2)
    for subkey in subkeys:
        b = f"{subkey:048b}"
        print(b)