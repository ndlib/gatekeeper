from hesburgh import heslog
import unittest
import os
from test import AlephTest, IlliadTest

modules = [AlephTest, IlliadTest]

tests = []
for module in modules:
  tests.append(module.Suite())

alltests = unittest.TestSuite(tests)


if __name__ == '__main__':
  # Set seret for encode/decode to use
  os.environ["JWT_SECRET"] = 'secret'
  # Hide most (if not all) heslogs
  heslog.setLevels(heslog.LEVEL_TEST)

  unittest.TextTestRunner(verbosity=2).run(alltests)
