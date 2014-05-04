'''
Spray
=====

A simple site server with builtin Jade support and caching.

This is not another static site generator, but an actual server aimed at 
providing developers with a way to very quickly write simple websites.
'''

from setuptools import setup

setup(
    name='Spray',
    version='0.1',
    url='http://github.com/glennyonemitsu/Spray/',
    license='MIT',
    author='Glenn Yonemitsu',
    author_email='yonemitsu@gmail.com',
    description='A simple site server with builtin Jade support',
    long_description=__doc__,
    packages=['spray'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flask',
        'gevent',
        'pyjade',
        'pyyaml',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points='''
        [console_scripts]
        spray=spray.spray:main
    ''',
)
