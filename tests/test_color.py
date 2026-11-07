from libascii import Color


def test_from_hex_string() -> None:
    assert Color("#ff0000").value == "#ff0000"


def test_from_rgb_tuple() -> None:
    assert Color((255, 0, 0)).value == "#ff0000"
    assert Color((0, 255, 0)).value == "#00ff00"
    assert Color((0, 0, 255)).value == "#0000ff"


def test_from_none() -> None:
    assert Color(None).value is None


def test_from_empty_string() -> None:
    assert Color("").value is None


def test_from_hex_classmethod() -> None:
    assert Color.from_hex("#00ff00").value == "#00ff00"
    assert Color.from_hex("#0000ff").value == "#0000ff"


def test_str() -> None:
    assert str(Color("red")) == "red"
    assert str(Color(None)) == ""
    assert str(Color((255, 0, 0))) == "#ff0000"


def test_eq() -> None:
    assert Color("red") == Color("red")
    assert Color("#ff0000") == Color((255, 0, 0))
    assert Color("red") != Color("blue")
    assert Color(None) != Color("red")


def test_hash() -> None:
    assert hash(Color("red")) == hash(Color("red"))
    assert hash(Color("red")) != hash(Color("blue"))


def test_repr() -> None:
    assert repr(Color("red")) == "Color('red')"
    assert repr(Color(None)) == "Color(None)"
    assert repr(Color((255, 0, 0))) == "Color('#ff0000')"


def test_invalid_rgb_raises() -> None:
    for bad in [
        (256, 0, 0),
        (0, -1, 0),
        (0, 0, 256),
        (0, 0),
        (0, 0, 0, 0),
        ("a", "b", "c"),
    ]:
        try:
            Color(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad!r}")


def test_invalid_hex_raises() -> None:
    for bad in ["ff0000", "#gg0000", "#ff00", "#ff00000", 123]:
        try:
            Color.from_hex(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad!r}")
