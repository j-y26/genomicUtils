
:::mkdocs-typer2
    :module: genomicUtils.calcReadTypeProp
    :name: calcReadTypeProp

This script is used subsequently to the gex_bam_tags_to_csv.py script by operating on the output csv file.

This script runs on multi-core CPUs to speed up the processing of the data by dividing the data into chunks and processing each chunk in parallel.

Read proportion are calculated as:
    exon_prop = number of confidently mapped exonic reads / number of confidently mapped reads
    intron_prop = number of confidently mapped intronic reads / number of confidently mapped reads
    intergenic_prop = number of confidently mapped intergenic reads / number of confidently mapped reads

Assumptions of the input csv file:
- The input csv file has the following columns:
    - CB_cell_barcode: cell barcode
    - UB_umi_barcode: UMI barcode
    - RE_region_type: region type of the alignment
    - GN_gene_name: gene name(s) for the alignment
- The input csv file only consists of confidently mapped reads (MAPQ >= 255)
- Only reads with valid cell barcodes (CB) and UMI barcodes (UB) are included
- The UMIs are collapsed (i.e., no duplicates)

The output is a csv file such that:
- Each row corresponds to a cell
- Each column corresponds to metadata, with columns
    - CB_cell_barcode: cell barcode
    - total_reads: total number of confidently mapped reads
    - exon_reads: number of confidently mapped exonic reads
    - exon_prop: proportion of confidently mapped exonic reads
    - intron_reads: number of confidently mapped intronic reads
    - intron_prop: proportion of confidently mapped intronic reads
    - intergenic_reads: number of confidently mapped intergenic reads
    - intergenic_prop: proportion of confidently mapped intergenic reads
        - 