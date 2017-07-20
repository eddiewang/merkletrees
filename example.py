#!/usr/bin/env python
# -*- coding: utf-8 -*-

from binascii import hexlify, unhexlify
from pyblake2 import blake2b
import json
from pprint import pprint

# Block 86011
# Hash 000000000000007384ca7ba61a988d14f9a9d731a981c186e8904f1e1d82e6f5
prevhash = '0000000000000079039da6f4d7790d54d774812f92e459387846524f4024afe3'
coinb1 = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000020000000000000004e6f6e536961000000000000000000006aba4dfb5df01095'
coinb2 = '0000000000000000'
merkle_branch = [
    '25cc1c464ed8f0a13da6c14098c2cd47526dcd64d3594a2ace794b9bc0ab704d',
    '2c162ebd012c0044cd34808a0dc9e5790f428cba73ce7b848a6f63ddd845c80e',
    '20283c26aa6cf99c126fe74021f2c5fb39baffd81814d725c57c883e16676c5d',
]
ntime = '2ed1705800000000'
extranonce1 = '99cfbade'
extranonce2 = 'ef7488b3'
nonce = '40371d049700e893'
data = json.load(open('stratum.json'))
transactions = [x["id"] for x in data["block"]["transactions"]]
minerpayoutid = data["block"]["minerpayoutids"][0]
transactions.insert(0, minerpayoutid)
# transactions.append(minerpayoutid)
print("Transaction + Mining Outputs", len(transactions))
arbtx = coinb1 + extranonce1 + extranonce2 + coinb2

result = []


def merkle(transactions):
    temp = []
    if len(transactions) == 1:
        return
    for t in range(1, len(transactions), 2):
        t1 = unhexlify(transactions[t - 1])
        t2 = unhexlify(transactions[t])
        hashedResult = blake2b(b'\x01' + t1 + t2, digest_size=32).digest()
        hashHex = hexlify(hashedResult).encode('ascii')
        temp.append(hashHex)
    # If odd, simply append the transaction value...
    # the way the merkle trees work in Sia is that orphan leaves
    # are not duplicated or hashed multiple times
    # https://github.com/NebulousLabs/merkletree
    #      ┌───┴──┐       ┌────┴───┐         ┌─────┴─────┐
    #   ┌──┴──┐   │    ┌──┴──┐     │      ┌──┴──┐     ┌──┴──┐
    # ┌─┴─┐ ┌─┴─┐ │  ┌─┴─┐ ┌─┴─┐ ┌─┴─┐  ┌─┴─┐ ┌─┴─┐ ┌─┴─┐   │
    #    (5-leaf)         (6-leaf)             (7-leaf)
    if len(transactions) % 2 == 1:
        t3 = transactions[len(transactions) - 1]
        temp.append(t3)
    result.extend(temp)
    merkle(temp)


merkle(transactions)
for t in result:
    for x in merkle_branch:
        if t == x:
            print("merkle branch found")
