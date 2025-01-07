from passlib.hash import sha256_crypt

# Ganti 'your_password' dengan password yang ingin Anda hash
password = 'Admin123_'
hashed_password = sha256_crypt.hash(password)
print(hashed_password)  # Salin dan gunakan hash ini untuk database