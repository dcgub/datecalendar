import pathlib
from glob import glob
from os.path import basename, splitext

from setuptools import setup, find_packages
from version import get_version, get_build_number

setup_dir = pathlib.Path(__file__).parent
README = (setup_dir / "README.rst").read_text()

setup(name='datecalendar',
	  version=get_version() + '-' + get_build_number(),
	  author='dcgub',
	  description="Replicates the DateCalendar.sol algorithms responsible for storing each date's proof of ownership.",
	  long_description=README,
	  long_description_content_type='text/x-rst',
	  url='https://datecalendar.io',
	  license="MIT",
	  classifiers=[
	      "Intended Audience :: Developers",
	      "License :: OSI Approved :: MIT License",
	      "Development Status :: 4 - Beta",
	      "Operating System :: OS Independent",
	      "Programming Language :: Python :: 3",
	      "Programming Language :: Python :: 3.8",
	      "Programming Language :: Python :: 3.9",
	      "Natural Language :: English"
	  ],
	  packages=find_packages('src'),
	  package_dir={'': 'src'},
	  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
	  include_package_data=True,
	  install_requires=['python-dateutil'],
	  python_requires=">=3.8")