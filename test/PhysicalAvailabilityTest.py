import unittest
from mock import Mock, patch
from hesburgh import hesutil, hestest
import physicalAvailability
import serviceRequests
import json

issn = "0040-5639"
year = 2000

testEvent = {
  "queryStringParameters": {
    "issn": "%s" % issn,
    "year": "%s" % year,
  }
}

hestest.init(__file__, "../testdata")
mockdata = hestest.get("t_heslib01", {}).get("alephQueryResultSet")

class PhysicalAvailabilityTest(unittest.TestCase):

  def setUp(self):
    self.parsedXml = serviceRequests.untangle.parse(mockdata)


  def test_handler_function_calls(self):
    with patch('physicalAvailability.Primo', autospec=True) as MockedPrimo, \
         patch('physicalAvailability.queryAlephForMatch', autospec=True) as MockedFunc:
      instance = MockedPrimo.return_value
      instance.query.return_value = []

      MockedFunc.return_value = ['item']

      ret = physicalAvailability.handler(testEvent, None)
      self.assertEqual(MockedFunc.call_count, 1)
      self.assertEqual(instance.query.call_count, 1)


  def test_handler_function_calls_no_entries(self):
    with patch('physicalAvailability.Primo', autospec=True) as MockedPrimo, \
         patch('physicalAvailability.queryAlephForMatch', autospec=True) as MockedFunc:
      instance = MockedPrimo.return_value
      instance.query.return_value = []

      MockedFunc.return_value = []

      ret = physicalAvailability.handler(testEvent, None)
      self.assertEqual(MockedFunc.call_count, 1)
      self.assertEqual(instance.query.call_count, 0)


  def test_aleph_query(self):
    with patch('physicalAvailability.Aleph', autospec=True) as MockedAleph, \
         patch('physicalAvailability.startEndYears', autospec=True) as years:
      instance = MockedAleph.return_value
      instance.query.return_value = self.parsedXml

      years.return_value = (0, year)

      ret = physicalAvailability.queryAlephForMatch(None, issn, year)
      self.assertEqual(instance.query.call_count, 1)


  def test_aleph_query(self):
    with patch('physicalAvailability.Aleph', autospec=True) as MockedAleph:
      instance = MockedAleph.return_value
      instance.query.return_value = self.parsedXml

      ret = physicalAvailability.queryAlephForMatch(None, issn, year)
      self.assertEqual(instance.query.call_count, 1)
      # have 2 records in test result set, only second is valid
      self.assertEqual(len(ret), 1)


  def test_aleph_query_years_out_of_range(self):
    with patch('physicalAvailability.Aleph', autospec=True) as MockedAleph, \
         patch('physicalAvailability.startEndYears', autospec=True) as years:
      instance = MockedAleph.return_value
      instance.query.return_value = self.parsedXml

      years.return_value = (0, 0)

      ret = physicalAvailability.queryAlephForMatch(None, issn, year)
      self.assertEqual(instance.query.call_count, 1)
      self.assertEqual(ret, [])


  def test_aleph_query_start_end_years(self):
    # have 2 records in test result set, only second is valid
    recordFields = self.parsedXml.present.record[1].metadata.oai_marc.varfield

    ret = physicalAvailability.startEndYears(recordFields)
    self.assertEqual(ret, (1940, 9999))


def Suite():
  return unittest.TestLoader().loadTestsFromTestCase(PhysicalAvailabilityTest)

