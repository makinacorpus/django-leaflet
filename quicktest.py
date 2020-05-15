import argparse
import os
import sys

from django.conf import settings
from django.test.runner import DiscoverRunner
import django


class QuickDjangoTest:
    """
    A quick way to run the Django test suite without a fully-configured project.

    Example usage:

        >>> QuickDjangoTest(apps=['app1', 'app2'], db='sqlite')

    Based on a script published by Lukasz Dziedzia at:
    http://stackoverflow.com/questions/3841725/how-to-launch-tests-for-django-reusable-app
    """
    DIRNAME = os.path.dirname(__file__)
    INSTALLED_APPS = [
        'django.contrib.staticfiles',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'django.contrib.messages',
    ]

    def __init__(self, *args, **kwargs):
        self.apps = kwargs.get('apps', [])
        self.database= kwargs.get('db', 'sqlite')
        self.run_tests()

    def run_tests(self):
        """
        Fire up the Django test suite.
        """
        if self.database == 'postgres':
            databases = {
                'default': {
                    'ENGINE': 'django.contrib.gis.db.backends.postgis',
                    'NAME': 'test_db',
                    'HOST': '127.0.0.1',
                    'USER': 'postgres',
                    'PASSWORD': '',
                }
            }

        else:
            databases = {
                'default': {
                    'ENGINE': 'django.contrib.gis.db.backends.spatialite',
                    'NAME': os.path.join(self.DIRNAME, 'database.db'),
                }
            }
        conf = {
            'DATABASES': databases,
            'INSTALLED_APPS': self.INSTALLED_APPS + self.apps,
            'STATIC_URL': '/static/',
            'MIDDLEWARE': [
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
            ],
            'TEMPLATES': [{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ]
                },
                'APP_DIRS': True,
            }],
        }
        if 'SPATIALITE_LIBRARY_PATH' in os.environ:
            # If you get SpatiaLite-related errors, refer to this document
            # to find out the proper SPATIALITE_LIBRARY_PATH value
            # for your platform.
            # https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/spatialite/
            #
            # Example for macOS (with spatialite-tools installed using brew):
            # $ export SPATIALITE_LIBRARY_PATH='/usr/local/lib/mod_spatialite.dylib'
            conf['SPATIALITE_LIBRARY_PATH'] = os.getenv('SPATIALITE_LIBRARY_PATH')
        settings.configure(**conf)
        django.setup()

        failures = DiscoverRunner().run_tests(self.apps, verbosity=1)
        if failures:  # pragma: no cover
            sys.exit(failures)

if __name__ == '__main__':
    """
    What do when the user hits this file from the shell.

    Example usage:

        $ python quicktest.py app1 app2 --db=sqlite

    """
    parser = argparse.ArgumentParser(
        usage="[args] [--db=sqlite]",
        description="Run Django tests on the provided applications."
    )
    parser.add_argument('apps', nargs='+', type=str)
    parser.add_argument('--db', nargs='?', type=str, default='sqlite')
    args = parser.parse_args()
    QuickDjangoTest(apps=args.apps, db=args.db)
