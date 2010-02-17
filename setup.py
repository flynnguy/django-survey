from setuptools import setup, find_packages

setup(
    name='django-survey',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite = 'survey.runtests.runtests',

    author='Christopher Flynn, Yann Malet, Doug Napoleone',
    author_email='chris@flynnguy.com',
    description='A simple extensible survey application for django sites forked from http://code.google.com/p/django-survey/',
    url='http://code.google.com/p/django-survey/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
