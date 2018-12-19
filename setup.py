from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='alien-effects-13r3',
    version='0.1',
    scripts=['alieneffects/alien-effects-13r3'],
    packages=['alieneffects'],
    author='Yashasvi Sriram',
    author_email='yash.3997@gmail.com',
    url='https://github.com/Yashasvi-Sriram/alien-effects',
    description='Backlight LED controller for alienware devices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
