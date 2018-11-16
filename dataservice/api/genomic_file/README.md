prefix: `GF`

Genomic Files track files related to the bioinformatics process such as `bam`
`cram`, `gvcf`, and other files. Files may be related to a `Biospecimen`
(eg: an aligned `cram`), others may not be directly related to `Biospecimen`,
having been derived from some other file(s) (eg: a cohort `vcf`).
Most all `Genomic Files` should be able to resolve to one or more `Biospecimens`
by tracing their lineage back through related `Tasks`
