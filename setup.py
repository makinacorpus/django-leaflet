
import os
from setuptools import setup, find_packages
import sys

here = os.path.abspath(os.path.dirname(__file__))
import codecs

requires = ['Django']
if sys.version_info < (2, 7):
    requires += ['ordereddict']

setup(
        name='django-leaflet',
        version='0.23.0',
        author='Mathieu Leplatre',
        author_email='mathieu.leplatre@makina-corpus.com',
        url='https://github.com/makinacorpus/django-leaflet',
        download_url="http://pypi.python.org/pypi/django-leaflet/",
        description="Use Leaflet in your django projects",
        long_description=codecs.open(
            os.path.join(
                here, 'README.rst'), 'r', 'utf-8').read() + '\n\n' +
                         codecs.open(
                             os.path.join(here, 'CHANGES'), 
                             'r', 'utf-8').read(),
        license='LPGL, see LICENSE file.',
        install_requires=requires,
        extras_require={
            'docs': ['sphinx', 'sphinx-autobuild'],
        },
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        classifiers=['Topic :: Utilities',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Intended Audience :: Developers',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Development Status :: 5 - Production/Stable',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'Programming Language :: Python :: 3.5'],
)
