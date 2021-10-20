from setuptools import setup


setup(
    name='adapter_tools',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=['Programming Language :: Python :: 3'],
    description='Command-line utilities for Human Cell Atlas adapter pipelines',
    url='http://github.com/broadinstitute/hca-adapter_tools',
    author='Human Cell Atlas Data Coordination Platform - Lantern Team',
    author_email='Broad Institute DSDE <dsde-engineering@broadinstitute.org>',
    license='BSD 3-clause "New" or "Revised" License',
    packages=['adapter_tools'],
    install_requires=[
        'arrow>=0.12.1',
        'google-auth==2.0.0',
        'google-cloud-storage==1.42.0',
        'mock>=2.0.0,<3',
        'requests>=2.20.0,<3',
        'requests-mock>=1.5.2,<2',
        'setuptools_scm>=2.0.0,<3',
        'tenacity>=5.0.2,<5.1',
        'PyJWT==1.6.4',
    ],
    entry_points={
        'console_scripts': [
            'copy-adapter-outputs=adapter_tools.commands.copy_adapter_outputs:main',
            'create-analysis-file=adapter_tools.commands.create_analysis_file:main',
            'create-analysis-process=adapter_tools.commands.create_analysis_process:main',
            'create-analysis-protocol=adapter_tools.commands.create_analysis_protocol:main',
            'create-file-descriptor=adapter_tools.commands.create_file_descriptor:main',
            'create-links=adapter_tools.commands.create_links:main',
            'create-reference-file=adapter_tools.commands.create_reference_file:main',
            'get-analysis-workflow-metadata=adapter_tools.commands.get_analysis_workflow_metadata:main',
            'get-bucket-date=adapter_tools.commands.get_bucket_date:main',
            'get-process-input-ids=adapter_tools.commands.get_process_input_ids:main',
            'get-reference-file-details=adapter_tools.commands.get_reference_details:main',
            'merge-looms=adapter_tools.commands.merge_looms:main',
            'parse-metadata=adapter_tools.commands.parse_cromwell_metadata:main',
        ]
    },
    include_package_data=True,
)
