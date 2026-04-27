import grain
import grain.cli
import grain.services
import grain.domain
import grain.adapters
import grain.validators
import grain.templates


def test_package_importable():
    assert grain is not None


def test_submodules_importable():
    assert grain.cli is not None
    assert grain.services is not None
    assert grain.domain is not None
    assert grain.adapters is not None
    assert grain.validators is not None
    assert grain.templates is not None
