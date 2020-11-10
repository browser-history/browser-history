from .aes import AESBlockModeOfOperation as AESBlockModeOfOperation, AESSegmentModeOfOperation as AESSegmentModeOfOperation, AESStreamModeOfOperation as AESStreamModeOfOperation
from .util import append_PKCS7_padding as append_PKCS7_padding, strip_PKCS7_padding as strip_PKCS7_padding, to_bufferable as to_bufferable
from typing import Any, Optional

PADDING_NONE: str
PADDING_DEFAULT: str

class BlockFeeder:
    def __init__(self, mode: Any, feed: Any, final: Any, padding: Any = ...) -> None: ...
    def feed(self, data: Optional[Any] = ...): ...

class Encrypter(BlockFeeder):
    def __init__(self, mode: Any, padding: Any = ...) -> None: ...

class Decrypter(BlockFeeder):
    def __init__(self, mode: Any, padding: Any = ...) -> None: ...

BLOCK_SIZE: Any

def encrypt_stream(mode: Any, in_stream: Any, out_stream: Any, block_size: Any = ..., padding: Any = ...) -> None: ...
def decrypt_stream(mode: Any, in_stream: Any, out_stream: Any, block_size: Any = ..., padding: Any = ...) -> None: ...
