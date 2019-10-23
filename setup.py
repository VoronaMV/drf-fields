import os
from setuptools import find_packages, setup
import drf_fields


setup(
    name='drf_fields',
    url='https://github.com/VoronaMV/drf-fields',
    version=drf_fields.__version__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    license='MIT',
    description='Django REST Framework extra fields.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    zip_safe=False,
    author='mvorona',
    author_email='mvl.vorona@gmail.com',
    keywords=['drf fields', 'fields', 'serializer fields'],
    install_requires=[],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django REST Framework',
        'License ::  Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
