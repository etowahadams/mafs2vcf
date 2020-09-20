from setuptools import setup, find_packages

setup(
    name='mafs2vcf',
    version='0.1',
    packages=['mafs2vcf'],
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mafs2vcf=mafs2vcf.scripts.cli:cli
    ''',
)