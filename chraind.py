#!/usr/bin/env python3

import hashlib
import struct
import sys

def eratosthenes():
    """
    Yields the sequence of prime numbers via the Sieve of Eratosthenes

    from http://code.activestate.com/recipes/117119/
    """

    # map composite integers to primes witnessing their compositeness
    D = { 25: [5] }
    yield 2; yield 3; yield 5
    a = 6
    while True:
        for q in (a+1, a+5):
            if q not in D:
                yield q        # not marked composite, must be prime
                D[q*q] = [q]   # first multiple of q not already marked
            else:
                for p in D[q]: # move each witness to its next multiple
                    D.setdefault(p+q,[]).append(p)
                del D[q]       # no longer need D[q], free memory
        a += 6

def primes(x):
    """
    Yields x primes
    """
    n = 0
    for p in eratosthenes():
        n += 1
        yield p
        if n >= x:
            break

def primes_under(k):
    """
    Yields primes that lower than k
    """
    for p in eratosthenes():
        if p < k:
            yield p
        else:
            break

class Chraind(object):
    def __init__(self, data, init_seed, hasher = hashlib.sha256):
        self.hasher = hasher

        if type(init_seed) == str:
            init_seed = init_seed.encode()
        pool = bytearray(hasher(init_seed).digest())
        l = len(pool)
        for p in primes_under(pool[0]):
            pool[p % l] ^= (p * (p + 1)) & 0xff
        self.pool = pool

        self.data = self.shuffle(data)

    def shuffle(self, L, N = 5):
        l = len(L)
        i = 0
        for p in primes_under(len(L) * N):
            p %= l
            L[i], L[p] = L[p], L[i]
            i = (i + 1) % l
        return L

    def mixin(self, content):
        """
        Mixin a integer array into pool

        content     list of integers
        """
        self.pool = self.pool[-3:] + self.pool[:-3]
        l = len(self.pool)
        for i in content:
            self.pool[(i + 3) % l] ^= (i ^ (i - 1)) & 0xff

    def update(self, seed):
        """
        Input the seed data, and shuffle data

        seed        string of seed data
        """
        h = self.hasher(seed.strip().encode()).digest()
        self.mixin(bytearray(h))
        a, b = struct.unpack('II', self.pool[0:16:2])
        l = len(self.data)
        for i in range(10):
            a, b = (a ^ b) % l, (b ^ (a - 1)) % l
            if a > b:
                a, b = b, a
            middle = self.shuffle(self.data[a:b])
            self.data = self.data[b:] + middle + self.data[:a]

    def choose(self, how_many = 1):
        m = 7 * how_many
        P = list(primes(how_many + m))[m:]
        for p in P:
            i = p % len(self.data)
            yield self.data[i]
            del self.data[i]

def main(script, *args):
    try:
        seed_src, data_src, how_many, *_ = args
    except ValueError:
        print('Usage: {} random_seed.txt source_list.txt how-many'.format(
              script), file = sys.stderr)
        return 1

    try:
        how_many = int(how_many)
        if how_many < 0:
            raise ValueError('how_many must be postivie')
    except ValueError as e:
        print('how-many must be a integer ({})'.format(e), file = sys.stderr)
        return 2

    with open(data_src, 'r') as fsrc:
        init_seed = input('Input initialize seed:').strip()
        chraind = Chraind(fsrc.readlines(), init_seed)

    with open(seed_src, 'r') as fseed:
        for seed in fseed:
            chraind.update(seed.strip())

    for i in chraind.choose(how_many):
        print(i.strip())

if __name__ == '__main__':
    exit(main(*sys.argv))
