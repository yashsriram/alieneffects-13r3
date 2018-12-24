from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='alienware-13r3-alien-effects',
    version='0.2.2',
    scripts=['alieneffects/alieneffects-13r3'],
    packages=['alieneffects'],
    author='Yashasvi Sriram',
    author_email='yash.3997@gmail.com',
    url='https://github.com/Yashasvi-Sriram/alieneffects-13r3',
    description='Backlight LED controller for alienware 13 R3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
