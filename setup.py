import setuptools

with open('README.md') as f:
    long_description = f.read()


setuptools.setup(
    name='arinna',
    author='Lukasz Towarek',
    author_email='lukasz.towarek@gmail.com',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ),
    use_scm_version={'write_to': 'src/arinna/version.py'},
    setup_requires=['setuptools_scm'],
    install_requires=[
        'paho-mqtt',
        'influxdb',
        'pyserial',
        'python-crontab',
        'pyyaml'
    ],
    extras_require={
        'dev': [
            'setuptools_scm',
            'tox',
            'pytest'
        ]
    },
    url='https://github.com/ltowarek/arinna',
    project_urls={
        'Bug Reports': 'https://github.com/ltowarek/arinna/issues',
        'Source': 'https://github.com/ltowarek/arinna',
    }
)
