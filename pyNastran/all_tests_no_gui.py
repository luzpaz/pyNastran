#import warnings
#warnings.filterwarnings('ignore', 'missing __init__.py*')

import sys
import os
import pyNastran
pkg_path = pyNastran.__path__[0]

# , 'py_to_rst.py'
manual_path = os.path.abspath(os.path.join(pkg_path, '..', 'docs', 'html_docs', 'manual'))
sys.path.append(manual_path)

#print(sys.path)
from notebook_to_markdown import create_rst_from_ipython_notebooks
#create_rst_from_ipython_notebooks()

#bdf
from pyNastran.bdf.test.all_tests import *
from pyNastran.dev.bdf_vectorized2.bdfv_unit_tests import *
try:
    import h5py
    IS_H5PY = True
except ModuleNotFoundError:
    IS_H5PY = False

if IS_H5PY:
    from pyNastran.dev.h5.test.test_h5 import *

#op2
from pyNastran.op2.test.all_tests import *

#f06
from pyNastran.f06.test.all_tests import *

#op4
from pyNastran.op4.test.op4_unit_tests import TestOP4

#utils
from pyNastran.utils.test.all_tests import *
from pyNastran.femutils.test.all_tests import *

# converters
from pyNastran.converters.test_formats import *

#gui - just tests the imports
from pyNastran.gui.test.all_tests_no_gui import *
#on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
#if not on_rtd:
    #import pyNastran.gui.gui
#import pyNastran.gui.gui

try:
    from pyNastran.dev.solver.test_springs import *
except ImportError:  # pragma: no cover
    pass


if __name__ == "__main__":  # pragma: no cover
    import unittest
    unittest.main()
