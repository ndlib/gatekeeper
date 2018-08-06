import unittest
from mock import Mock, patch
import serviceHandler
from serviceRequests import untangle
import alephQuery
from hesburgh import hesutil, hestest
import json
import os

hestest.init(__file__, "../testdata")
mockdata = hestest.get("t_heslib01", {}).get("alephItem")

class AlephQueryTestCase(unittest.TestCase):

  def setUp(self):
    self.parsedXml = untangle.parse(mockdata)


  def test_find_item_calls(self):
    with patch('alephQuery.Aleph', autospec=True) as MockedAleph:
      instance = MockedAleph.return_value
      instance.findItem.return_value = self.parsedXml

      event = {
        "pathParameters": {
          "systemId": "003326992",
        }
      }

      ret = alephQuery.findItem(event, None)
      self.assertEqual(instance.findItem.call_count, 1)


  def test_find_item_title_stripping(self):
    with patch('alephQuery.Aleph', autospec=True) as MockedAleph:
      instance = MockedAleph.return_value
      instance.findItem.return_value = self.parsedXml

      event = {
        "pathParameters": {
          "systemId": "003326992",
        }
      }

      ret = alephQuery.findItem(event, None)
      data = json.loads(ret.get("body"))
      self.assertEqual(data.get("name"), "Nineteenth Century collections online")


def Suite():
  return unittest.TestLoader().loadTestsFromTestCase(AlephQueryTestCase)

