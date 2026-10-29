import string
import unicodedata
from itertools import cycle

ALPHABET = "abcdefghijklmnopqrstuvwxyzăâîșț"
LETTERS = set(ALPHABET + ALPHABET.upper())
STRIP = set(string.whitespace + string.punctuation)
ALLOWED = LETTERS | STRIP
FILLERS = "XYWQ"
COLS = 5

_FIX = str.maketrans("şţŞŢ", "șțȘȚ")
LETTER_HINT = "Allowed: Romanian letters (a–z, ă, â, î, ș, ț), spaces, and punctuation."
OPERATIONS = {"e": "e", "encryption": "e", "d": "d", "decryption": "d"}


# ---------- text helpers ----------


def normalize(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip().translate(_FIX)


def fold(text: str) -> str:
    """Drop whitespace/punctuation, uppercase, and merge Î into I."""
    return "".join(ch for ch in text.upper() if ch not in STRIP).replace("Î", "I")


MATRIX_LETTERS = "".join(dict.fromkeys(fold(ALPHABET)))  # 30 letters
ROWS = len(MATRIX_LETTERS) // COLS


# ---------- input ----------


def ask(prompt: str, validate) -> str:
    """Prompt until validate(value) returns None; otherwise print its error."""
    while True:
        value = normalize(input(prompt))
        error = validate(value)
        if error is None:
            return value
        print(error, end="\n\n")


def check_text(s: str):
    if not s:
        return "Input cannot be empty.\n" + LETTER_HINT
    if bad := sorted(set(s) - ALLOWED):
        return f"Invalid character(s): {bad!r}\n{LETTER_HINT}"
    if not set(s) & LETTERS:
        return "Input must have at least one letter.\n" + LETTER_HINT


def make_key_check(min_len: int):
    def check_key(s: str):
        if not s:
            return "Key cannot be empty."
        errors = []
        if len(s) < min_len:
            errors.append(f"Key must be at least {min_len} characters long.")
        if bad := sorted(set(s) - LETTERS):
            errors.append(f"Invalid character(s): {bad!r}")
            errors.append(f"Allowed characters: {ALPHABET} (case insensitive)")
        return "\n".join(errors) or None

    return check_key


def check_operation(s: str):
    if s.lower() not in OPERATIONS:
        return "Please enter 'e' for encryption or 'd' for decryption."


# ---------- cipher ----------


def prepare(text: str) -> str:
    """Fold the text, split doubled letters with fillers, pad to even length."""
    fillers = cycle(FILLERS)

    def filler(avoid: str) -> str:
        f = next(fillers)
        while f == avoid:
            f = next(fillers)
        return f

    out: list[str] = []
    for ch in fold(text):
        if len(out) % 2 and out[-1] == ch:
            out.append(filler(ch))
        out.append(ch)
    if len(out) % 2:
        out.append(filler(out[-1]))
    return "".join(out)


def to_digraphs(text: str) -> list[str]:
    return [text[i : i + 2] for i in range(0, len(text), 2)]


def construct_matrix(key: str) -> list[list[str]]:
    letters = list(dict.fromkeys(fold(key) + MATRIX_LETTERS))
    return [letters[i : i + COLS] for i in range(0, len(letters), COLS)]


def substitute_pair(a: str, b: str, pos, matrix, step: int) -> str:
    """Playfair step: step=+1 encrypts, step=-1 decrypts."""
    (r1, c1), (r2, c2) = pos[a], pos[b]
    if r1 == r2:
        return matrix[r1][(c1 + step) % COLS] + matrix[r2][(c2 + step) % COLS]
    if c1 == c2:
        return matrix[(r1 + step) % ROWS][c1] + matrix[(r2 + step) % ROWS][c2]
    return matrix[r1][c2] + matrix[r2][c1]


def _substitute(text: str, key: str, step: int) -> str:
    matrix = construct_matrix(key)
    pos = {ch: (r, c) for r, row in enumerate(matrix) for c, ch in enumerate(row)}
    return "".join(
        substitute_pair(a, b, pos, matrix, step) for a, b in to_digraphs(text)
    )


def encrypt(plain_text: str, key: str) -> str:
    return _substitute(prepare(plain_text), key, +1)


def decrypt(encrypted_text: str, key: str, paired: bool = False) -> str | list[str]:
    cipher = fold(encrypted_text)
    if len(cipher) % 2:
        raise ValueError("Ciphertext must have an even number of letters.")
    result = _substitute(cipher, key, -1)
    return to_digraphs(result) if paired else result


# ---------- main ----------

if __name__ == "__main__":
    operation = OPERATIONS[
        ask("Enter operation (e = encrypt, d = decrypt): ", check_operation).lower()
    ]
    text = ask("Enter message: ", check_text)
    key = ask("Enter key: ", make_key_check(7))

    try:
        print(encrypt(text, key) if operation == "e" else decrypt(text, key))
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}")
