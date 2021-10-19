from secrets import randbits
from math import gcd


def generate_Prime():
    prime = False
    num = randbits(32)
    while not prime:
        if isPrime(num):
            prime = True
        else:
            num = randbits(32)
    return num


def generate_E(nTot):
    valid = False
    num = randbits(7)
    while not valid:
        if gcd(num, nTot) == 1 and 1 < num < nTot:
            valid = True
        else:
            num = randbits(7)
    return num


def isPrime(n):
    if n < 100000: return False
    if n < 2 or n % 2 == 0: return False
    if n % 3 == 0: return False
    r = int(n ** 0.5)
    f = 5
    while f <= r:
        if n % f == 0: return False
        if n % (f + 2) == 0: return False
        f += 6
    return True


def get_Factors(n):
    factors = set()
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.update([i, n // i])
    return factors


def find_LCM(num1, num2):
    return abs(num1 * num2) // gcd(num1, num2)


def MMI(a, m):
    m0 = m
    y = 0
    x = 1
    while a > 1:
        q = a // m
        t = m

        m = a % m
        a = t
        t = y

        y = x - q * y
        x = t

    if x < 0:
        x = x + m0

    return x


def arrayToString(arr):
    mes = ""
    for char in arr:
        mes += char
    return mes


class RSA:

    def __init__(self):
        p = generate_Prime()
        q = generate_Prime()
        n = p * q
        nTot = find_LCM(p - 1, q - 1)
        e = generate_E(nTot)
        d = MMI(e, nTot)
        self.public = (n, e)
        self.private = (n, d)
        self.clientPublic = None

    def encrypt(self, asc):
        return pow(asc, self.clientPublic[1], self.clientPublic[0])

    def decrypt(self, asc):
        return pow(asc, self.private[1], self.private[0])

    def setClientKey(self, public):
        self.clientPublic = public

    def getPublicKey(self):
        return self.public

    def encryptMes(self, mes):
        cipherText = ""
        for char in mes:
            cipherText += str(self.encrypt(ord(char)))
            cipherText += " "
        cipherText = cipherText.strip()
        return cipherText

    def decryptMes(self, mes):
        plainText = ""
        mes = mes.split(" ")
        for char in mes:
            plainText += chr(self.decrypt(int(char)))
        return arrayToString(plainText.split("29"))

    def encryptFile(self, line):
        cipherText = ""
        for byte in line:
            cipherText += str(self.encrypt(byte))
            cipherText += " "
        cipherText = cipherText.strip()
        return cipherText.encode()

    def decryptFile(self, line):
        plainText = ""
        line = line.decode().split(" ")
        for byte in line:
            plainText += chr(self.decrypt(int(byte)))
        return arrayToString(plainText.split("29")).encode()
