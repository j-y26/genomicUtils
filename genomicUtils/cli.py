import typer
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import (
    convertContigNames,
    bedSelect,
    calcReadTypeProp,
    extractExonFromGTF,
    extractGEXFromH5,
    extractGeneFromGTF,
    extractTranscriptFromGTF,
    fileNameConversion,
    fragment2Bigwig,
    generatePromoterBed,
    generateSampleMatrix,
    gexBamTagsToCSV,
    multiFastaSelect,
)

app = typer.Typer(
    help="A collection of genomic analysis CLI tools",
    add_completion=False,
    rich_markup_mode="rich"
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True,
        help="Show version and exit"
    )
):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# Register subcommands
app.add_typer(bedSelect.app, name="bedSelect")
app.add_typer(fileNameConversion.app, name="fileNameConversion")
app.add_typer(convertContigNames.app, name="convertContigNames")
app.add_typer(extractGeneFromGTF.app, name="extractGeneFromGTF")
app.add_typer(extractTranscriptFromGTF.app, name="extractTranscriptFromGTF")
app.add_typer(extractExonFromGTF.app, name="extractExonFromGTF")
app.add_typer(generatePromoterBed.app, name="generatePromoterBed")
app.add_typer(generateSampleMatrix.app, name="generateSampleMatrix")
app.add_typer(multiFastaSelect.app, name="multiFastaSelect")
app.add_typer(gexBamTagsToCSV.app, name="gexBamTagsToCSV")
app.add_typer(calcReadTypeProp.app, name="calcReadTypeProp")
app.add_typer(extractGEXFromH5.app, name="extractGEXFromH5")
app.add_typer(fragment2Bigwig.app, name="fragment2Bigwig")


if __name__ == "__main__":
    app()