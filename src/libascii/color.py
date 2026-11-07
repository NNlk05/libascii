class Color:
    def __init__(self, value: str | tuple[int, int, int]) -> None:
        if isinstance(value, tuple):
            if len(value) != 3 or not all(
                isinstance(c, int) and 0 <= c <= 255 for c in value
            ):
                msg = "RGB tuple must contain 3 integers in range 0-255"
                raise ValueError(msg)
            r, g, b = value
            self.value = f"#{r:02x}{g:02x}{b:02x}"
        elif value == "":
            self.value = None
        else:
            self.value = value

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        if not isinstance(hex_str, str) or not hex_str.startswith("#"):
            msg = "hex string must be in format #RRGGBB"
            raise ValueError(msg)
        if len(hex_str) != 7:
            msg = "hex string must be in format #RRGGBB"
            raise ValueError(msg)
        try:
            int(hex_str[1:], 16)
        except ValueError:
            msg = f"invalid hex string: {hex_str!r}"
            raise ValueError(msg) from None
        return cls(hex_str)

    def __str__(self) -> str:
        return self.value if self.value is not None else ""
