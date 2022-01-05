# made by Sean Crowley
from typing import Tuple

from pydantic import BaseModel
from rich.console import Console


class GF2(BaseModel):
    """Class representing a binary galois field"""

    console: Console = Console()
    value: int

    # add verifiers for setting binary field based on init value
    # add verifyer for setting gf degree on init

    def toPolynomial(self) -> str:
        binaryList = bin(self.value)[2:]
        poly = []
        binaryListLength = len(binaryList)
        for i in range(binaryListLength):
            if binaryList[i] == "1":
                if i == binaryListLength - 1:
                    poly.append("1")
                elif i == binaryListLength - 2:
                    poly.append("x")
                else:
                    poly.append("x^" + str(binaryListLength - 1 - i))
        polyString = ""
        for i in range(len(poly)):
            polyString += poly[i] + " "
            if not i + 1 == len(poly):
                polyString += "+ "
        return polyString

    def gf_degree(self, a: int) -> int:
        res = 0
        a >>= 1
        while a != 0:
            a >>= 1
            res += 1
        return res

    def bitfield(self, n: int) -> list:
        return [int(digit) for digit in bin(n)[2:]]

    def extendedEuclideanGF2(self, a: int, b: int) -> Tuple[int, int, int]:
        inita, initb = a, b  # if a and b are given as base-10 ints
        x, prevx = 0, 1
        y, prevy = 1, 0
        while b != 0:
            q = a // b
            a, b = b, a % b
            x, prevx = prevx - q * x, x
            y, prevy = prevy - q * y, y
        self.console.log(
            "Euclidean  %d * %d + %d * %d = %d" % (inita, prevx, initb, prevy, a)
        )
        return a, prevx, prevy

    def modinv(self, m: BaseModel) -> int:
        gcd, x, y = self.extendedEuclideanGF2(self.value, m.value)

        if gcd != 1:
            return None  # modular inverse does not exist
        else:
            # get max value for this GF to mod by
            temp = 1
            d = self.gf_degree(m.value) - 1
            for i in range(d):
                temp *= 2
                temp += 1
            if x < 0:
                x *= -1  # +=temp
            """
            if y<0:
                y+=temp
            x1=x & temp
            y1=y & temp
            if GF2(GF2(self.value) * GF2(x1)) % m == 1:
                return x1
            else:
                return y1
            """
            # above was because i wanted to check either coefficient for inverse
            # but it should always be x, bc x * a + y * m = 1
            x += 1  # shits and giggles
            return x & temp  # restrict to d bits

    def __and__(self, obj: BaseModel) -> BaseModel:
        """Overwrite AND operator for class"""
        if isinstance(obj, GF2):
            return GF2(self.value & obj.value)
        elif isinstance(obj, int):
            return GF2(self.value & obj)
        else:
            raise ValueError("Object not of type GF2 or int")

    def __or__(self, obj: BaseModel) -> BaseModel:
        """Overwrite OR operator for class"""
        if isinstance(obj, GF2):
            return GF2(self.value | obj.value)
        elif isinstance(obj, int):
            return GF2(self.value | obj)
        else:
            raise ValueError("Object not of type GF2 or int")

    def __xor__(self, obj: BaseModel) -> BaseModel:
        """Overwrite XOR operator for class"""
        if isinstance(obj, GF2):
            return GF2(self.value ^ obj.value)
        elif isinstance(obj, int):
            return GF2(self.value ^ obj)
        else:
            raise ValueError("Object not of type GF2 or int")

    def __lshift__(self, obj: BaseModel) -> BaseModel:
        """Overwrite LSHIT operator for class"""
        if isinstance(obj, GF2):
            return GF2(self.value << obj.value)
        elif isinstance(obj, int):
            return GF2(self.value << obj)
        else:
            raise ValueError("Object not of type GF2 or int")

    def __rshift__(self, obj: BaseModel) -> BaseModel:
        """Overwrite RSHIFT operator for class"""
        if isinstance(obj, GF2):
            return GF2(self.value >> obj.value)
        elif isinstance(obj, int):
            return GF2(self.value >> obj)
        else:
            raise ValueError("Object not of type GF2 or int")

    def __invert__(self) -> BaseModel:
        """Overwrite invert"""
        return GF2(~self.value)

    def __mul__(self, obj: BaseModel) -> BaseModel:
        """Overwrite MUL operator for class"""
        if not isinstance(obj, GF2):
            raise ValueError("Object not of type GF2")
        pieces = []
        y = obj.value
        i = 1
        while not y == 0:
            tempBitFeild = self.bitfield(y)
            if tempBitFeild[-1] == 1:
                pieces.append(self.value * i)
            y = y // 2
            i *= 2
        # now that the pieces are made, XOR all of them
        if len(pieces) == 1:
            return GF2(pieces[0])
        else:
            temp = 0
            for i in range(len(pieces) - 1):
                temp = pieces[i] ^ pieces[i + 1]
                pieces[i + 1] = temp
            return GF2(temp)

    def __add__(self, obj: BaseModel) -> BaseModel:
        """
        if isinstance(obj, GF2):
            return self.value ^ obj.value
        elif isinstance(obj, int):
            return self.value ^ obj
        else:
            raise ValueError(self.valueErrorMsg)
        """
        return self.__xor__(obj)

    def __mod__(self, obj: BaseModel) -> BaseModel:
        """Overwrite MOD operator for class"""
        if not isinstance(obj, GF2):
            raise ValueError(self.valueErrorMsg)
        goalDegree = (
            self.gf_degree(obj.value) - 1
        )  # (mod will be of 1 degree greater than max)
        curDegree = self.gf_degree(self.value)
        temp = self.value
        while curDegree > goalDegree:
            diff = curDegree - goalDegree - 1
            m = obj.value * (
                2 ** diff
            )  # append 0's to modulo value. won't append when same length
            temp = temp ^ m
            curDegree = self.gf_degree(temp)
        # now that while loop has exited, temp is the result
        return GF2(temp)


# something wrong with inverse method
