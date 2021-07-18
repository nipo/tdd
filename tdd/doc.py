from .header import Header
from .message import C40Message
from base64 import b32decode

__doc__ = """
Documentation representation.
"""

class TwoDDoc:
    """
    A 2D-Doc document
    """
    def __init__(self,
                 header, message,
                 signature,
                 signed_data = None,
                 extra = None):
        self.header = header
        self.message = message
        self.signature = signature
        self.signed_data = signed_data
        self.extra = extra

    @classmethod
    def from_code(cls, doc):
        """
        Load a 2D-Doc from its ASCII form, as outputted by a barcode reader
        """
        header = Header.from_code(doc)
        if header.mode == "c40":
            data, sign = doc[header.length:].split('\x1f', 1)
            signature = b32decode(sign+"=")
            message = C40Message.from_code(header.perimeter_id, data)
            signed_data = (doc[:header.length]+data).encode("ascii")
        else:
            raise ValueError("Binary code not supported fully yet")

        return cls(header, message, signature,
                   signed_data = signed_data)

    def signature_is_valid(self, keychain):
        """
        Check signature against given keychain. If key is not
        available, KeyError is raised.
        """
        cert = keychain.lookup(self.header.ca_id, self.header.cert_id)
        return cert.pubkey.signature_is_valid(self.signed_data, self.signature)
