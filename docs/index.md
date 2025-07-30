<img src='asset/logo_title.png' alt='genomicUtils' width='500'/>

`genomicUtils` is a modular command-line toolkit designed to streamline bulk and single-cell genomic data processing.

It provides a curated collection of tools for manipulating genomic annotations, formatting data, extracting features, and preparing input files for downstream analysis.


The toolkit includes utilities for:

- **General-purpose genomic data manipulation** (e.g., GTF parsing, BED/FASTA filtering, contig name conversion),

- **File and sample metadata handling** (e.g., sample matrix generation, filename conversions),

- **Single-cell and multiome data preprocessing** (e.g., read type profiling, fragment conversion, tag extraction from 10X BAM/H5 files).


Each tool is self-contained and scriptable, making `genomicUtils` ideal for high-throughput data processing pipelines and reproducible workflows in computational genomics.

## General Tools

- [bedSelect](general/bedSelect.md): Given an input BED file with multiple sequence coordinates, extract and output a subset of sequences based on regular expression patterns matching a list of sequence identifiers in user-specified columns to the BED file
- [convertContigNames](general/convertContigNames.md): Convert chromosome names in a input file based on a mapping file
- [extractExonFromGTF](general/extractExonFromGTF.md): Extracting exon information from gtf file
- [extractGeneFromGTF](general/extractGeneFromGTF.md): Extracting gene information from gtf file
- [extractTranscriptFromGTF](general/extractTranscriptFromGTF.md): Extracting transcript information from gtf file
- [fileNameConversion](general/fileNameConversion.md): Convert (part) of a file name for files in a directory based on a sample csv file
- [generatePromoterBed](general/generatePromoterBed.md): Generate promoter regions from a transcript annotation file
- [generateSampleMatrix](general/generateSampleMatrix.md): Generate a sample matrix csv file for files in a directory with a specific suffix
- [multiFastaSelect](general/multiFastaSelect.md): Extract sequences from a multi-sequence FASTA file based on regex patterns matching sequence identifiers in the header lines

## Single-Cell Tools

- [calcReadTypeProp](single_cell/calcReadTypeProp.md): Calculate the proportion of reads of each type in each cell barcode
- [extractGEXFromH5](single_cell/extractGEXFromH5.md): Extract gene expression features from a multiome H5 file
- [fragment2Bigwig](single_cell/fragment2Bigwig.md): Convert 10X CellRanger ARC/ATAC fragment file to BigWig format
- [gexBamTagsToCSV](single_cell/gexBamTagsToCSV.md): Parse Cell Ranger BAM tags into a CSV file with deduplication
- [gexBamReadTypeProp](single_cell/gexBamReadTypeProp.md): Combined pipeline that processes Cell Ranger BAM files to calculate read type proportions per cell
