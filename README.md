# mafs2vcf

mafs2vcf is a Python command line interface for converting
[ANGSD generated .mafs files](http://www.popgen.dk/angsd/index.php/Allele_Frequencies) to a
[variant call format](https://en.wikipedia.org/wiki/Variant_Call_Format) file (.vcf).

## Installation
```
$ git clone https://github.com/etowahs/mafs2vcf.git
$ cd mafs2vcf
$ pip install .
$ mafs2vcf --help
```

## Usage
To convert mafs file to vcf, mafs2vcf requires the mafs file for the target species and divergent species. If you
also have a mafs file for an ancestral species, it can be included as an option argument with the flag `-a`.
```
$ mafs2vcf --t data/target.mafs --d data/divergent.mafs --a data/ancestral.mafs
```
The resulting vcf file will have four different individuals, two for the target (SAMP1, SAMP2), one for the divergent (DIV1),
and one for the ancestral (ANC1). The target mafs is divided up into two individuals because it is useful for downstream processing
in the [massprf-pipeline](https://github.com/sjgaughran/massprf-pipeline).
If the knownEM of a site is under 0.99, then we assume that the site is polymorphic and the sample gets a 0/1 in the vcf file.
If the knownEM is >= 0.99, then we assume that the site is fixed and the sample gets a 1/1/ in the vcf file.