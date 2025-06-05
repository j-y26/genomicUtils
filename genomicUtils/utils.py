# genomicUtils/utils.py

from genomicUtils import __version__
import typer

def version_callback(value: bool):
    if value:
        typer.echo(f"genomicUtils version {__version__}")
        raise typer.Exit()
