import pytest 
from myAES import __version__
from myAES.BinaryGaloisFeild import GF2
from myAES.AES import AES

from rich.console import Console 

console = Console() 

def test_version():
    assert __version__ == "0.1.0"

def test_GF2_polynomial():
    """Test if polynomial output matches expected"""
    expectedPolyStr = "x "
    testGF = GF2(2)
    testPolynomialString = testGF.toPolynomial()
    assert testPolynomialString == expectedPolyStr #, f"{expectedPolyStr=}, {testPolynomialString=}"