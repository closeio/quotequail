from setuptools import setup

setup(
    name='quotequail',
    version='0.2.3',
    url='http://github.com/closeio/quotequail',
    license='MIT',
    author='Thomas Steinacher',
    author_email='engineering@close.io',
    maintainer='Thomas Steinacher',
    maintainer_email='engineering@close.io',
    description='A library that identifies quoted text in plain text and HTML email messages.',
    long_description=__doc__,
    packages=[
        'quotequail',
    ],
    test_suite='tests',
    tests_require=['lxml'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
