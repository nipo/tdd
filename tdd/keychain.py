from Crypto.Util import asn1

__doc__ = "Keychain management"

der_obj = lambda x: asn1.DerObject().decode(x).payload
der_seq = lambda x: asn1.DerSequence().decode(x)
der_set = lambda x: asn1.DerSetOf().decode(x)
der_oid = lambda x: asn1.DerObjectId().decode(x).value
der_int = lambda x: asn1.DerInteger().decode(x)
#der_str = lambda x: asn1.DerOctetString().decode(x)
der_str = lambda x: str(asn1.DerObject().decode(x).payload, "utf-8")
der_bits = lambda x: asn1.DerBitString().decode(x).value

class PublicKey:
    """
    A public key store. Only NIST P-256 is supported for now.
    """
    id_prime256v1 = "1.2.840.10045.3.1.7"
    id_ecPublicKey = "1.2.840.10045.2.1"

    def __init__(self, type, value):
        self.type = type
        self.key = value

    @classmethod
    def from_der(cls, data):
        from Crypto.PublicKey import ECC

        type, key = der_seq(data)
        pub_priv, algo = der_seq(type)
        pub_priv = der_oid(pub_priv)
        try:
            algo = der_oid(algo)
        except ValueError:
            algo = der_seq(algo)

        if pub_priv != cls.id_ecPublicKey:
            raise ValueError("Not a public key")
        if algo == cls.id_prime256v1:
            type = 'p256v1'

        return cls(type, ECC.import_key(data))

    def signature_is_valid(self, data, signature):
        from Crypto.Signature import DSS
        from Crypto.Hash import SHA256

        verifier = DSS.new(self.key, 'deterministic-rfc6979')
        try:
            verifier.verify(SHA256.new(data), signature)
            return True
        except:
            return False

class Dn:
    """
    X-509 Certificate DN low-tech parser/container
    """
    def __init__(self, **kw):
        self.__values = kw

    def __getitem__(self, name):
        return self.__values[name]

    def __setitem__(self, name, value):
        self.__values[name] = value


    oids = {
        "2.5.4.3": "commonName",
        "2.5.4.4": "surname",
        "2.5.4.5": "serialNumber",
        "2.5.4.6": "countryName",
        "2.5.4.7": "localityName",
        "2.5.4.8": "stateOrProvinceName",
        "2.5.4.9": "streetAddress",
        "2.5.4.10": "organizationName",
        "2.5.4.11": "organizationalUnitName",
        "2.5.4.12": "title",
        "2.5.4.13": "description",
        "2.5.4.14": "searchGuide",
        }

    @classmethod
    def from_der(cls, data):
        kv = {}
        for item in der_seq(data):
            s = der_seq(der_set(item)[0])
            oid = der_oid(s[0])
            try:
                k = cls.oids[oid]
            except KeyError:
                continue
            kv[k] = der_str(s[1])

        return cls(**kv)
        
class Certificate:
    """
    X-509 Certificate DN low-tech parser. Does not verify cert signature.
    """
    def __init__(self, issuer, subject, pubkey):
        self.issuer = issuer
        self.subject = subject
        self.pubkey = pubkey

    @classmethod
    def from_der(cls, data):
        from Crypto.PublicKey import ECC

        der = der_seq(data)

        payload = der_seq(der[0])
        info = der[1]
        sign = der[2]

        fields = list(payload)
        while not isinstance(fields[0], int):
            if fields[0][0] & 0xc0 == 0:
                break
            fields.pop(0)

        serial = fields[0]
        signature = der_seq(fields[1])
        issuer = Dn.from_der(fields[2])
        subject = Dn.from_der(fields[4])
        pubkey = PublicKey.from_der(fields[5])

        return cls(issuer, subject, pubkey)

class KeyChain:
    """
    Certificate store, indexes certificates through common name of
    issuer and subject. This is somehow 2D-Doc specific.
    """
    def __init__(self, certs = []):
        self.certs = list(certs)

    def lookup(self, ca_cn, cert_cn):
        for c in self.certs:
            if c.issuer["commonName"] == ca_cn and \
               c.subject["commonName"] == cert_cn:
                return c

        raise KeyError((ca_cn, cert_cn))

    def der_multipart_load(self, fd):
        boundary = b"--End\r\n"
        end = b"--End--"
        blob = fd.read()
        blob = blob.split(end)[0]
        certs = blob.split(boundary)

        for i, c in enumerate(certs):
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
            cert = Certificate.from_der(der)
        except ValueError:
            return
        self.certs.append(cert)

def internal():
    """
    Spawn a keychain with all built-in certificated loaded.
    """
    import pkg_resources

    k = KeyChain()
    for chain in ["FR01", "FR02", "FR03", "FR04"]:
        chain_name = "chains/" + chain + ".der"
        fd = pkg_resources.resource_stream(__name__, chain_name)
        k.der_multipart_load(fd)
    fd = pkg_resources.resource_stream(__name__, "chains/FR00.der")
    k.der_add(fd.read())
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
        print(c.issuer["commonName"], c.subject["commonName"])
