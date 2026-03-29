from cryptography import x509
from cryptography.x509.oid import NameOID
from pathlib import Path

__doc__ = "Keychain management"

USER_CHAINS_DIR = Path.home() / ".config" / "tdd" / "chains"

class KeyChain:
    """
    Certificate store, indexes certificates through common name of
    issuer and subject. This is somehow 2D-Doc specific.
    """
    def __init__(self):
        self.certs = []

    @staticmethod
    def _cn(name):
        """Extract common name from an x509 Name."""
        attrs = name.get_attributes_for_oid(NameOID.COMMON_NAME)
        return attrs[0].value if attrs else None

    def lookup(self, ca_cn, cert_cn):
        """
        Find a certificate by CA and subject common names.
        Verifies the certificate is signed by the CA before returning.
        Raises KeyError if certificate or CA not found.
        """
        cert = None
        ca = None
        for c in self.certs:
            subject_cn = self._cn(c.subject)
            issuer_cn = self._cn(c.issuer)
            if issuer_cn == ca_cn and subject_cn == cert_cn:
                cert = c
            if subject_cn == ca_cn:
                ca = c
            if cert is not None and ca is not None:
                break

        if cert is None:
            raise KeyError((ca_cn, cert_cn))

        if ca is not None:
            cert.verify_directly_issued_by(ca)

        return cert

    def der_multipart_load(self, fd):
        boundary = b"--End\r\n"
        end = b"--End--"
        blob = fd.read()
        blob = blob.split(end)[0]
        certs = blob.split(boundary)

        for c in certs:
            if c.endswith(b'\r\n'):
                c = c[:-2]
            if not c:
                continue
            header, data = c.split(b'\r\n\r\n', 1)
            header_lines = header.split(b'\r\n')
            ct = None
            for h in header_lines:
                k, v = str(h, 'utf-8').split(": ", 1)
                if k.lower() == "content-type":
                    ct = v
            if ct == "application/pkix-cert":
                self.der_add(data)

    def der_add(self, der):
        try:
            cert = x509.load_der_x509_certificate(der)
        except ValueError:
            return
        self.certs.append(cert)

def internal():
    """
    Spawn a keychain with all built-in certificates loaded,
    then load any user-provisioned certificates from ~/.config/tdd/chains/.
    """
    from importlib.resources import files

    k = KeyChain()

    # Load bundled certificate chains
    chains = files('tdd.chains')
    for chain in ["FR01", "FR02", "FR03", "FR04", "FR05"]:
        chain_file = chains.joinpath(chain + ".der")
        with chain_file.open('rb') as fd:
            k.der_multipart_load(fd)
    with chains.joinpath("FR00.der").open('rb') as fd:
        k.der_add(fd.read())

    # Load user-provisioned certificates
    if USER_CHAINS_DIR.is_dir():
        for der_file in sorted(USER_CHAINS_DIR.glob("*.der")):
            k.der_add(der_file.read_bytes())

    return k

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        k = internal()
    else:
        k = KeyChain()
        for fn in sys.argv[1:]:
            k.der_multipart_load(open(fn, 'rb'))

    for c in k.certs:
        print(k._cn(c.issuer), k._cn(c.subject))
