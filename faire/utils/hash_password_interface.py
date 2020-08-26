from werkzeug.security import generate_password_hash, check_password_hash

class HashPasswordInterface:
    """
    Wraps Hash and Check
    """
    def hash(self, password:str) -> str:
        raise NotImplementedError()

    def check(self, hash:str, password:str) -> bool:
        raise NotImplementedError



