from distutils.core import setup

setup(
    name='bitmarket24',
    author='pkoszalka',
    author_email='pawel.koszalka@yahoo.pl',
    url='https://github.com/pkoszalka/bitmarket24',
    version='0.8',
    packages=['bitmarket24', ],
    description='API client for Bitmarket24 cryptocurrency trading platform.',
    license='MIT License',
    install_requires=[
        'PyJWT',
        'requests',
    ],
    classifiers=[
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
