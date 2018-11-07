import random
import bitstring
import base32_crockford

high_bits = random.getrandbits(32)  # pretend it's a 32 bit timestamp


def binarize(hb, lb, flip_lb=False):
    hb = '{0:032b}'.format(hb)
    lb = '{0:032b}'.format(lb)
    if flip_lb:
        lb = lb[::-1]
    return hb, lb


def interleave(a, b):
    return ''.join(map(''.join, zip(b, a)))


assert interleave(
    *binarize(
        0b00000000000000000000000000000000, 0b11111111111111111111111111111111
    )
) == '10' * 32


def encode(val):
    return base32_crockford.encode(val & 0xffffffffffffffff).zfill(13)


def assemble_bits(high_bits, low_bits):
    # a = bitstring.BitArray(uint=(high_bits << 32) + low_bits, length=64)
    # b = bitstring.BitArray(bin=interleave(*binarize(high_bits, low_bits)))
    c = bitstring.BitArray(
        bin=interleave(*binarize(high_bits, low_bits, True))
    )

    print(
        '*', encode(c.int)
    )


print("In the same half-second")
# pretend we're generating keys in the same second
low_bits = random.getrandbits(32)  # randomized sub-second incrementer
for i in range(10):
    low_bits += i  # sub-second increment
    assemble_bits(high_bits, low_bits)

print("--")

print("In different half-second")
# pretend we're generating keys in different seconds
for i in range(10):
    high_bits += 1
    low_bits = random.getrandbits(32)
    assemble_bits(high_bits, low_bits)


# On the subject of what it looks like to interleave bits from a timestamp and
# a randomized counter together:

# (counter portion re-randomized every second)
# 'flip-interleaved' means the counter bits are reversed before interleaving

# Generating in different seconds
# 5Q6GHKNYKSTYX - interleaved: 3FPW7V1B4FMZK - flip-interleaved: 6FKYKKM3N5HZP
# 5Q6GHKRNXE9SQ - interleaved: 2DKYKKM31F1XX - flip-interleaved: 7DPPPK1B4FMXR
# 5Q6GHM7YZ48YA - interleaved: 7FPYQHG30FP26 - flip-interleaved: 373YJK095FKAQ
# 5Q6GHMDD5M8RV - interleaved: 37KMKSG30F2AF - flip-interleaved: 77JPJK09MD6AE
# 5Q6GHMMQ7KHF7 - interleaved: 2DQMQS5917Q1Q - flip-interleaved: 7D7Y6HN1ND79J
# 5Q6GHMTP4B9QH - interleaved: 6DPMJK531DQ99 - flip-interleaved: 65QWPK530D39S
# 5Q6GHN1QZXXZ7 - interleaved: 3DQYQVHBHFQ4N - flip-interleaved: 7D7YPVMBNFQCM
# 5Q6GHN90BQSD7 - interleaved: 352P7SNB17K4X - flip-interleaved: 7D6Y6KN9N724C
# 5Q6GHNGYJXGS3 - interleaved: 2FPW6VH90F355 - flip-interleaved: 756PJHMBH5KFG
# 5Q6GHNY258Z20 - interleaved: 656MKK0BN565A - flip-interleaved: 253M7VG34D35B

# Generating inside the same second (no re-randomize call)
# 5Q6GHKDSJ4E6E - interleaved: 3F3W6HG3M5MPY - flip-interleaved: 3F3W3V0915MPY
# 5Q6GHKDSJ4E6F - interleaved: 3F3W6HG3M5MPZ - flip-interleaved: 7F3W3V0915MPY
# 5Q6GHKDSJ4E6H - interleaved: 3F3W6HG3M5MWB - flip-interleaved: 65KW3V0915MPY
# 5Q6GHKDSJ4E6M - interleaved: 3F3W6HG3M5MWT - flip-interleaved: 2DKW3V0915MPY
# 5Q6GHKDSJ4E6R - interleaved: 3F3W6HG3M5MYA - flip-interleaved: 27KW3V0915MPY
# 5Q6GHKDSJ4E6X - interleaved: 3F3W6HG3M5MYV - flip-interleaved: 6FKW3V0915MPY
# 5Q6GHKDSJ4E73 - interleaved: 3F3W6HG3M5NMF - flip-interleaved: 757W3V0915MPY
# 5Q6GHKDSJ4E7A - interleaved: 3F3W6HG3M5NPE - flip-interleaved: 377W3V0915MPY
# 5Q6GHKDSJ4E7J - interleaved: 3F3W6HG3M5NWE - flip-interleaved: 35QW3V0915MPY
# 5Q6GHKDSJ4E7V - interleaved: 3F3W6HG3M5NYF - flip-interleaved: 77QW3V0915MPY
