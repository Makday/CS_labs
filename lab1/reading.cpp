bool read_line_utf8(string& out) {
    HANDLE h = GetStdHandle(STD_INPUT_HANDLE);
    DWORD mode;
    if (!GetConsoleMode(h, &mode))
        return (bool)getline(cin, out);

    wstring wline;
    wchar_t buf[512];
    DWORD n;
    while (true) {
        if (!ReadConsoleW(h, buf, 512, &n, nullptr) || n == 0)
            return false;
        wline.append(buf, n);
        if (wline.back() == L'\n') break;
    }

    if (wline[0] == 0x1A) return false;

    while (!wline.empty() && (wline.back() == L'\r' || wline.back() == L'\n'))
        wline.pop_back();

    if (wline.empty()) { out.clear(); return true; }

    int len = WideCharToMultiByte(CP_UTF8, 0, wline.data(), (int)wline.size(),
                                  nullptr, 0, nullptr, nullptr);
    out.assign(len, '\0');
    WideCharToMultiByte(CP_UTF8, 0, wline.data(), (int)wline.size(),
                        &out[0], len, nullptr, nullptr);
    return true;
}

void discard_line() {
    cin.clear();
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
}

char read_operation() {
    while (true) {
        cout << "Choose operation: Encryption/Decryption (e/d): ";
        char type;
        if (cin >> type) {
            discard_line();
            if (type == 'e' || type == 'd') return type;
        } else if (cin.eof()) {
            exit(1);
        } else {
            discard_line();
        }
        cout << "Invalid operation, use e or d.\n";
    }
}

u32string find_invalid(const u32string& normalized) {
    u32string bad;
    for (char32_t c : normalized) {
        if (ALPHABET.find(c) == u32string::npos &&   // not a letter
            bad.find(c) == u32string::npos)          // not already reported
            bad += c;
    }
    return bad;
}

string describe(const u32string& bad) {
    ostringstream out;
    for (char32_t c : bad) {
        out << "'" << utf32to8(u32string(1, c)) << "' (U+"
            << uppercase << hex << setw(4) << setfill('0') << (unsigned)c << ")  ";
    }
    return out.str();
}

int read_key() {
    const int max_key = (int)ALPHABET.size() - 1;
    while (true) {
        cout << "Enter key [1," << max_key << "]: ";
        string line;
        if (!read_line_utf8(line)) exit(1);          // input closed

        size_t b = line.find_first_not_of(" \t\r");
        size_t e = line.find_last_not_of(" \t\r");
        string s = (b == string::npos) ? "" : line.substr(b, e - b + 1);

        bool ok = !s.empty() && s.size() <= 3;
        for (char ch : s)
            if (ch < '0' || ch > '9') ok = false;

        if (ok) {
            int key = stoi(s);
            if (key >= 1 && key <= max_key) return key;
        }
        cout << "Invalid key, key must be a whole number in the interval [1,"
             << max_key << "].\n";
    }
}

u32string read_key2() {
    const size_t min_len = 7;
    while (true) {
        cout << "Enter second key (Romanian letters only, at least " << min_len << " letters): ";
        string line;
        if (!read_line_utf8(line)) exit(1);

        u32string k = normalize(line);           // uppercase, no spaces, comma-below fixed

        u32string bad = find_invalid(k);
        if (!bad.empty()) {
            cout << "These characters are not in the Romanian alphabet:\n  "
                 << describe(bad) << "\nTry again.\n";
            continue;
        }
        if (k.size() < min_len) {
            cout << "Second key is too short (" << k.size() << " letters), need at least "
                 << min_len << ".\n";
            continue;
        }
        return k;
    }
}

string read_text() {
    while (true) {
        cout << "Enter text: ";
        string text;
        if (!read_line_utf8(text)) exit(1);                  // input closed

        u32string normalized = normalize(text);
        if (normalized.empty()) {
            cout << "Text is empty, try again.\n";
            continue;
        }

        u32string bad = find_invalid(normalized);
        if (bad.empty()) return text;

        cout << "These characters are not in the Romanian alphabet:\n  "
             << describe(bad) << "\nTry again.\n";
    }
}