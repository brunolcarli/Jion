"""
Utilities module.
"""


class CompressedString:
    def __init__(self, text: str) -> None:
        self.bit_string = self._compress(text)

    def _compress(self, text: str) -> None:
        """
        Compress the text to bytes type for data storage optimization.
        In pure python, a unique char needs 50  bytes.
        The same char in bytes type needs 34 bytes.
        This is not a great difference, but is a difference.
        """
        return bytes(text.encode('utf-8'))

    def decompress(self) -> str:
        """
        Decompress the byte string to pure string.
        """
        return self.bit_string.decode('utf-8')

    def __repr__(self) -> str:
        """
        Return the string representation of the bit string.
        """
        return repr(self.decompress())

    @staticmethod
    def decompress_bytes(byte_string: bytes) -> str:
        """
        Use this method for decompressing any other byte string whithout
        the need of instantiating the class.
        """
        return byte_string.decode('utf-8')
