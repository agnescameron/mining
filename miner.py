import urllib2
import json
import time
from hashlib import sha256 as H
from Crypto.Cipher import AES
import random
import time
from struct import pack, unpack
import requests


NODE_URL = "http://6857coin.csail.mit.edu"

"""
    This is a bare-bones miner compatible with 6857coin, minus the final proof of
    work check. We have left lots of opportunities for optimization. Partial
    credit will be awarded for successfully mining any block that appends to
    a tree rooted at the genesis block. Full credit will be awarded for mining
    a block that adds to the main chain. Note that the faster you solve the proof
    of work, the better your chances are of landing in the main chain.

    Feel free to modify this code in any way, or reimplement it in a different
    language or on specialized hardware.

    Good luck!
"""

def verify_pow(Ai, Aj, Bi, Bj, b):
    """
    B.parentid is the SHA256 Hash of a header in the blockchain.
    B.root is the SHA256 hash of the block contents.
    B.difficulty >= MinimumDifficulty = 86.
    B.timestamp must be less than 2 minutes off from server.
    i != j and the hamming distance Dist(A(i) + B(j) mod 2128, A(j) + B(i) mod 2128) <= 128 - B.difficulty.
    """
    valid = False

    #check hamming distance
    str1 = bin((Ai + Bj)%2**128)[2:]
    str2 = bin((Aj + Bi)%2**128)[2:]
    #print str1
    #print str2
    xor = int(str1, 2)^int(str2, 2)
 #   print xor
    ham_dist = bin(xor).count("1")
#    print ham_dist
    # must better less than 128-difficulty
    if ham_dist <= 128 - b["difficulty"]:
        print ham_dist
        print str1, str2
        valid = True
    return valid

def solve_block(b):
    """
    Iterate over random nonce triples until a valid proof of work is found
    for the block

    Expects a block dictionary `b` with difficulty, version, parentid,
    timestamp, and root (a hash of the block data).

    """
    valid = False
    while valid == False:
        startRand = time.time()
        b["nonces"] = [random.getrandbits(64), random.getrandbits(64), random.getrandbits(64)]
        endRand = time.time()
        #   Compute Ai, Aj, Bi, Bj
        ciphers = compute_ciphers(b)
        endCiph = time.time()
        #   Parse the ciphers as big-endian unsigned integers
        Ai, Aj, Bi, Bj = [unpack_uint128(cipher) for cipher in ciphers]
        endUnpack = time.time()
        #   verify proof of work
        valid = verify_pow(Ai, Aj, Bi, Bj, b)
        endVerify = time.time()

        tRand = endRand - startRand
        tCiph = endCiph - endRand
        tUnpack = endUnpack - endCiph
        tVerify = endVerify - endUnpack

        #print "times are: tRand ", tRand, " tCiph ", tCiph, " tUnpack ", tUnpack, " tVerify ", tVerify

        if valid == True:
            print "valid!"


def main():
    """
    Repeatedly request next block parameters from the server, then solve a block
    containing our team name.

    We will construct a block dictionary and pass this around to solving and
    submission functions.
    """
    block_contents = "agnescam, prela, ampayne"
    while True:
        #   Next block's parent, version, difficulty
        next_header = get_next()
        #   Construct a block with our name in the contents that appends to the
        #   head of the main chain
        print "next header is"
        print next_header
        new_block = make_block(next_header, block_contents)
        #   Solve the POW
        print "Solving block..."
        print new_block
        solve_block(new_block)
        #   Send to the server
        print "Contents:"
        print new_block["root"]
        add_block(new_block, block_contents)


def get_next():
    """
       Parse JSON of the next block info
           difficulty      uint64
           parentid        HexString
           version         single byte
    """
    return json.loads(urllib2.urlopen(NODE_URL + "/next").read())
    #return json.loads(urllib2.urlopen(NODE_URL + "/block/a6b8ef3b1d28145fd475904bd803f6d74fdc8551313194cc6aaa4d358216edb3").read())["header"]

def add_block(h, contents):
    """
       Send JSON of solved block to server.
       Note that the header and block contents are separated.
            header:
                difficulty      uint64
                parentid        HexString
                root            HexString
                timestampe      uint64
                version         single byte
            block:          string
    """
    h["root"] = unicode(h["root"])
    add_block_request = {"header": h, "block": contents}
    print h
    print "Sending block to server..."
    print json.dumps(add_block_request)
    r = requests.post(NODE_URL + "/add", data=json.dumps(add_block_request))
    print r
    print r.content


def hash_block_to_hex(b):
    """
    Computes the hex-encoded hash of a block header. First builds an array of
    bytes with the correct endianness and length for each arguments. Then hashes
    the concatenation of these bytes and encodes to hexidecimal.

    Not used for mining since it includes all 3 nonces, but serves as the unique
    identifier for a block when querying the explorer.
    """
    # h = H()
    # h.update(''.join([b["parentid"].decode('hex'), b["root"].decode('hex'), pack('>Q', long(b["difficulty"])), pack('>Q', long(b["timestamp"])), pack('>Q', long(b["nonces"][0])), pack('>Q', long(b["nonces"][1])), pack('>Q', long(b["nonces"][2]))]))
    # b["hash"] = h.digest().encode('hex')
    # return b["hash"]

    packed_data = []
    packed_data.extend(b["parentid"].decode('hex'))
    packed_data.extend(b["root"].decode('hex'))
    packed_data.extend(pack('>Q', long(b["difficulty"])))
    packed_data.extend(pack('>Q', long(b["timestamp"])))
    #   Bigendian 64bit unsigned
    for n in b["nonces"]:
        #   Bigendian 64bit unsigned
        packed_data.extend(pack('>Q', long(n)))
    packed_data.append(chr(b["version"]))
    if len(packed_data) != 105:
        print "invalid length of packed data"
    h = H()
    h.update(''.join(packed_data))
    b["hash"] = h.digest().encode('hex')
    return b["hash"]



def compute_ciphers(b):
    """
    Computes the ciphers Ai, Aj, Bi, Bj of a block header.
    """
    # h = H()
    # h.update(''.join([b["parentid"].decode('hex'), b["root"].decode('hex'), pack('>Q', long(b["difficulty"])), pack('>Q', long(b["timestamp"])), pack('>Q', long(b["nonces"][0]))]))
    # seed = h.digest()

    # if len(seed) != 32:
    #     print "invalid length of packed data"
    # h = H()
    # h.update(seed)
    # seed2 = h.digest()

    # A = AES.new(seed)
    # B = AES.new(seed2)

    # i = pack('>QQ', 0, long(b["nonces"][1]))
    # j = pack('>QQ', 0, long(b["nonces"][2]))

    # Ai = A.encrypt(i)
    # Aj = A.encrypt(j)
    # Bi = B.encrypt(i)
    # Bj = B.encrypt(j)

    # return Ai, Aj, Bi, Bj

    packed_data = []
    packed_data.extend(b["parentid"].decode('hex'))
    packed_data.extend(b["root"].decode('hex'))
    packed_data.extend(pack('>Q', long(b["difficulty"])))
    packed_data.extend(pack('>Q', long(b["timestamp"])))
    packed_data.extend(pack('>Q', long(b["nonces"][0])))
    packed_data.append(chr(b["version"]))
    if len(packed_data) != 89:
        print "invalid length of packed data"
    h = H()
    h.update(''.join(packed_data))
    seed = h.digest()

    if len(seed) != 32:
        print "invalid length of packed data"
    h = H()
    h.update(seed)
    seed2 = h.digest()

    A = AES.new(seed)
    B = AES.new(seed2)

    i = pack('>QQ', 0, long(b["nonces"][1]))
    j = pack('>QQ', 0, long(b["nonces"][2]))

    Ai = A.encrypt(i)
    Aj = A.encrypt(j)
    Bi = B.encrypt(i)
    Bj = B.encrypt(j)

    return Ai, Aj, Bi, Bj




def unpack_uint128(x):
    h, l = unpack('>QQ', x)
    return (h << 64) + l


def hash_to_hex(data):
    """Returns the hex-encoded hash of a byte string."""
    h = H()
    h.update(data)
    return h.digest().encode('hex')


def make_block(next_info, contents):
    """
    Constructs a block from /next header information `next_info` and sepcified
    contents.
    """
    block = {
        "version": next_info["version"],
        #   for now, root is hash of block contents (team name)
        "root": hash_to_hex(contents),
        "parentid": next_info["parentid"],
        #   nanoseconds since unix epoch
        "timestamp": long(time.time()*1000*1000*1000),
        "difficulty": next_info["difficulty"]
    }
    return block


# def rand_nonce():
#     """
#     Returns a random uint64
#     """
#     return random.getrandbits(64)


if __name__ == "__main__":
    main()