from cipher import (
    ALPHABET,
    COLS,
    ROWS,
    MATRIX_LETTERS,
    normalize,
    fold,
    prepare,
    to_digraphs,
    construct_matrix,
    substitute_pair,
    encrypt,
    decrypt,
    check_text,
    make_key_check,
    check_operation,
)

KEY = "parolăța"
# Matrix for KEY (6 rows x 5 cols):
#   P A R O L
#   Ă Ț B C D
#   E F G H I
#   J K M N Q
#   S T U V W
#   X Y Z Â Ș


def check(name, got, expected):
    assert got == expected, f"{name}: got {got!r}, expected {expected!r}"


def pos_of(matrix):
    return {ch: (r, c) for r, row in enumerate(matrix) for c, ch in enumerate(row)}


def pair(a, b, step, key=KEY):
    m = construct_matrix(key)
    return substitute_pair(a, b, pos_of(m), m, step)


# ---- constants ----
check("30 matrix letters", len(MATRIX_LETTERS), 30)
check("rows x cols", ROWS * COLS, 30)

# ---- normalize / fold ----
check("cedilla ş -> ș", normalize("ş"), "ș")
check("cedilla ţ -> ț", normalize("ţ"), "ț")
check("strips ends", normalize("  abc \n"), "abc")
check("fold strips, uppercases", fold("a, b!"), "AB")
check("fold Î -> I", fold("îÎ"), "II")

# ---- matrix ----
m = construct_matrix(KEY)
check("6 rows", len(m), 6)
check("each row 5 cols", all(len(r) == 5 for r in m), True)
check("30 unique letters", len({c for r in m for c in r}), 30)
check("key first", "".join(m[0]) + m[1][0] + m[1][1], "PAROLĂȚ")
check("repeated key letters removed", construct_matrix("aabbccdd")[0][:4], list("ABCD"))
check("no Î in matrix", any("Î" in r for r in m), False)
check("key î == key i", construct_matrix("îîîîîîî"), construct_matrix("iiiiiii"))
check(
    "case-insensitive key", construct_matrix("parolăța"), construct_matrix("PAROLĂȚA")
)

# ---- prepare ----
check("simple", prepare("ab"), "AB")
check("odd padded", prepare("abc"), "ABCX")
check("double letters", prepare("aa"), "AXAY")
check("triple letters", prepare("aaa"), "AXAYAW")
check("î merged with i", prepare("îi"), "IXIY")
check(
    "only even output",
    all(len(prepare(w)) % 2 == 0 for w in ["a", "ab", "abc", "aab", "școala"]),
    True,
)
check(
    "no equal letters in a digraph",
    all(d[0] != d[1] for d in to_digraphs(prepare("aabbccddxxyyww"))),
    True,
)
check("filler never equals neighbour", prepare("xx")[1] != "X", True)
check("punct/spaces ignored", prepare("a b, c."), prepare("abc"))

# ---- the three Playfair rules ----
check("enc row", pair("P", "A", 1), "AR")
check("enc row wrap", pair("L", "P", 1), "PA")
check("enc column", pair("Ă", "P", 1), "EĂ")
check("enc column wrap", pair("X", "P", 1), "PĂ")
check("enc rectangle", pair("P", "B", 1), "RĂ")
check("enc rectangle reversed", pair("B", "P", 1), "ĂR")
check("dec row", pair("A", "R", -1), "PA")
check("dec row wrap", pair("P", "A", -1), "LP")
check("dec column", pair("E", "Ă", -1), "ĂP")
check("dec column wrap", pair("P", "Ă", -1), "XP")
check("dec rectangle", pair("R", "Ă", -1), "PB")

# ---- encrypt / decrypt known vectors ----
check("encrypt pa", encrypt("pa", KEY), "AR")
check("decrypt ar", decrypt("ar", KEY), "PA")
check("encrypt strips and uppercases", encrypt("P A!", KEY), "AR")

# ---- round trips ----
messages = [
    "Școala începe în șapte ani, aaa!",
    "aaa bbb c",
    "a",
    "ab",
    "Țara Românească",
    "Ana are mere.",
    "zzzzzzzz",
    "ăâîșț",
    "Hello, World!",
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
    "a" * 51,
    "Să nu uiți: ț, ș, ă, â și î!",
]
keys = [
    "parolăța",
    "cheiesecretă",
    "ABCDEFG",
    "zzzzzzy",
    "ĂÂÎȘȚab",
    "aaaaaaaaaab",
    "FirstAmendment",
]
for msg in messages:
    for k in keys:
        check(f"round trip {msg!r}/{k}", decrypt(encrypt(msg, k), k), prepare(msg))

# ---- properties ----
check("ciphertext even", len(encrypt("abc", KEY)) % 2, 0)
check(
    "ciphertext letters in matrix",
    set(encrypt("Școala începe", KEY)) <= set(MATRIX_LETTERS),
    True,
)
check(
    "ciphertext != plaintext", encrypt("test mesaj", KEY) != prepare("test mesaj"), True
)
check(
    "different key -> different output",
    encrypt("test mesaj", KEY) != encrypt("test mesaj", "cheiesecretă"),
    True,
)
check(
    "message formatting ignored",
    encrypt("Test mesaj", KEY),
    encrypt("TESTMESAJ!!", KEY),
)
check(
    "key case ignored",
    encrypt("test mesaj", "parolăța"),
    encrypt("test mesaj", "PAROLĂȚA"),
)

# ---- decrypt: input cleaning, paired flag, errors ----
ct = encrypt("Școala începe", KEY)
spaced = " ".join(to_digraphs(ct))
check("decrypt ignores spaces", decrypt(spaced, KEY), decrypt(ct, KEY))
check("decrypt ignores case", decrypt(ct.lower(), KEY), decrypt(ct, KEY))
check(
    "decrypt ignores punctuation", decrypt(ct[:4] + "-" + ct[4:], KEY), decrypt(ct, KEY)
)
check("paired=True", decrypt(ct, KEY, paired=True), to_digraphs(decrypt(ct, KEY)))
try:
    decrypt("abc", KEY)
    raise SystemExit("odd-length ciphertext should raise ValueError")
except ValueError:
    pass
try:
    decrypt("12", KEY)
    raise SystemExit("unknown chars should raise KeyError")
except KeyError:
    pass

# ---- validators ----
check("text ok", check_text("Salut, lume!"), None)
check("text ok romanian", check_text("Școală îți țară"), None)
check("text empty", check_text("") is not None, True)
check("text only punct", check_text("!!! ,,,") is not None, True)
check("text digits rejected", check_text("abc 123") is not None, True)
check("text other script", check_text("привет") is not None, True)
check("text error shows hint", "Allowed" in check_text("abc 123"), True)
check("text cedilla ok after normalize", check_text(normalize("ţară şi")), None)

key_check = make_key_check(7)
check("key ok", key_check("parolăța"), None)
check("key exactly 7", key_check("abcdefg"), None)
check("key 6 too short", key_check("abcdef") is not None, True)
check("key empty", key_check(""), "Key cannot be empty.")
check("key digit", key_check("parola12") is not None, True)
check("key space", key_check("pa rola x") is not None, True)
check("key punct", key_check("parola-x!") is not None, True)
check("key hint shown", "Allowed characters" in key_check("parola12"), True)
check("short and invalid reports both", key_check("a1").count("\n") >= 2, True)
check("custom min_len", make_key_check(3)("abc"), None)

check("op e", check_operation("e"), None)
check("op E", check_operation("E"), None)
check("op encryption", check_operation("Encryption"), None)
check("op d", check_operation("d"), None)
check("op decryption", check_operation("decryption"), None)
check("op invalid", check_operation("x") is not None, True)
check("op empty", check_operation("") is not None, True)

print("All tests passed")
