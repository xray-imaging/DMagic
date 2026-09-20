from setuptools import setup, Extension, find_packages

setup(
    name = 'dmagic',
    author = 'Francesco De Carlo',
    author_email = 'decarlo@anl.gov',
    description = 'Data Management Magic Tools.',
    packages = find_packages(),
    package_data={'dmagic': ['*.txt']},
    # Only pyyaml was declared here, but the package has never been importable
    # without these, all imported at module level:
    #     pytz, requests  scheduling.py   (requests also in authorize.py)
    #     numpy           config.py
    #     pyepics         __main__.py
    # dmagic/__init__.py does "from dmagic.scheduling import *", so a fresh
    # install failed on the very first import.
    #
    # The APS DM SDK is deliberately NOT listed: it is not on PyPI, so pip
    # cannot resolve it.  It is a conda package -- 2-BM has aps-dm-api 10.1.0
    # from the aps-anl-tag channel, docs/source/install.rst says apsu -- and
    # dmagic degrades gracefully without it: create/delete/email/add-user/
    # remove-user/daq-start/daq-stop announce themselves as unavailable and
    # every other subcommand still works.
    install_requires=[
        'pyyaml',
        'requests',
        'pytz',
        'numpy',
        'pyepics',
    ],
    entry_points={'console_scripts':['dmagic = dmagic.__main__:main'],},
    version = open('VERSION').read().strip(),
    zip_safe = False,
    url='http://dmagic.readthedocs.org',
    download_url='https://github.com/xray-imaging/DMagic.git',
    license='BSD-3',
    platforms='Any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
)

