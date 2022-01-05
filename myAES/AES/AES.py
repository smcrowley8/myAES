#made by Sean Crowley
from GaloisField.BinaryGaloisFeild import GF2
#from AES_PREP import AES_PREP 
import codecs
#in future, replace all comments with assume with some sort of error checking

'''************************ ISSUE ***************
the _setString methods needto handle ascii values that are no good somehow
'''

class AES:
    #**************** end of cipher stuff ************
    def _setCtString(self, ctList:list):
        s=""
        self.ctString=""
        for e in ctList:
            if e<32 or e==127:
                #get rid of bad chars
                e+=127
            temp=chr(e)
            s+=temp
        self.ctString=s
        self.ctStrings.append(s)
    def getCtString(self)->str:
        l=len(self.ctStrings)
        if l==0:
            raise ValueError("no ct string was made, please try again")
        elif l==1:
            return self.ctString
        else:
            s=""
            for e in self.ctStrings:
                s+=e
            return s   
    
    def _setPtString(self, ptList:list):
        s=""
        self.ptString=""
        for e in ptList:
            if e<32 or e==127:
                #get rid of bad chars
                e+=128
            temp=chr(e)
            s+=temp
        self.ptString=s
        self.ptStrings.append(s)
    def getPtString(self)->str:
        l=len(self.ptStrings)
        if l==0:
            raise ValueError("no pt string was made, please try again")
        elif l==1:
            return self.ptString
        else:
            s=""
            for e in self.ptStrings:
                s+=e
            return s 
        
    #**************** setup stuff ***************
    def makeMat(self, pt:list)->list:
        #assume pt is a list of bytes
        ptMat=[]
        for i in range(4):
            temp=[]
            for j in range(4):
                temp.append(pt[i+(4*j)])
            ptMat.append(temp)
        return ptMat
    #************ decrypt stuff ***************

    def byteSubInv(self, m:list)->list:
        for i in range(len(m)):
            for j in range(len(m[i])):
                x,y=self.byteToNibbles(m[i][j])
                m[i][j]=self.sboxINV[x][y]
        return m
    
    def shiftRowInv(self, m:list)->list:
        #first row not effected
        temp=self.transposeMat(m)
        for i in range(1,4):#skip first row
            temp[i]=self.shiftRight(temp[i],i)
        #re transpose for future matrix stuff
        ans=self.transposeMat(temp)
        return ans

    
    def mixColInv(self, m:list)->list:
        '''
        coefficient = [
            [GF2(0x0e), GF2(0x0b), GF2(0x0d), GF2(0x09)],
            [GF2(0x09), GF2(0x0e), GF2(0x0b), GF2(0x0d)],
            [GF2(0x0d), GF2(0x09), GF2(0x0e), GF2(0x0b)],
            [GF2(0x0b), GF2(0x0d), GF2(0x09), GF2(0x0e)]
        ]
        '''
        coefficient=[
            [14,11,13,9],
            [9, 14, 11, 13],
            [13, 9, 14, 11],
            [11, 13, 9, 14]
        ]
        ans=self.GFmatMul(coefficient, m) 
        return ans

    #****************** key stuff ****************
    def keyTransform(self, k:list, n:int)->list:
        #will take a 1d list, left shift it, apply sbox to it
            #and then the first element is XOR'd with 2^((n-4)/4) 
                #n = the row being made
        #only called if n%4=0 so no check needed
        t=[]
        for ele in k: #needed for dereferencing
            t.append(ele)
        t=self.shiftLeft(t, 1)
        for i in range(len(t)):
            a,b=self.byteToNibbles(t[i])
            t[i]=self.sbox[a][b]
        temp=t[0] ^ (2** int(((n-4)/4)))
        #check if out of bounds of a single byte
            # if it is out of bounds do i multiply mod by 0b100000000 or do i mod by GF2(8) reduction polynomial?
        t[0]=temp
        return t


    # note 
    #the keymat return here is created by rows, so key0=row 0, key1=row 1
    #creating the 40 extra keys will be done by added rows instead of columns
    def generateKeyMat(self, key)->list:
        if isinstance(key, list):
            keyMat=[]
            for i in range(4):
                row=[key[i] for i in range(i*4, (i*4)+4)]
                keyMat.append(row)
            return keyMat
        else:
            raise TypeError("key must be a list of ints")
        

    def listXOR(self, a:list, b:list)->list:
        #assume of same length
        return [a[i] ^ b[i] for i in range(len(a))]
    
    #will add 40 rows to keymat and then  transpose it so it's ready for encrypt/decrypt
    def generateKeys(self, key:list)->list:
        keyMat=self.generateKeyMat(key) 
        for n in range(4,44):#add 40 rows (should be 4,44)
            a=keyMat[n-4]
            temp=keyMat
            if n%4==0:
                temp2=temp[n-1]
                b=self.keyTransform(temp2,n)
            else:
                b=keyMat[n-1]
            newRow=self.listXOR(a,b)
            keyMat.append(newRow)   
        return keyMat  

    def generateRoundKey(self, key:list, round:int):
        ans=key[4*round:(4*round)+4]
        #transpose?
        return ans
    
    #************* encryption stuff ****************
    def addRoundKey(self, m:list, key:list)->list:
        ans=[]
        for i in range(4):#always 4?
            temp=[]
            for j in range(4):
                temp.append(m[i][j] ^ key[i][j])
            ans.append(temp)
        return ans

    def mixCol(self, m:list)->list:
        '''
        one=GF2(1)
        two=GF2(2)
        three=GF2(3)
        coefficient=[
            [two, one,one,three],
            [three, two, one, one],
            [one, three, two, one],
            [one, one, three, two]
        ] #this is transposed because i do things with rows instead of columns
        '''
        coefficient=[
            [2,3,1,1],
            [1,2,3,1],
            [1,1,2,3],
            [3,1,1,2]] #not transposed bc matmul will transpose state
        #m=self.toGF(m) 
        #time to multiply
        ans=self.GFmatMul(coefficient, m) 
        return ans

    def shiftRow(self, m:list)->list:
        #this object internally refers to the matrices as the transpose of what they are conceptually
        #to shit a row one must shift that column instead
        temp=self.transposeMat(m)
        for i in range(1,4):#skip first row
            temp[i]=self.shiftLeft(temp[i],i)
        #re transpose for future matrix stuff
        ans=self.transposeMat(temp)
        return ans

    def byteSub(self, m:list)->list:
        for i in range(len(m)):
            for j in range(len(m[i])):
                x,y=self.byteToNibbles(m[i][j])
                m[i][j]=self.sbox[x][y]
        return m

    def encrypt(self, pt, key:list, numrounds:int):
        '''
        #if a string is passed preperation is needed
        if isinstance(pt, str):
            temp_prep = AES_PREP(PT=pt)
            ptList=temp_prep.getPtList()
            if isinstance(ptList[0], list): 
                #this means we ahve a list of lists and must encrypt for each list
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
        '''

        #generate pt matrix for computations
        ptMat=self.transposeMat(self.makeMat(pt)) #makeMat is formatted conceptually
        
        #the key matrix is made in generate keys
        extendedKeyMat=self.generateKeys(key)
        #ARK on original key
        k0=self.generateRoundKey(extendedKeyMat, 0)
        workingMat=self.addRoundKey(m=ptMat, key=k0)
        if(self.print):
            print('pt mat')
            self.printHexMatrix(ptMat)
            print('key 0 ')
            self.printHexMatrix(k0)
            print('result from initial ARK')
            self.printHexMatrix(workingMat)
        #n-1 rounds for 4 layers (BS, SR, MC, ARK) using round 1 to n-1 key
        #round N: BS, SR, ARK using round N key
        #128 pt -> 4X4 matrix, each element is a byte
        for i in range(1, numrounds+1):
            byteSubResult=self.byteSub(workingMat)

            shiftRowResult = self.shiftRow(byteSubResult)

            mixColResult = self.mixCol(shiftRowResult) 

            roundKey=self.generateRoundKey(extendedKeyMat, i)
            nextRoundMat=self.addRoundKey(mixColResult, key=roundKey)
            if(self.print):
                print('round ', i, ' key')
                self.printHexMatrix(roundKey)
                print('result from byteSub round ', i)
                self.printHexMatrix(byteSubResult)
                print('result from shiftRow round ', i)
                self.printHexMatrix(shiftRowResult)
                print('result from mixCol round ', i)
                self.printHexMatrix(mixColResult)
                print('result from ARK round ', i)
                self.printHexMatrix(nextRoundMat)

            workingMat=nextRoundMat
        #this is for setting the ct string
        temp=[]
        for row in workingMat:
            temp+=row 
        #make 2d into 1d
        self._setCtString(temp) #set ctString
        return workingMat #should first turn workingMat into a string?
    
    def decrypt(self, ct, key:list, numrounds:int):
        '''
        if isinstance(ct, str):
            temp_prep = AES_PREP(CT=ct)
            ctList=temp_prep.getCtList()
            if isinstance(ctList[0], list): 
                #this means we ahve a list of lists and must encrypt for each list
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
        '''
        #each layer is invertible
        ctMat=self.transposeMat(self.makeMat(ct)) #makeMat is formatted conceptually
        #we want the transpose of the conceptual ptMat

        extendedKeyMat=self.generateKeys(key)

        #ARK on original key
        k0=self.generateRoundKey(extendedKeyMat, numrounds)
        #if 10 rounds we want the key from k40:k43

        workingMat=self.addRoundKey(m=ctMat, key=k0) #initial ARK
        #add print check and statements here
        if(self.print):
            print('ct mat')
            self.printHexMatrix(ctMat)
            print('key 0 ')
            self.printHexMatrix(k0)
            print('result from initial ARK')
            self.printHexMatrix(workingMat)
        #first round will use key9 (k36:39)
        for i in reversed(range(numrounds)): 
            if i>0 or numrounds==1:
                IMixColResult=self.mixColInv(workingMat)
                workingMat=IMixColResult

            IShiftRowResult = self.shiftRowInv(workingMat)

            #then inverse bytesub
            IByteSubResult = self.byteSubInv(IShiftRowResult)
            
            #then add round key
            roundKey=self.generateRoundKey(extendedKeyMat, i)
            IARKresult = self.addRoundKey(IByteSubResult, roundKey)

            workingMat=IARKresult

            #add prints here
            if(self.print):
                print('round ', i, ' key')
                self.printHexMatrix(roundKey)
                if i>0 or numrounds==1:
                    print('result from mixCol round ', i)
                    self.printHexMatrix(IMixColResult)
                print('result from inverse shiftRow round ', i)
                self.printHexMatrix(IShiftRowResult)
                print('result from inverse byteSub round ', i)
                self.printHexMatrix(IByteSubResult)
                print('result from ARK round ', i)
                self.printHexMatrix(IARKresult)

        temp=[]
        for row in workingMat:
            temp+=row 
        #make 2d into 1d
        self._setPtString(temp) #set ctString
        return workingMat

    def __init__(self, printStuff=False):
        #do something
        self.print=printStuff
        self.mod=0b100011011

        self.sbox=[
            [0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76],
            [0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0],
            [0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15],
            [0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75],
            [0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84],
            [0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf],
            [0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8],
            [0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2],
            [0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73],
            [0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb],
            [0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79],
            [0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08],
            [0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a],
            [0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e],
            [0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf],
            [0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16]
        ]
        self.sboxINV=[
            [0x52,0x09,0x6a,0xd5,0x30,0x36,0xa5,0x38,0xbf,0x40,0xa3,0x9e,0x81,0xf3,0xd7,0xfb],
            [0x7c,0xe3,0x39,0x82,0x9b,0x2f,0xff,0x87,0x34,0x8e,0x43,0x44,0xc4,0xde,0xe9,0xcb],
 	        [0x54,0x7b,0x94,0x32,0xa6,0xc2,0x23,0x3d,0xee,0x4c,0x95,0x0b,0x42,0xfa,0xc3,0x4e],
 	        [0x08,0x2e,0xa1,0x66,0x28,0xd9,0x24,0xb2,0x76,0x5b,0xa2,0x49,0x6d,0x8b,0xd1,0x25],
 	        [0x72,0xf8,0xf6,0x64,0x86,0x68,0x98,0x16,0xd4,0xa4,0x5c,0xcc,0x5d,0x65,0xb6,0x92],
 	        [0x6c,0x70,0x48,0x50,0xfd,0xed,0xb9,0xda,0x5e,0x15,0x46,0x57,0xa7,0x8d,0x9d,0x84],
 	        [0x90,0xd8,0xab,0x00,0x8c,0xbc,0xd3,0x0a,0xf7,0xe4,0x58,0x05,0xb8,0xb3,0x45,0x06],
 	        [0xd0,0x2c,0x1e,0x8f,0xca,0x3f,0x0f,0x02,0xc1,0xaf,0xbd,0x03,0x01,0x13,0x8a,0x6b],
 	        [0x3a,0x91,0x11,0x41,0x4f,0x67,0xdc,0xea,0x97,0xf2,0xcf,0xce,0xf0,0xb4,0xe6,0x73],
 	        [0x96,0xac,0x74,0x22,0xe7,0xad,0x35,0x85,0xe2,0xf9,0x37,0xe8,0x1c,0x75,0xdf,0x6e],
 	        [0x47,0xf1,0x1a,0x71,0x1d,0x29,0xc5,0x89,0x6f,0xb7,0x62,0x0e,0xaa,0x18,0xbe,0x1b],
 	        [0xfc,0x56,0x3e,0x4b,0xc6,0xd2,0x79,0x20,0x9a,0xdb,0xc0,0xfe,0x78,0xcd,0x5a,0xf4],
 	        [0x1f,0xdd,0xa8,0x33,0x88,0x07,0xc7,0x31,0xb1,0x12,0x10,0x59,0x27,0x80,0xec,0x5f],
 	        [0x60,0x51,0x7f,0xa9,0x19,0xb5,0x4a,0x0d,0x2d,0xe5,0x7a,0x9f,0x93,0xc9,0x9c,0xef],
 	        [0xa0,0xe0,0x3b,0x4d,0xae,0x2a,0xf5,0xb0,0xc8,0xeb,0xbb,0x3c,0x83,0x53,0x99,0x61],
         	[0x17,0x2b,0x04,0x7e,0xba,0x77,0xd6,0x26,0xe1,0x69,0x14,0x63,0x55,0x21,0x0c,0x7d]
        ]

        #for end of program to make sure if methods are called early theres no issue
        self.ctString=""
        self.ctStrings=[]
        self.ptString=""
        self.ptStrings=[] 
        temp=[]
        temp.append("AES(): initializes AES object for encryption and decryption\n")
        temp.append("AES(printStuff=True): initailze AES for encrypt/decrypt, will print steps and results frome each step along the way\n\n")
        temp.append("AES.encrypt(pt=, key=, numrounds=): will encrypt pt(either a list of ints or a string) using key(must be a list of ints) over numrounds(int). Returns the final matrix\n")
        temp.append("AES.decrypt(ct=, key=, numrounds=): will decrypt ct(either a string or a list of ints) using key(a list of ints) over numrounds(int). Returns the final matrix\n")
        temp.append("AES.get(C/P)tString(): will return a string made from the encrypt/decrypt")
        temp.append("encoding used when strings are passed is UTF-8\n")
        temp.append("TypeError and ValueErrors are possible and will be returned with custom output string\n")
        s=""
        for t in temp:
            s+=t
        self.__doc__=s

    #*****************  data manip stuff ******************
    
    def GFdot(self, a,b):
        '''
        #assume same length
        temp=[]
        #list of products
        for i in range(len(a)):
            temp.append( GF2(a[i] * b[i]) % GF2(self.mod))
        #now sum
        ans=0
        for i in temp:#ignore first element
            ans=ans ^ i
        return ans
        '''
        #something wrong with logic above
        m=GF2(self.mod)
        first=GF2(GF2(a[0])*GF2(b[0])) % m
        sec=GF2(GF2(a[1])*GF2(b[1])) % m
        third=GF2(GF2(a[2])*GF2(b[2])) % m
        fourth=GF2(GF2(a[3])*GF2(b[3])) % m 
        temp=[first, sec, third, fourth]
        ans=0
        for i in temp:
            ans=ans^i 
        return ans

    def getCol(self, m, c):
        #return column c of matrix m (list)
        return [r[c] for r in m]

    def GFmatMul(self, a,b):
        ans=[] #ans(i,j)=a[i] dot b[][j]
        b=self.transposeMat(b)
        for i in range(len(a)): #for each row in a
            temp=[]
            for j in range(len(b[0])):# for each col in b
                #append to temp the product of a[i] and col j in b
                temp.append(self.GFdot(a[i],self.getCol(b,j)))
            ans.append(temp)
        ans=self.transposeMat(ans)
        return ans

    def byteToNibbles(self, byte:int)->tuple:
        s=hex(byte)[2:] #get rid of 0x
        while len(s)<2:
            s='0'+s
        return int(s[0], 16),int(s[1], 16)

    def shiftLeft(self, r:list, n:int)->list:
        #shifts row r left n bits
        for i in range(n):
            temp=r.pop(0)
            r.append(temp)
        return r
    
    def shiftRight(self, r:list, n:int)->list:
        #shifts row r right n bits
        for i in range(n):
            temp=r.pop(-1)
            r.insert(0,temp)
        return r
    
    def transposeMat(self, m:list):
        '''ans=[]
        for i in range(len(m[0])): #for each colum
            temp=[]
            for j in range(4): #for each new col
                temp.append(m[j][i])#add Jth element from row i to new list
            ans.append(temp)
        return ans'''
        ans=m.copy()
        ans=list(zip(*ans)) #this is now a list of tuples
        for i in range(len(ans)):
            ans[i]=list(ans[i])#turn tuples to list so its a proper matrix
        return ans

    def printHexMatrix(self, t):
        m=self.transposeMat(t)
        s=""
        for r in m:
            for e in r:
                temp=hex(e)[2:]+" "
                if(len(temp)==2):
                    temp='0'+temp
                s+=temp
            s+='\n'
        print(s)