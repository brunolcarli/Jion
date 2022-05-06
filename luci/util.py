"""
Utilities module.
"""
from operator import length_hint
from string import ascii_lowercase, punctuation
from luci.models import Message, Quote, Word


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


def populate_word_table():
    """
    Create Word records on database from all messages and quotes registered
    o database.
    Words must be all lowercase.
    Word must be a single token.
    Word cannot contain or be:
        - puncts
        - special characters
        - spaces
        - numbers
    
    So it is necessary to preprocess all entries before saving.
    """
    messages = [CompressedString.decompress_bytes(m.text)
                for m in Message.objects.all()]
    messages = messages + [CompressedString.decompress_bytes(q.quote)
                for q in Quote.objects.all()]
    not_vowels = [i for i in ascii_lowercase if i not in 'aeiou']
    words = set()

    for message in messages:
        tokens = message.lower().split()
        for token in tokens:
            token = token.strip()

            if not token[0].isalpha():
                token = token.replace(token[0], '')
            if not token:
                continue
            if not token[-1].isalpha():
                token = token.replace(token[-1], '')
            
            if not token.isalpha():
                continue

            if len(token) < 2 and token not in not_vowels:
                words.add(token)
            elif len(token) > 1:
                words.add(token)
    
    print(f'Identified {len(words)} words!')
    for word in list(words):
        obj, is_new = Word.objects.get_or_create(token=word, length=len(word))
        if is_new:
            obj.save()

    print('Done!')
