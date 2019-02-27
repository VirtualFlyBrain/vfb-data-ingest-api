from setuptools import setup, find_packages

setup(
    name='vfb_curation_api',
    version='1.0.0',
    description='An API that encapsulates curation processes of the Virtual Flybrain Project',
    url='https://github.com/VirtualFlyBrain/vfb_curation_api',
    author='Nicolas Matentzoglu',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Virtual Fly Brain',
        'License :: Apache License Version 2.0',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='rest flask swagger flask-restplus virtual-fly-brain',

    packages=find_packages(),

    install_requires=['flask-restplus==0.9.2', 'Flask-SQLAlchemy==2.1'],
)
