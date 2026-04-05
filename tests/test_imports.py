import forge
import forge.cli
import forge.services
import forge.domain
import forge.adapters
import forge.validators
import forge.templates


def test_package_importable():
    assert forge is not None


def test_submodules_importable():
    assert forge.cli is not None
    assert forge.services is not None
    assert forge.domain is not None
    assert forge.adapters is not None
    assert forge.validators is not None
    assert forge.templates is not None
