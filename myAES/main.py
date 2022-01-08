"""Main CLI entry point"""
import click
from rich.console import Console  # , ConsoleThreadLocals

from myAES.AES import AES

console = Console()


@click.group()
def cli() -> None:
    """Main entrypoint for CLI"""

    console = Console()
    console.log("Welcome to myAES")


@click.command()
@click.option("-file", type=click.types.STRING, help="Path to file to be encrpyted")
@click.option(
    "--debug",
    type=click.types.BOOL,
    default=False,
    help="Whether or not to run AES and GF2 with debug logs on",
)
def encrypt(file: click.types.STRING, debug: bool) -> None:
    """Will use aes to encrypt file at given path"""
    aes = AES(printStuff=debug)
    console.log(type(aes))


@click.command()
@click.option(
    "--repeat",
    type=click.types.STRING,
    default="no input",
    help="phrase/word to be echo'd",
)
def test_command(repeat: click.types.STRING) -> None:
    console.log(repeat)


if __name__ == "__main__":
    """Run main cli"""
    cli()
