import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.core.server import setting_config

from src.log_conf import Logger
LOGGER = Logger.get_logger(__name__)

backend = default_backend()
cipher_iterations = 100
config_password = setting_config['ENCRYPTION_TOKEN']


def _derive_key(password: bytes, salt: bytes, iterations: int = cipher_iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))


def password_encrypt(message: bytes, password: str = config_password, iterations: int = cipher_iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    encrypted = b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )
    LOGGER.info("Message: {} successfully encrypted".format(message.decode()))
    return encrypted


def password_decrypt(token: bytes, password: str = config_password) -> bytes:
    decoded = b64d(token)
    salt, iter_num, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter_num, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)