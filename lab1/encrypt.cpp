u32string build_alphabet(const u32string& k2, const u32string& base) {
    u32string result;
    for (char32_t c : k2)
        if (result.find(c) == u32string::npos) result += c;
    for (char32_t c : base)
        if (result.find(c) == u32string::npos) result += c;
    return result;
}

u32string caesar_encrypt(const u32string& s, int key, const u32string& alphabet) {
    u32string result = s;
    const int n = (int)alphabet.size();
    for (char32_t& c : result) {
        size_t pos = alphabet.find(c);
        if (pos == u32string::npos) continue;
        c = alphabet[((int)pos + key + n) % n];
    }
    return result;
}