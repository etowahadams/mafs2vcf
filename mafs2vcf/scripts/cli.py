import click
from mafs2vcf.main import MafsConverter

@click.command()
@click.option('--target', '--t', required=True, help='Target species mafs file.', type=click.Path())
@click.option('--divergent', '--d', required=True, help='Divergent species mafs file.', type=click.Path())
@click.option('--ancestral', '--a', required=False, default=None, help='Ancestral species mafs file.', type=click.Path())
@click.option('--output', '--o', required=True, default='mafs2vcf_output.vcf', help='Name of output file.')

def cli(target, divergent, ancestral, output):
    """Convert .mafs file outputs from ANGSD to a vcf file."""
    M1 = MafsConverter(target,
                       divergent,
                       ancestral)
    print("Started conversion...")
    M1.convert_to_VCF_anc(output)
    print("Finished. Generated file:", output)

if __name__ == '__main__':
    cli()
