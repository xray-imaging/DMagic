from setuptools import setup, Extension, find_packages

setup(
    name = 'dmagic',
    author = 'Francesco De Carlo',
    author_email = 'decarlo@anl.gov',
    description = 'Data Management Magic Tools.',
    packages = find_packages(),
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

