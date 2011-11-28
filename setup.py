from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='PuntoPagos',
      version=version,
      description="Punto Pagos REST API implementation",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author=u'Pedro Buron, Alejandro Varas',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      test_suite='tests',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
