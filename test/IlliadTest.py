import unittest
from mock import Mock
import serviceHandler
from serviceRequests.illiad import Illiad
from hesburgh import hesutil, hestest
import json
import os

hestest.init(__file__, "../testdata")
mockdata = hestest.get("t_heslib01", {}).get("illiad")

class IlliadTestCase(unittest.TestCase):
  def setUp(self):
    os.environ["ILLIAD_KEY"] = "test_key"

    self.netid = "test_netid"
    self.handler = Illiad(self.netid)
    self.handler._makeReq = Mock(return_value=mockdata)


  def bookTest(self, item):
    self.assertIn("title", item)
    self.assertIn("journalTitle", item)
    self.assertIn("journalVolume", item)
    self.assertIn("journalIssue", item)
    self.assertIn("journalMonth", item)
    self.assertIn("journalYear", item)
    self.assertIn("articleAuthor", item)
    self.assertIn("articleTitle", item)
    self.assertIn("author", item)
    self.assertIn("publishedDate", item)
    self.assertIn("requestType", item)
    self.assertIn("dueDate", item)
    self.assertIn("transactionNumber", item)
    self.assertIn("transactionStatus", item)
    self.assertIn("pages", item)


  def test_book_format(self):
    data = self.handler.request("checkedOut")
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("AWESOME BOOK TITLE", item.get("title"))


  def test_web(self):
    data = self.handler.request("web")
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("AWESOME BOOK TITLE", item.get("title"))


  def test_pending(self):
    data = self.handler.request("pending")
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20ne%20%27Request%20Finished%27)%20and%20not%20startswith(TransactionStatus,%20%27Cancel%27)%20and%20not%20(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)%20and%20not%20(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("AWESOME BOOK TITLE", item.get("title"))


def Suite():
  return unittest.TestLoader().loadTestsFromTestCase(IlliadTestCase)

