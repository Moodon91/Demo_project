from passlib.hash import pbkdf2_sha256

# Function for hashing the password


def hash_password(password):
    return pbkdf2_sha256.hash(password)


# Function for user authentication. Hashes user-inputted password and
# compares it with the one in the database


def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)
