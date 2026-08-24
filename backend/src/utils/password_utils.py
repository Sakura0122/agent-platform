from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    对密码进行哈希处理。

    Args:
        password: 明文密码。

    Returns:
        哈希后的密码字符串。
    """
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配。

    Args:
        password: 明文密码。
        encoded_hash: 已存储的密码哈希值。

    Returns:
        如果密码匹配则返回 True，否则返回 False。
    """
    return password_hash.verify(password, encoded_hash)
