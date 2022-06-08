
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'Django',
]

with open(os.path.join(here, 'README.rst')) as f:
    long_descr = f.read()
with open(os.path.join(here, 'CHANGES')) as f:
    long_descr += '\n\n' + f.read()

setup(
    name='django-leaflet',
    version='0.28.3',
    author='Mathieu Leplatre',
    author_email='mathieu.leplatre@makina-corpus.com',
    url='https://github.com/makinacorpus/django-leaflet',
    download_url="http://pypi.python.org/pypi/django-leaflet/",
    description="Use Leaflet in your django projects",
    long_description=long_descr,
    license='LPGL, see LICENSE file.',
    install_requires=requires,
    extras_require={
        'docs': ['sphinx', 'sphinx-autobuild'],
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Topic :: Utilities',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
