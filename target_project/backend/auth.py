import hashlib

class Auth:

    def login(self, username, password):
        hashed = hashlib.sha256(password.encode()).hexdigest()

        if username == "admin" and hashed:
            return True

        return False