#made by Sean Crowley
import time
#something wrong with inverse method
class GF2:
    def toPolynomial(self):
        s=bin(self.value)[2:]
        poly=[]
        l=len(s)
        for i in range(l):
            if s[i]=="1":
                if i==l-1:
                    poly.append("1")
                elif i==l-2:
                    poly.append("x")
                else:
                    poly.append("x^"+str(l-1-i))
        ans=""
        for i in range(len(poly)):
            ans+=poly[i]+" "
            if not i+1 == len(poly):
                ans+="+ "
        return ans

    def gf_degree(self,a) :
        res = 0
        a >>= 1
        while (a != 0) :
            a >>= 1;
            res += 1;
        return res
    
    def bitfield(self,n):
        return [int(digit) for digit in bin(n)[2:]]
    
    def extendedEuclideanGF2(self,a, b):
        inita, initb = a, b   # if a and b are given as base-10 ints
        x, prevx = 0, 1
        y, prevy = 1, 0
        while b != 0:
            q = a//b
            a, b = b, a%b
            x, prevx = prevx - q*x, x
            y, prevy = prevy - q*y, y
        print("Euclidean  %d * %d + %d * %d = %d" % (inita, prevx, initb, prevy, a))
        return a, prevx, prevy
    
    def modinv(self, m): 
        gcd, x, y = self.extendedEuclideanGF2(self.value, m.value) 
            
        if gcd != 1: 
            return None  # modular inverse does not exist 
        else: 
            #get max value for this GF to mod by
            temp=1
            d=self.gf_degree(m.value) -1
            for i in range(d):
                temp*=2
                temp+=1
            if x<0:
                x*=-1#+=temp
            '''
            if y<0:
                y+=temp
            x1=x & temp 
            y1=y & temp 
            if GF2(GF2(self.value) * GF2(x1)) % m == 1:
                return x1
            else:
                return y1
            '''
            #above was because i wanted to check either coefficient for inverse
            #but it should always be x, bc x * a + y * m = 1
            x+=1 #shits and giggles
            return x & temp #restrict to d bits
    
    def __init__(self, value):
        #check if string
        self.valueErrorMsg="must be of class GF2"
        self.value=value
        self.degree=self.gf_degree(value)

    def __and__(self, obj):
        if isinstance(obj, GF2):
            return self.value & obj.value
        elif isinstance(obj, int):
            return self.value & obj
        else:
            raise ValueError(self.valueErrorMsg)

    def __or__(self, obj):
        if isinstance(obj, GF2):
            return self.value | obj.value
        elif isinstance(obj, int):
            return self.value | obj
        else:
            raise ValueError(self.valueErrorMsg)
    
    def __xor__(self, obj):
        if isinstance(obj, GF2):
            return self.value ^ obj.value
        elif isinstance(obj, int):
            return self.value ^ obj
        else:
            raise ValueError(self.valueErrorMsg)
    
    def __lshift__(self, obj):
        if isinstance(obj, GF2):
            return self.value << obj.value
        elif isinstance(obj, int):
            return self.value << obj
        else:
            raise ValueError(self.valueErrorMsg)
    
    def __rshift__(self, obj):
        if isinstance(obj, GF2):
            return self.value >> obj.value
        elif isinstance(obj, int):
            return self.value >> obj
        else:
            raise ValueError(self.valueErrorMsg)
    
    def __invert__(self):
        return ~self.value
    
    def __mul__(self, obj):
        if not isinstance(obj, GF2):
            raise ValueError(self.valueErrorMsg)
        pieces=[]
        y=obj.value
        i=1
        while not y==0:
            temp=self.bitfield(y)
            if temp[-1]==1:
                pieces.append(self.value*i)
            y=y//2
            i*=2
        #now that the pieces are made, XOR all of them
        if len(pieces)==1:
            return pieces[0]
        else:
            temp=0
            for i in range(len(pieces)-1):
                temp=pieces[i] ^ pieces[i+1]
                pieces[i+1]=temp
            return temp

    def __add__(self, obj):
        '''
        if isinstance(obj, GF2):
            return self.value ^ obj.value
        elif isinstance(obj, int):
            return self.value ^ obj 
        else:
            raise ValueError(self.valueErrorMsg)
        '''
        return self.__xor__(obj)

    def __mod__(self, obj):
        if not isinstance(obj, GF2):
            raise ValueError(self.valueErrorMsg)
        goalDegree=self.gf_degree(obj.value) - 1 #(mod will be of 1 degree greater than max)
        curDegree=self.gf_degree(self.value)
        temp=self.value
        while curDegree>goalDegree:
            diff=curDegree-goalDegree - 1
            m=obj.value * (2**diff) #append 0's to modulo value. wont append when same length
            temp=temp ^ m 
            curDegree=self.gf_degree(temp)
        #now that while loop has exited, temp is the result
        return temp