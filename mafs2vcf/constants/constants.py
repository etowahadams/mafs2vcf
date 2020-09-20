VCF_HEADER_DIV = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMP1\tSAMP2\tDIV1\n'
VCF_HEADER_ANC = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMP1\tSAMP2\tDIV1\tANC1\n'
VCF_INFO = '##fileformat=VCFv4.3\n' \
           '##INFO=<ID=KEM,Number=1,Type=Float,Description="knownEM frequency using -doMaf 1">\n' \
           '##INFO=<ID=PKEM,Number=1,Type=Float,Description="pK-EM">\n' \
           '##INFO=<ID=NI,Number=1,Type=Integer,Description="nInd">\n'
VAR_ID = '.'
VAR_FILTER = 'PASS'
VAR_QUAL = '.'