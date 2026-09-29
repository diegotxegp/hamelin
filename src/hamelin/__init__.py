"""
HAMELIN - Clinical Research AutoML Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A clinical research tool for data analysis and machine learning.
"""

__version__ = "0.1.0"
__author__ = "Diego García-Prieto, Camilo Palazuelos, Rafael Duque, Mano Domingo"


def main() -> None:
    import sys

    from hamelin.main import main as _main
    sys.exit(_main())
