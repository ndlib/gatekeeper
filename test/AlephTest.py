import unittest
from mock import Mock
import serviceHandler
from serviceRequests.aleph import Aleph
from hesburgh import hesutil, hestest
import json
import os

hestest.init(__file__, "../testdata")
mockdata = hestest.get("t_heslib01", {}).get("aleph")

class AlephTestCase(unittest.TestCase):

  def setUp(self):
    os.environ["ALEPH_PATH"] = "/test_path"
    os.environ["ALEPH_URL"] = "url"

    self.netid = "test_netid"
    self.handler = Aleph(self.netid)
    self.handler._makeReq = Mock(return_value=mockdata)


  def test_user_data_format(self):
    data = self.handler.request("user")
    self.handler._makeReq.assert_called_with(self.handler.url + "/test_path", { 'Content-Type': 'xml' })

    self.assertIn("name", data)
    self.assertIn("address1", data)
    self.assertIn("address2", data)
    self.assertIn("telephone", data)
    self.assertIn("telephone2", data)
    self.assertIn("homeLibrary", data)
    self.assertIn("status", data)

    self.assertEqual("User, Test", data.get("name"))
    self.assertEqual("208 Hesburgh Library", data.get("address1"))
    self.assertEqual("Notre Dame, IN 46556", data.get("address2"))


  def test_book_format(self):
    data = self.handler.request("borrowed")
    self.handler._makeReq.assert_called_with(self.handler.url + "/test_path", { 'Content-Type': 'xml' })

    self.assertIsInstance(data, list)
    item = data[0]
    self.assertIn("title", item)
    self.assertIn("author", item)
    self.assertIn("dueDate", item)
    self.assertIn("published", item)
    self.assertIn("status", item)


def Suite():
  return unittest.TestLoader().loadTestsFromTestCase(AlephTestCase)

