"""Main CLI entry point"""
import sys 

import click 
from rich.console import Console, ConsoleThreadLocals

from .AES.AES import AES 
from .GaloisField.BinaryGaloisFeild import GF2

@click.group()
def cli()->None: 
    """Main entrypoint for CLI"""

    console = Console()
    console.log("Welcome to myAES")

@cli.command()
@click.option(
    "-file",
    type=click.types.Path,
    help="Path to file to be encrpyted"
)
@click.option(
    "--debug",
    type = click.types.BOOL,
    default=False,
    help="Whether or not to run AES and GF2 with debug logs on"
)
def encrypt(file:click.types.Path, debug:bool)->None:
    """Will use aes to encrypt file at given path"""
    pass