from setuptools import setup

setup(
    name='quotequail',
    version='0.1.1',
    url='http://github.com/elasticsales/quotequail',
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
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
