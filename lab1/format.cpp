
u32string utf8to32(const string& s) {
    u32string result;
    size_t i = 0;
    while (i < s.size()) {
        unsigned char first_byte = s[i];
        int len;
        char32_t cp;
        if      ((first_byte & 0b1000'0000) == 0b0000'0000) { len = 1; cp = first_byte & 0b0111'1111; }  // 0xxxxxxx
        else if ((first_byte & 0b1110'0000) == 0b1100'0000) { len = 2; cp = first_byte & 0b0001'1111; }  // 110xxxxx
        else if ((first_byte & 0b1111'0000) == 0b1110'0000) { len = 3; cp = first_byte & 0b0000'1111; }  // 1110xxxx
        else                                                { len = 4; cp = first_byte & 0b0000'0111; }

        for (int k = 1; k < len && i + k < s.size(); ++k) {
            unsigned char next = s[i + k];
            char32_t cp_next = (next & 0b0011'1111);
            cp = (cp << 6) | cp_next;
        }
        result += cp;
        i += len;
    }
    return result;
}

string utf32to8(const u32string& s) {
    string out;
    for (char32_t cp : s) {
        if (cp < 0x80) {
            out += (char)cp;
        } else if (cp < 0x800) {
            out += (char)(0b1100'0000 | (cp >> 6));
            out += (char)(0b1000'0000 | (cp & 0b0011'1111));
        } else if (cp < 0x10000) {
            out += (char)(0b1110'0000 | (cp >> 12));
            out += (char)(0b1000'0000 | ((cp >> 6) & 0b0011'1111));
            out += (char)(0b1000'0000 | (cp & 0b0011'1111));
        } else {
            out += (char)(0b1111'0000 | (cp >> 18));
            out += (char)(0b1000'0000 | ((cp >> 12) & 0b0011'1111));
            out += (char)(0b1000'0000 | ((cp >> 6) & 0b0011'1111));
            out += (char)(0b1000'0000 | (cp & 0b0011'1111));
        }
    }
    return out;
}

bool is_space(char32_t c) {
    return c == U' ' || c == U'\t' || c == U'\r' || c == 0x00A0;
}

u32string remove_spaces(const u32string& s) {
    u32string result = s;
    size_t k = 0;
    for(size_t i = 0; i < result.size(); i++) {
        if (!is_space(result[i]))
            result[k++] = result[i];
    }
    result.resize(k);
    return result;
}

char32_t cedilla_to_comma(char32_t c) {
    switch (c) {
        case 0x015E: return 0x0218;   // Ş -> Ș
        case 0x015F: return 0x0219;   // ş -> ș
        case 0x0162: return 0x021A;   // Ţ -> Ț
        case 0x0163: return 0x021B;   // ţ -> ț
        case 0x0327: return 0x0326;   // combining cedilla -> combining comma below
    }
    return c;
}

char32_t to_upper_ro(char32_t c) {
    switch (c) {
        case 0x0103: return 0x0102;   // ă -> Ă
        case 0x00E2: return 0x00C2;   // â -> Â
        case 0x00EE: return 0x00CE;   // î -> Î
        case 0x0219: return 0x0218;   // ș -> Ș
        case 0x021B: return 0x021A;   // ț -> Ț
    }
    if (c >= U'a' && c <= U'z') return c - 32;
    return c;
}

char32_t fuse_pair(char32_t base, char32_t mark) {
    struct Fuse { char32_t base, mark, result; };

    static const Fuse FUSES[] = {
        {U'S', 0x0326, 0x0218},
        {U'T', 0x0326, 0x021A},
        {U'A', 0x0302, 0x00C2},
        {U'A', 0x0306, 0x0102},
        {U'I', 0x0302, 0x00CE},
    };

    for (const Fuse& f : FUSES)
        if (f.base == base && f.mark == mark)
            return f.result;
    return 0;
}

u32string fuse(const u32string& s) {
    u32string result;
    result.reserve(s.size());
    for(char32_t c : s) {
        if(!result.empty()) {
            char32_t fused = fuse_pair(result.back(), c);
            if (fused != 0) {
                result.back() = fused;
                continue;
            }
        }
        result += c;
    }
    return result;
}

u32string normalize_letters(const u32string& s) {
    u32string result = s;
    for (char32_t& c : result) {
        c = to_upper_ro(cedilla_to_comma(c));
    }
    return result;
}

u32string normalize(const string& s) {
    return  fuse(normalize_letters(remove_spaces(utf8to32(s))));
}