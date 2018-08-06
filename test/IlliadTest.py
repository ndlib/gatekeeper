import unittest
from mock import Mock
import serviceHandler
from serviceRequests.illiad import Illiad
from hesburgh import hesutil, hestest
import json
import os

hestest.init(__file__, "../testdata")

class IlliadTestCase(unittest.TestCase):
  def setUp(self):
    os.environ["ILLIAD_URL"] = "url"
    os.environ["ILLIAD_KEY"] = "test_key"

    self.netid = "test_netid"
    self.handler = Illiad(self.netid)


  def bookTest(self, item):
    self.assertIn("title", item)
    self.assertIn("author", item)
    self.assertIn("published", item)
    self.assertIn("dueDate", item)
    self.assertIn("transactionNumber", item)
    self.assertIn("status", item)


  def test_book_format(self):
    self.handler._makeReq = Mock(return_value=hestest.get("t_heslib01", {}).get("illiad_checkedOut"))

    data = self.handler.checkedOut()
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("AWESOME BOOK TITLE", item.get("title"))


  def test_web(self):
    self.handler._makeReq = Mock(return_value=hestest.get("t_heslib01", {}).get("illiad_web"))

    data = self.handler.web()
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("Web Item Title", item.get("title"))


  def test_pending(self):
    self.handler._makeReq = Mock(return_value=hestest.get("t_heslib01", {}).get("illiad_pending"))

    data = self.handler.pending()
    headers = { 'Content-Type': 'application/json', 'ApiKey': 'test_key' }
    url = self.handler.url

    self.handler._makeReq.assert_called_once_with(url + self.netid + "?$filter=(TransactionStatus%20ne%20%27Request%20Finished%27)%20and%20not%20startswith(TransactionStatus,%20%27Cancel%27)%20and%20not%20(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)%20and%20not%20(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)", headers)

    self.assertIsInstance(data, list)

    item = data[0]
    self.bookTest(item)
    self.assertEqual("Pending Title", item.get("title"))


def Suite():
  return unittest.TestLoader().loadTestsFromTestCase(IlliadTestCase)

