#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <fstream>
#include <limits>
#include <cstdlib>
#include <windows.h>

using namespace std;

#include "format.cpp"

static const u32string ALPHABET =
    U"A\u0102\u00C2BCDEFGHI\u00CEJKLMNOPQRS\u0218T\u021AUVWXYZ";

#include "reading.cpp"
#include "encrypt.cpp"

int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    char type = read_operation();
    int key = read_key();
    u32string key2 = read_key2();
    string text = read_text();

    u32string alphabet = build_alphabet(key2, ALPHABET);
    cout<<"The new built alphabet: "<<utf32to8(alphabet)<<'\n';

    if (type == 'd') key = -key;
    cout <<"Result: "<<utf32to8(caesar_encrypt(normalize(text), key, alphabet)) << '\n';
}