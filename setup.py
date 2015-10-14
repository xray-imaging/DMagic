from setuptools import setup, Extension, find_packages

setup(
    name = 'dmagic',
    author = 'Francesco De Carlo',
    author_email = 'decarlof@aps.anl.gov',
    description = 'Data Management Magic Tools.',
    packages = find_packages(),
    version = open('VERSION').read().strip(),
    zip_safe = False,
    url='http://dmagic.readthedocs.org',
    download_url='http://github.com/decarlof/dmagic.git',
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
        'Programming Language :: Python :: 2.7']
)

