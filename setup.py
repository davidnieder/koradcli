from setuptools import setup

setup(
    name='koradcli',
    version='0.1',
    py_modules=['koradcli', 'koradserial'],
    install_requires=[
        'Click', 'pyserial'
    ],
    entry_points='''
        [console_scripts]
        korad=koradcli:korad
    '''
)
