import re
import typer
from pathlib import Path
from typing import Optional
from genomicUtils.utils import version_callback
from genomicUtils import __version__

app = typer.Typer(help="Extracting transcript information from gtf file. Output file follows BED format with additional columns for gene information.")

@app.command(no_args_is_help=True)
def extract(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
    gtf_file: Path = typer.Option(..., "-i", "--input", help="Input GTF file"),
    output_file: Path = typer.Option(..., "-o", "--output", help="Output file for transcript information")
):
    """
    Extract transcript information from a GTF file and write it to an output file.
    The output file will contain the following columns: `chromosome`, `start`, `end`, `strand`, `transcript_id`, `transcript_name`, `transcript_type`, `gene_id`, and `gene_name`.
    """
    with open(gtf_file, 'r') as f, open(output_file, 'r') as o:
        typer.echo(f"Extracted transcript information from {gtf_file} to {output_file}.")

        # Write header
        o.write('chromosome' + '\t' + 'start' + '\t' + 'end' + '\t' + 'strand' + '\t' + 'transcript_id' + '\t' + 'transcript_name' + '\t' + 'transcript_type' + '\t' + 'gene_id' + '\t' + 'gene_name' + '\n')

        for line in f:
            if line.startswith('#'):
                continue
            fields = line.strip().split('\t')
            if fields[2] == 'transcript':
                attr = fields[8]
                transcript_id = re.search(r'transcript_id "([^"]+)"', attr)
                transcript_name = re.search(r'transcript_name "([^"]+)"', attr)
                transcript_type = re.search(r'transcript_biotype "([^"]+)"', attr)
                gene_id = re.search(r'gene_id "([^"]+)"', attr)
                gene_name = re.search(r'gene_name "([^"]+)"', attr)

                if transcript_id and gene_id:
                    o.write(
                        fields[0] + '\t' +
                        fields[3] + '\t' +
                        fields[4] + '\t' +
                        fields[6] + '\t' +
                        transcript_id.group(1) + '\t' +
                        (transcript_name.group(1) if transcript_name else '') + '\t' +
                        (transcript_type.group(1) if transcript_type else '') + '\t' +
                        gene_id.group(1) + '\t' +
                        (gene_name.group(1) if gene_name else '') + '\n'
                    )

if __name__ == '__main__':
    app()