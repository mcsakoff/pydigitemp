from setuptools import setup, find_packages
import digitemp

setup(
    name='pydigitemp',
    version=digitemp.__version__,
    description='Python implementation of 1-Wire protocol',
    author='Alexey McSakoff',
    author_email='mcsakoff@gmail.com',
    url='https://github.com/mcsakoff/pydigitemp',
    install_requires=[
        'pyserial>=3.0,<4.0',
    ],
    packages=find_packages(),
    license='Python',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
    keywords=['1-wire', 'UART', 'RS232', 'DS1820', 'DS18B20', 'DS18S20'],
)
