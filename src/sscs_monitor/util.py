# util.py

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, ec, rsa


def extract_public_key(cert_bytes):
    """
    Extracts the public key from a PEM-encoded certificate.
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_bytes)
        return cert.public_key()
    except Exception as e:
        raise ValueError(f"Failed to extract public key: {e}") from e


def verify_artifact_signature(public_key, signature, artifact_bytes):
    """
    Verifies the signature of the artifact using the provided public key.
    Raises an exception if verification fails.
    """
    try:
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature, artifact_bytes, padding.PKCS1v15(), hashes.SHA256()
            )
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, artifact_bytes, ec.ECDSA(hashes.SHA256()))
        else:
            raise TypeError("Unsupported public key type")
    except Exception as e:
        raise ValueError(f"Signature verification failed: {e}") from e
