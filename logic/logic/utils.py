import string

def simple_gematria(text: str) -> int:
    """
    Suma A=1, B=2... Z=26, ignora espacios.
    """
    text = text.upper()
    letters = string.ascii_uppercase
    value = 0
    for ch in text:
        if ch in letters:
            value += (letters.index(ch) + 1)
    return value
