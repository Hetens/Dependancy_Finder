import os
import sys
from OpenSSL import crypto

def test_PKCS7_SIGNER_INFO():
    # Create a PKCS7 object
    p7 = crypto.PKCS7()
    
    # Create a X509 certificate (this will be our signer)
    cert = crypto.X509()
    cert.get_subject().CN = "Test"
    k = crypto.PKey()   
    k.generate_key(crypto.TYPE_RSA, 2048)
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Add a signer
    p7.type_is_signed()
    p7.add_signer(cert)
    
    # Get signer info
    signer_info = p7.get_signer_info()
    
    assert len(signer_info) == 1, "PKCS7_SIGNER_INFO addition failed."
    print("PKCS7_SIGNER_INFO test passed.")

def test_PKCS7_RECIP_INFO():
    # Create a PKCS7 object
    p7 = crypto.PKCS7()
    
    # Create a X509 certificate (this will be our recipient)
    cert = crypto.X509()
    cert.get_subject().CN = "Test Recipient"
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Add a recipient
    p7.type_is_enveloped()
    p7.add_recipient(cert)
    
    # Unfortunately, there's no direct way to get the number of recipients
    # in the Python OpenSSL bindings. We'll check if encryption is possible instead.
    try:
        p7.encrypt(b'Test data')
        print("PKCS7_RECIP_INFO test passed.")
    except Exception as e:
        assert False, f"PKCS7_RECIP_INFO test failed: {str(e)}"

if __name__ == "__main__":
    test_PKCS7_SIGNER_INFO()
    test_PKCS7_RECIP_INFO()
    print("All tests passed successfully.")