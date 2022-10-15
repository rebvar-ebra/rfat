from nacl.signing import SigningKey
from nacl.signing import VerifyKey
import hashlib


def get_hash(object):
    
    return hashlib.sha256(object.encode()).hexdigest()
 



def get_signature(object):
    # Generate a new random signing key
     signing_key = SigningKey.generate()

    # Sign the message with the signing key
     signed_checkpoint = signing_key.sign(str(object).encode())
    # Obtain the verify key for a given signing key
     verify_key = signing_key.verify_key

    # Serialize the verify key to send it to a third party
     public_key = verify_key.encode()

     result = signed_checkpoint +(b'split')+  public_key
     
     return result