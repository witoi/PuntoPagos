import sys, os
from setuptools import setup, find_packages

from puntopagos import __version__


version = '.'.join(map(str, __version__))


setup(name='PuntoPagos',
      version=version,
      description="Punto Pagos REST API implementation",
      long_description=open('README.md', 'r').read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      ],
      keywords='puntopagos, witoi, e-commerce',
      author=u'Pedro Buron, Alejandro Varas',
      author_email=u'pedro@witoi.com, alejandro@witoi.com',
      url='http://desarrollo.witoi.com',
      license='GPLv3',
      packages=['puntopagos'],
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      tests_require=[
        'mock',
      ],
      test_suite='tests',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
