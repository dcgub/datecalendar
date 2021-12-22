from glob import glob
from os.path import basename

from setuptools import setup, find_packages
from version import get_version, get_build_number


setup(name='datecalendar',
	  version=get_version() + '-' + get_build_number(),
	  maintainer='dcgub',
	  description='Utility functions for working with Date Calendar.',
	  url='www.datecalendar.io',
	  packages=find_packages('src'),
	  package_dir={'': 'src'},
	  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
	  include_package_data=True,
	  zip_safe=False,
	  install_requires=[])