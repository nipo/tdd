"""
Pytest fixtures for 2D-Doc specification tests.
"""
import pytest

from cryptography import x509
from importlib.resources import files
from pathlib import Path

def discover_test_cases(samples_dir: Path):
    """
    Discover all test cases by finding .txt files with matching .yaml files.
    Returns list of (txt_path, yaml_path) tuples.
    """
    test_cases = []
    for txt_file in samples_dir.rglob("*.txt"):
        yaml_file = txt_file.with_suffix(".yaml")
        if yaml_file.exists():
            test_cases.append((txt_file, yaml_file))
    return sorted(test_cases, key=lambda x: str(x[0]))


def pytest_generate_tests(metafunc):
    """
    Dynamically generate test cases from samples directory.
    """
    if "spec_sample" in metafunc.fixturenames:
        samples_dir = Path(__file__).parent / "spec_samples"
        test_cases = discover_test_cases(samples_dir)

        ids = [str(txt.relative_to(samples_dir.parent)) for txt, _ in test_cases]
        metafunc.parametrize("spec_sample", test_cases, ids=ids)


@pytest.fixture
def keychain():
    """
    Load the internal keychain with bundled certificates.
    """
    from tdd.keychain import KeyChain
    test_chains = files('tdd.chains').joinpath('FR000001.der')
    with test_chains.open("rb") as fd:
        test_cert = x509.load_der_x509_certificate(fd.read())
    return KeyChain(certs = {"FR000001": test_cert})
