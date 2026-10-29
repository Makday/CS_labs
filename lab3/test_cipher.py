from main import encrypt, decrypt, prepare

msg, key = "Școala începe în șapte ani, aaa!", "parolăța"
assert decrypt(encrypt(msg, key), key) == prepare(msg)

msg, key = "aaa bbb c", "cheiesecretă"
assert decrypt(encrypt(msg, key), key) == prepare(msg)

assert encrypt("test mesaj", "parolăța") == encrypt("test mesaj", "PAROLĂȚA")

print("All tests passed")
