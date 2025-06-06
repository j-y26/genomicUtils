
:::mkdocs-typer2
    :module: genomicUtils.gexBamTagsToCSV
    :name: gexBamTagsToCSV

**Output:**

- Each row corresponds to a read  
- Each column corresponds to a tag  
- The values are the tag values, without the tag name or type  
- UMIs are deduplicated  
- Only confidently mapped reads are included (`MAPQ = 255`)  
- Only valid barcodes are retained (`CB`, `UB`)

**Parsed Tags:**

1. `CB:Z:` Confirmed cell barcode  
2. `UB:Z:` Confirmed UMI  
3. `MAPQ:` Mapping quality  
4. `RE:A:` Region type of alignment (`E`, `N`, `I`)  
5. `GN:Z:` Gene name(s)