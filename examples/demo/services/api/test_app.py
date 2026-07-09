from app import add, greeting


def test_greeting_default():
    assert greeting() == "Hello, world!"


def test_greeting_name():
    assert greeting("Northwind") == "Hello, Northwind!"


def test_add():
    assert add(2, 3) == 5
