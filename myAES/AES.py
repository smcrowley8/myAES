# import codecs
from rich.console import Console

from myAES.BinaryGaloisFeild import GF2

# in future, replace all comments with assume with some sort of error checking

"""************************ ISSUE ***************
the _setString methods needto handle ascii values that are no good somehow
"""


class AES:
    # **************** end of cipher stuff ************
    def _setCtString(self, ctList: list) -> None:
        """set cipher text string"""
        tempString = ""
        self.ctString = ""
        for e in ctList:
            if e < 32 or e == 127:
                # get rid of bad chars
                e += 127
            temp = chr(e)
            tempString += temp
        self.ctString = tempString
        self.ctStrings.append(tempString)

    def getCtString(self) -> str:
        """Get cipher text string"""
        strLength = len(self.ctStrings)
        if strLength == 0:
            raise ValueError("no ct string was made, please try again")
        elif strLength == 1:
            return self.ctString
        else:
            ctStr = ""
            for char in self.ctStrings:
                ctStr += char
            return ctStr

    def _setPtString(self, ptList: list) -> None:
        """set plain text String"""
        s = ""
        self.ptString = ""
        for e in ptList:
            if e < 32 or e == 127:
                # get rid of bad chars
                e += 128
            temp = chr(e)
            s += temp
        self.ptString = s
        self.ptStrings.append(s)

    def getPtString(self) -> str:
        """Get plain text string"""
        ptLenth = len(self.ptStrings)
        if ptLenth == 0:
            raise ValueError("no pt string was made, please try again")
        elif ptLenth == 1:
            return self.ptString
        else:
            s = ""
            for e in self.ptStrings:
                s += e
            return s

    # **************** setup stuff ***************
    def makeMat(self, pt: list) -> list:
        """Make a 2d list based off of the bits of the plain text given"""
        # assume pt is a list of bytes
        ptMat = []
        for i in range(4):
            temp = []
            for j in range(4):
                temp.append(pt[i + (4 * j)])
            ptMat.append(temp)
        return ptMat

    # ************ decrypt stuff ***************

    def byteSubInv(self, m: list) -> list:
        """Given a matrix, do..."""
        for i in range(len(m)):
            for j in range(len(m[i])):
                x, y = self.byteToNibbles(m[i][j])
                m[i][j] = self.sboxINV[x][y]
        return m

    def shiftRowInv(self, m: list) -> list:
        """Given a matrix, shift rows up"""
        # first row not effected
        transposedMat = self.transposeMat(m)
        for i in range(1, 4):  # skip first row
            transposedMat[i] = self.shiftRight(transposedMat[i], i)
        # re transpose for future matrix stuff
        workingMat = self.transposeMat(transposedMat)
        return workingMat

    def mixColInv(self, m: list) -> list:
        """given a matrix, perform inverse GF matrix multiplication"""
        """
        coefficient = [
            [GF2(0x0e), GF2(0x0b), GF2(0x0d), GF2(0x09)],
            [GF2(0x09), GF2(0x0e), GF2(0x0b), GF2(0x0d)],
            [GF2(0x0d), GF2(0x09), GF2(0x0e), GF2(0x0b)],
            [GF2(0x0b), GF2(0x0d), GF2(0x09), GF2(0x0e)]
        ]
        """
        coefficient = [
            [14, 11, 13, 9],
            [9, 14, 11, 13],
            [13, 9, 14, 11],
            [11, 13, 9, 14],
        ]
        workingMat = self.GFmatMul(coefficient, m)
        return workingMat

    # ****************** key stuff ****************
    def keyTransform(self, k: list, n: int) -> list:
        """will take a 1d list, left shift it, apply sbox to it"""
        # n = the row being made
        # only called if n%4=0 so no check needed
        t = []
        for ele in k:  # needed for dereferencing
            t.append(ele)
        t = self.shiftLeft(t, 1)
        for i in range(len(t)):
            a, b = self.byteToNibbles(t[i])
            t[i] = self.sbox[a][b]

        # and then the first element is XOR'd with 2^((n-4)/4)
        temp = t[0] ^ (2 ** int(((n - 4) / 4)))
        # check if out of bounds of a single byte
        # if it is out of bounds do i multiply mod by 0b100000000 or do i mod by GF2(8) reduction polynomial?
        t[0] = temp
        return t

    # note
    # the keymat return here is created by rows, so key0=row 0, key1=row 1
    # creating the 40 extra keys will be done by added rows instead of columns
    def generateKeyMat(self, key: list) -> list:
        """given a key, will generate a matrix for AES"""
        if isinstance(key, list):
            keyMat = []
            for i in range(4):
                row = [key[i] for i in range(i * 4, (i * 4) + 4)]
                keyMat.append(row)
            return keyMat
        else:
            raise TypeError(f"key must be a list of ints, got {type(key)}")

    def listXOR(self, a: list, b: list) -> list:
        """XOR of list of bits"""
        # assume of same length
        return [a[i] ^ b[i] for i in range(len(a))]

    # will add 40 rows to keymat and then  transpose it so it's ready for encrypt/decrypt
    def generateKeys(self, key: list) -> list:
        """given a key, will generate future rounds keys"""
        keyMat = self.generateKeyMat(key)
        for n in range(4, 44):  # add 40 rows (should be 4,44)
            a = keyMat[n - 4]
            temp = keyMat
            if n % 4 == 0:
                temp2 = temp[n - 1]
                b = self.keyTransform(temp2, n)
            else:
                b = keyMat[n - 1]
            newRow = self.listXOR(a, b)
            keyMat.append(newRow)
        return keyMat

    def generateRoundKey(self, key: list, round: int) -> list:
        """Generate a rounds key based on the initial key"""
        workingMat = key[4 * round : (4 * round) + 4]
        # transpose?
        return workingMat

    # ************* encryption stuff ****************
    def addRoundKey(self, m: list, key: list) -> list:
        """adds this rounds key to working matrix"""
        answer = []
        for i in range(4):  # always 4?
            temp = []
            for j in range(4):
                temp.append(m[i][j] ^ key[i][j])
            answer.append(temp)
        return answer

    def mixCol(self, m: list) -> list:
        """performs mix column method on working matrix"""
        """
        one=GF2(1)
        two=GF2(2)
        three=GF2(3)
        coefficient=[
            [two, one,one,three],
            [three, two, one, one],
            [one, three, two, one],
            [one, one, three, two]
        ] #this is transposed because i do things with rows instead of columns
        """
        coefficient = [
            [2, 3, 1, 1],
            [1, 2, 3, 1],
            [1, 1, 2, 3],
            [3, 1, 1, 2],
        ]  # not transposed bc matmul will transpose state
        # m=self.toGF(m)
        # time to multiply
        workingMat = self.GFmatMul(coefficient, m)
        return workingMat

    def shiftRow(self, m: list) -> list:
        """shift matrix rows down"""
        # this object internally refers to the matrices as the transpose of what they are conceptually
        # to shit a row one must shift that column instead
        temp = self.transposeMat(m)
        for i in range(1, 4):  # skip first row
            temp[i] = self.shiftLeft(temp[i], i)
        # re transpose for future matrix stuff
        workingMat = self.transposeMat(temp)
        return workingMat

    def byteSub(self, m: list) -> list:
        """do..."""
        for i in range(len(m)):
            for j in range(len(m[i])):
                x, y = self.byteToNibbles(m[i][j])
                m[i][j] = self.sbox[x][y]
        return m

    def encrypt(self, pt: list, key: list, numrounds: int) -> list:
        """perform encryption"""

        """
        #if a string is passed preparation is needed
        if isinstance(pt, str):
            temp_prep = AES_PREP(PT=pt)
            ptList=temp_prep.getPtList()
            if isinstance(ptList[0], list):
                #this means we have a list of lists and must encrypt for each list
                for i in range(len(ptList)-1):
                    #do all but the last one, which will be done here
                    p=ptList.pop(0)
                    self.encrypt(p, key, numrounds)
                #now we set pt so we can use the last list given
                pt=ptList.pop(0)
            elif isinstance(ptList[0], int):
                #this is what we want, now we can continue
                pt=ptList.copy()
            else:
                raise TypeError("pt must be a string or list of bytes, please try again")
        """

        # generate pt matrix for computations
        ptMat = self.transposeMat(self.makeMat(pt))  # makeMat is formatted conceptually

        # the key matrix is made in generate keys
        extendedKeyMat = self.generateKeys(key)
        # ARK on original key
        k0 = self.generateRoundKey(extendedKeyMat, 0)
        workingMat = self.addRoundKey(m=ptMat, key=k0)
        if self.print:
            self.console.log("pt mat")
            self.printHexMatrix(ptMat)
            self.console.log("key 0 ")
            self.printHexMatrix(k0)
            self.console.log("result from initial ARK")
            self.printHexMatrix(workingMat)
        # n-1 rounds for 4 layers (BS, SR, MC, ARK) using round 1 to n-1 key
        # round N: BS, SR, ARK using round N key
        # 128 pt -> 4X4 matrix, each element is a byte
        for i in range(1, numrounds + 1):
            byteSubResult = self.byteSub(workingMat)

            shiftRowResult = self.shiftRow(byteSubResult)

            mixColResult = self.mixCol(shiftRowResult)

            roundKey = self.generateRoundKey(extendedKeyMat, i)
            nextRoundMat = self.addRoundKey(mixColResult, key=roundKey)
            if self.print:
                self.console.log("round ", i, " key")
                self.printHexMatrix(roundKey)
                self.console.log("result from byteSub round ", i)
                self.printHexMatrix(byteSubResult)
                self.console.log("result from shiftRow round ", i)
                self.printHexMatrix(shiftRowResult)
                self.console.log("result from mixCol round ", i)
                self.printHexMatrix(mixColResult)
                self.console.log("result from ARK round ", i)
                self.printHexMatrix(nextRoundMat)

            workingMat = nextRoundMat
        # this is for setting the ct string
        temp = []
        for row in workingMat:
            temp += row
        # make 2d into 1d
        self._setCtString(temp)  # set ctString
        return workingMat  # should first turn workingMat into a string?

    def decrypt(self, ct: list, key: list, numrounds: int) -> list:
        """perform decryption"""

        """
        if isinstance(ct, str):
            temp_prep = AES_PREP(CT=ct)
            ctList=temp_prep.getCtList()
            if isinstance(ctList[0], list):
                #this means we have a list of lists and must encrypt for each list
                for i in range(len(ctList)-1):
                    #do all but the last one, which will be done here
                    c=ctList.pop(0)
                    self.decrypt(c, key, numrounds)
                #now we set pt so we can use the last list given
                ct=ctList.pop(0)
            elif isinstance(ctList[0], int):
                #this is what we want, now we can continue
                ct=ctList.copy()
            else:
                raise TypeError("pt must be a string or list of bytes, please try again")
        """
        # each layer is invertible
        ctMat = self.transposeMat(self.makeMat(ct))  # makeMat is formatted conceptually
        # we want the transpose of the conceptual ptMat

        extendedKeyMat = self.generateKeys(key)

        # ARK on original key
        k0 = self.generateRoundKey(extendedKeyMat, numrounds)
        # if 10 rounds we want the key from k40:k43

        workingMat = self.addRoundKey(m=ctMat, key=k0)  # initial ARK
        # add print check and statements here
        if self.print:
            self.console.log("ct mat")
            self.printHexMatrix(ctMat)
            self.console.log("key 0 ")
            self.printHexMatrix(k0)
            self.console.log("result from initial ARK")
            self.printHexMatrix(workingMat)
        # first round will use key9 (k36:39)
        for i in reversed(range(numrounds)):
            if i > 0 or numrounds == 1:
                IMixColResult = self.mixColInv(workingMat)
                workingMat = IMixColResult

            IShiftRowResult = self.shiftRowInv(workingMat)

            # then inverse bytesub
            IByteSubResult = self.byteSubInv(IShiftRowResult)

            # then add round key
            roundKey = self.generateRoundKey(extendedKeyMat, i)
            IARKresult = self.addRoundKey(IByteSubResult, roundKey)

            workingMat = IARKresult

            # add prints here
            if self.print:
                self.console.log("round ", i, " key")
                self.printHexMatrix(roundKey)
                if i > 0 or numrounds == 1:
                    self.console.log("result from mixCol round ", i)
                    self.printHexMatrix(IMixColResult)
                self.console.log("result from inverse shiftRow round ", i)
                self.printHexMatrix(IShiftRowResult)
                self.console.log("result from inverse byteSub round ", i)
                self.printHexMatrix(IByteSubResult)
                self.console.log("result from ARK round ", i)
                self.printHexMatrix(IARKresult)

        temp = []
        for row in workingMat:
            temp += row
        # make 2d into 1d
        self._setPtString(temp)  # set ctString
        return workingMat

    def __init__(self, printStuff: bool = False) -> None:
        # do something
        self.console = Console()
        self.print = printStuff
        self.mod = 0b100011011

        self.sbox = [
            [
                0x63,
                0x7C,
                0x77,
                0x7B,
                0xF2,
                0x6B,
                0x6F,
                0xC5,
                0x30,
                0x01,
                0x67,
                0x2B,
                0xFE,
                0xD7,
                0xAB,
                0x76,
            ],
            [
                0xCA,
                0x82,
                0xC9,
                0x7D,
                0xFA,
                0x59,
                0x47,
                0xF0,
                0xAD,
                0xD4,
                0xA2,
                0xAF,
                0x9C,
                0xA4,
                0x72,
                0xC0,
            ],
            [
                0xB7,
                0xFD,
                0x93,
                0x26,
                0x36,
                0x3F,
                0xF7,
                0xCC,
                0x34,
                0xA5,
                0xE5,
                0xF1,
                0x71,
                0xD8,
                0x31,
                0x15,
            ],
            [
                0x04,
                0xC7,
                0x23,
                0xC3,
                0x18,
                0x96,
                0x05,
                0x9A,
                0x07,
                0x12,
                0x80,
                0xE2,
                0xEB,
                0x27,
                0xB2,
                0x75,
            ],
            [
                0x09,
                0x83,
                0x2C,
                0x1A,
                0x1B,
                0x6E,
                0x5A,
                0xA0,
                0x52,
                0x3B,
                0xD6,
                0xB3,
                0x29,
                0xE3,
                0x2F,
                0x84,
            ],
            [
                0x53,
                0xD1,
                0x00,
                0xED,
                0x20,
                0xFC,
                0xB1,
                0x5B,
                0x6A,
                0xCB,
                0xBE,
                0x39,
                0x4A,
                0x4C,
                0x58,
                0xCF,
            ],
            [
                0xD0,
                0xEF,
                0xAA,
                0xFB,
                0x43,
                0x4D,
                0x33,
                0x85,
                0x45,
                0xF9,
                0x02,
                0x7F,
                0x50,
                0x3C,
                0x9F,
                0xA8,
            ],
            [
                0x51,
                0xA3,
                0x40,
                0x8F,
                0x92,
                0x9D,
                0x38,
                0xF5,
                0xBC,
                0xB6,
                0xDA,
                0x21,
                0x10,
                0xFF,
                0xF3,
                0xD2,
            ],
            [
                0xCD,
                0x0C,
                0x13,
                0xEC,
                0x5F,
                0x97,
                0x44,
                0x17,
                0xC4,
                0xA7,
                0x7E,
                0x3D,
                0x64,
                0x5D,
                0x19,
                0x73,
            ],
            [
                0x60,
                0x81,
                0x4F,
                0xDC,
                0x22,
                0x2A,
                0x90,
                0x88,
                0x46,
                0xEE,
                0xB8,
                0x14,
                0xDE,
                0x5E,
                0x0B,
                0xDB,
            ],
            [
                0xE0,
                0x32,
                0x3A,
                0x0A,
                0x49,
                0x06,
                0x24,
                0x5C,
                0xC2,
                0xD3,
                0xAC,
                0x62,
                0x91,
                0x95,
                0xE4,
                0x79,
            ],
            [
                0xE7,
                0xC8,
                0x37,
                0x6D,
                0x8D,
                0xD5,
                0x4E,
                0xA9,
                0x6C,
                0x56,
                0xF4,
                0xEA,
                0x65,
                0x7A,
                0xAE,
                0x08,
            ],
            [
                0xBA,
                0x78,
                0x25,
                0x2E,
                0x1C,
                0xA6,
                0xB4,
                0xC6,
                0xE8,
                0xDD,
                0x74,
                0x1F,
                0x4B,
                0xBD,
                0x8B,
                0x8A,
            ],
            [
                0x70,
                0x3E,
                0xB5,
                0x66,
                0x48,
                0x03,
                0xF6,
                0x0E,
                0x61,
                0x35,
                0x57,
                0xB9,
                0x86,
                0xC1,
                0x1D,
                0x9E,
            ],
            [
                0xE1,
                0xF8,
                0x98,
                0x11,
                0x69,
                0xD9,
                0x8E,
                0x94,
                0x9B,
                0x1E,
                0x87,
                0xE9,
                0xCE,
                0x55,
                0x28,
                0xDF,
            ],
            [
                0x8C,
                0xA1,
                0x89,
                0x0D,
                0xBF,
                0xE6,
                0x42,
                0x68,
                0x41,
                0x99,
                0x2D,
                0x0F,
                0xB0,
                0x54,
                0xBB,
                0x16,
            ],
        ]
        self.sboxINV = [
            [
                0x52,
                0x09,
                0x6A,
                0xD5,
                0x30,
                0x36,
                0xA5,
                0x38,
                0xBF,
                0x40,
                0xA3,
                0x9E,
                0x81,
                0xF3,
                0xD7,
                0xFB,
            ],
            [
                0x7C,
                0xE3,
                0x39,
                0x82,
                0x9B,
                0x2F,
                0xFF,
                0x87,
                0x34,
                0x8E,
                0x43,
                0x44,
                0xC4,
                0xDE,
                0xE9,
                0xCB,
            ],
            [
                0x54,
                0x7B,
                0x94,
                0x32,
                0xA6,
                0xC2,
                0x23,
                0x3D,
                0xEE,
                0x4C,
                0x95,
                0x0B,
                0x42,
                0xFA,
                0xC3,
                0x4E,
            ],
            [
                0x08,
                0x2E,
                0xA1,
                0x66,
                0x28,
                0xD9,
                0x24,
                0xB2,
                0x76,
                0x5B,
                0xA2,
                0x49,
                0x6D,
                0x8B,
                0xD1,
                0x25,
            ],
            [
                0x72,
                0xF8,
                0xF6,
                0x64,
                0x86,
                0x68,
                0x98,
                0x16,
                0xD4,
                0xA4,
                0x5C,
                0xCC,
                0x5D,
                0x65,
                0xB6,
                0x92,
            ],
            [
                0x6C,
                0x70,
                0x48,
                0x50,
                0xFD,
                0xED,
                0xB9,
                0xDA,
                0x5E,
                0x15,
                0x46,
                0x57,
                0xA7,
                0x8D,
                0x9D,
                0x84,
            ],
            [
                0x90,
                0xD8,
                0xAB,
                0x00,
                0x8C,
                0xBC,
                0xD3,
                0x0A,
                0xF7,
                0xE4,
                0x58,
                0x05,
                0xB8,
                0xB3,
                0x45,
                0x06,
            ],
            [
                0xD0,
                0x2C,
                0x1E,
                0x8F,
                0xCA,
                0x3F,
                0x0F,
                0x02,
                0xC1,
                0xAF,
                0xBD,
                0x03,
                0x01,
                0x13,
                0x8A,
                0x6B,
            ],
            [
                0x3A,
                0x91,
                0x11,
                0x41,
                0x4F,
                0x67,
                0xDC,
                0xEA,
                0x97,
                0xF2,
                0xCF,
                0xCE,
                0xF0,
                0xB4,
                0xE6,
                0x73,
            ],
            [
                0x96,
                0xAC,
                0x74,
                0x22,
                0xE7,
                0xAD,
                0x35,
                0x85,
                0xE2,
                0xF9,
                0x37,
                0xE8,
                0x1C,
                0x75,
                0xDF,
                0x6E,
            ],
            [
                0x47,
                0xF1,
                0x1A,
                0x71,
                0x1D,
                0x29,
                0xC5,
                0x89,
                0x6F,
                0xB7,
                0x62,
                0x0E,
                0xAA,
                0x18,
                0xBE,
                0x1B,
            ],
            [
                0xFC,
                0x56,
                0x3E,
                0x4B,
                0xC6,
                0xD2,
                0x79,
                0x20,
                0x9A,
                0xDB,
                0xC0,
                0xFE,
                0x78,
                0xCD,
                0x5A,
                0xF4,
            ],
            [
                0x1F,
                0xDD,
                0xA8,
                0x33,
                0x88,
                0x07,
                0xC7,
                0x31,
                0xB1,
                0x12,
                0x10,
                0x59,
                0x27,
                0x80,
                0xEC,
                0x5F,
            ],
            [
                0x60,
                0x51,
                0x7F,
                0xA9,
                0x19,
                0xB5,
                0x4A,
                0x0D,
                0x2D,
                0xE5,
                0x7A,
                0x9F,
                0x93,
                0xC9,
                0x9C,
                0xEF,
            ],
            [
                0xA0,
                0xE0,
                0x3B,
                0x4D,
                0xAE,
                0x2A,
                0xF5,
                0xB0,
                0xC8,
                0xEB,
                0xBB,
                0x3C,
                0x83,
                0x53,
                0x99,
                0x61,
            ],
            [
                0x17,
                0x2B,
                0x04,
                0x7E,
                0xBA,
                0x77,
                0xD6,
                0x26,
                0xE1,
                0x69,
                0x14,
                0x63,
                0x55,
                0x21,
                0x0C,
                0x7D,
            ],
        ]

        self.ctString = ""
        self.ctStrings: list = []
        self.ptString = ""
        self.ptStrings: list = []

    # *****************  data manip stuff ******************

    def GFdot(self, a: list, b: list) -> int:
        """perform dot product on binary galois field objects"""
        # something wrong with logic above
        m = GF2(self.mod)
        first = GF2(GF2(a[0]) * GF2(b[0])) % m
        sec = GF2(GF2(a[1]) * GF2(b[1])) % m
        third = GF2(GF2(a[2]) * GF2(b[2])) % m
        fourth = GF2(GF2(a[3]) * GF2(b[3])) % m
        temp = [first, sec, third, fourth]
        answer = 0
        for i in temp:
            answer = answer ^ i
        return answer

    def getCol(self, m: list, c: int) -> list:
        """get a column from the matrix as a list"""
        # return column c of matrix m (list)
        return [r[c] for r in m]

    def GFmatMul(self, a: list, b: list) -> list:
        """perform matrix multiplication on matrices with GF2 elements"""
        workingMat = []  # answer(i,j)=a[i] dot b[][j]
        b = self.transposeMat(b)
        for i in range(len(a)):  # for each row in a
            temp = []
            for j in range(len(b[0])):  # for each col in b
                # append to temp the product of a[i] and col j in b
                temp.append(self.GFdot(a[i], self.getCol(b, j)))
            workingMat.append(temp)
        workingMat = self.transposeMat(workingMat)
        return workingMat

    def byteToNibbles(self, byte: int) -> tuple:
        """breaks a byte into a tuple of nibbles"""
        s = hex(byte)[2:]  # get rid of 0x
        while len(s) < 2:
            s = "0" + s
        return int(s[0], 16), int(s[1], 16)

    def shiftLeft(self, r: list, n: int) -> list:
        """given a list and number of shifts, performs shifts and returns new list"""
        # shifts row r left n bits
        for i in range(n):
            temp = r.pop(0)
            r.append(temp)
        return r

    def shiftRight(self, r: list, n: int) -> list:
        """given list and number of shifts, perform shifts and return new list"""
        # shifts row r right n bits
        for i in range(n):
            temp = r.pop(-1)
            r.insert(0, temp)
        return r

    def transposeMat(self, m: list) -> list:
        """given a matrix, returns that matrix transposed"""

        workingMat = m.copy()
        workingMat = list(zip(*workingMat))  # this is now a list of tuples
        for i in range(len(workingMat)):
            workingMat[i] = list(
                workingMat[i]
            )  # turn tuples to list so its a proper matrix
        return workingMat

    def printHexMatrix(self, t: list) -> None:
        m = self.transposeMat(t)
        s = ""
        for r in m:
            for e in r:
                temp = hex(e)[2:] + " "
                if len(temp) == 2:
                    temp = "0" + temp
                s += temp
            s += "\n"
        self.console.log(s)
