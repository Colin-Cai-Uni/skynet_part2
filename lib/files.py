import os
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Verification key
verification_key = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMXG
S37QSfTKnJrz5xX4tQbw9Kz+6Xkjd68ggLM74b0BYoP2RlUIGkZSWPoMWAXYU1k3
NaDanBxIQGUC4eOKbNArXRFZz99ZA75u40I+T7fpyz7wptZsaJz+zLxwVS1xqTiJ
oThADLPp8EQl0t/c92f3zeRrxQ4yWzaHNk1raGy2BlufkRuYLdbunSULsaw8kdTJ
kwULAyOq033CqLLrJtr0JCiEgrASRWUFpbN+h+EwwltelSMpYwwLEusxU36JtJE7
YVRev+bJAVd+KoBXdJp8KHK3PZQf73mCffaZHz6ZGvoUZs0CeV6I+T9kaVH3gwPp
MgI2ZMLCGVl1gkvK8X"""
# Instead of storing files on disk,
# we'll save them in memory for simplicity
filestore = {}
# Valuable data to be sent to the botmaster
valuables = []

###

def save_valuable(data):
    valuables.append(data)

def encrypt_for_master(data):
    # Encrypt the file so it can only be read by the bot master
    key = RSA.importKey(open('skynet_encrypt.public').read())
    cipher = PKCS1_OAEP.new(key)
    encrypted_data = cipher.encrypt(data)
    return encrypted_data

def upload_valuables_to_pastebot(fn):
    # Encrypt the valuables so only the bot master can read them
    valuable_data = "\n".join(valuables)
    valuable_data = bytes(valuable_data, "ascii")
    encrypted_master = encrypt_for_master(valuable_data)

    # "Upload" it to pastebot (i.e. save in pastebot folder)
    f = open(os.path.join("pastebot.net", fn), "wb")
    f.write(encrypted_master)
    f.close()

    print("Saved valuables to pastebot.net/%s for the botnet master" % fn)

###

def verify_file(f):
    # Splits off the first line of the file and verifies that it is an integer
    lines = f.split(bytes("\n", "ascii"), 1)
    first_line = lines.pop(0)
    f = bytes("\n", "ascii").join(lines)
    try:
        size = int(first_line)
    except ValueError:
        return False

    # Hash the file content but not the signature itself
    h = SHA256.new()
    h.update(f[:size])
    
    # Verify that the signature is valid for the file
    key = RSA.importKey(verification_key)
    verifier = PKCS1_PSS.new(key)
    if verifier.verify(h, f[size:]):
        return True
    return False

def process_file(fn, f):
    if verify_file(f):
        # If it was, store it unmodified
        # (so it can be sent to other bots)
        # Decrypt and run the file
        filestore[fn] = f
        print("Stored the received file as %s" % fn)
    else:
        print("The file has not been signed by the botnet master")

def download_from_pastebot(fn):
    # "Download" the file from pastebot.net
    # (i.e. pretend we are and grab it from disk)
    # Open the file as bytes and load into memory
    if not os.path.exists(os.path.join("pastebot.net", fn)):
        print("The given file doesn't exist on pastebot.net")
        return
    f = open(os.path.join("pastebot.net", fn), "rb").read()
    process_file(fn, f)

def p2p_download_file(sconn):
    # Download the file from the other bot
    fn = str(sconn.recv(), "ascii")
    f = sconn.recv()
    print("Receiving %s via P2P" % fn)
    process_file(fn, f)

###

def p2p_upload_file(sconn, fn):
    # Grab the file and upload it to the other bot
    # You don't need to encrypt it only files signed
    # by the botnet master should be accepted
    # (and your bot shouldn't be able to sign like that!)
    if fn not in filestore:
        print("That file doesn't exist in the botnet's filestore")
        return
    print("Sending %s via P2P" % fn)
    sconn.send(fn)
    sconn.send(filestore[fn])

def run_file(f):
    # If the file can be run,
    # run the commands
    pass
