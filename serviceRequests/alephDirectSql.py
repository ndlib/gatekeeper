import os
import sys
from hesburgh import heslog, hesutil

# make sure the library is in the import path so python can find it
ldPath = os.path.dirname(os.path.realpath(__file__ + "../../")) + '/lib'
sys.path.append(ldPath)

import cx_Oracle


class AlephOracle(object):
  def __init__(self):
    super(AlephOracle, self).__init__()

    user = hesutil.getEnv("ALEPH_ORACLE_USER", throw=True)
    pwd = hesutil.getEnv("ALEPH_ORACLE_PWD", throw=True)
    host = hesutil.getEnv("ALEPH_ORACLE_HOST", throw=True)

    # oracle requires the machine name must be the same as the hosts file entry for 127.0.0.1
    # this is used by the client to create a unique id to connect to the db with
    # taken from https://stackoverflow.com/questions/39201869/aws-python-lambda-with-oracle-oid-generation-failed
    f = open('/tmp/HOSTALIASES','w')
    str_host = os.uname()[1]
    f.write(str_host + ' localhost\n')
    f.close()
    os.environ['HOSTALIASES'] = '/tmp/HOSTALIASES'

    self.connection = cx_Oracle.connect(user, pwd, host + "/ALEPH22")
    self.cursor = self.connection.cursor()


  def userCircHistory(self, alephID):
    self.cursor.execute("""
      SELECT
        z36h_number, z36h_loan_date, z36h_returned_date,
        z13_rec_key, z13_author, z13_title, z13_imprint, z13_year,
        z30_rec_key, z30_barcode, z30_call_no, z30_description
      FROM ndu50.z36h
      LEFT JOIN ndu50.z30 ON z36h_rec_key = z30_rec_key
      LEFT JOIN ndu01.z103 ON SUBSTR(z30_rec_key,1,9) = SUBSTR(z103_rec_key,6,9)
      LEFT JOIN ndu01.z13  ON SUBSTR(z103_rec_key_1,6.9) = z13_rec_key
      WHERE z36h_bor_status != '98'
      AND z36h_id = :alephID
      AND SUBSTR(z103_rec_key,1,5) = 'NDU50'
      UNION
      SELECT
        z36_number, z36_loan_date, z36_returned_date,
        z13_rec_key, z13_author, z13_title, z13_imprint, z13_year,
        z30_rec_key, z30_barcode, z30_call_no, z30_description
      FROM ndu50.z36
      LEFT JOIN ndu50.z30 ON z36_rec_key = z30_rec_key
      LEFT JOIN ndu01.z103 ON SUBSTR(z30_rec_key,1,9) = SUBSTR(z103_rec_key,6,9)
      LEFT JOIN ndu01.z13  ON SUBSTR(z103_rec_key_1,6.9) = z13_rec_key
      WHERE z36_bor_status != '98'
      AND z36_id = :alephID
      AND SUBSTR(z103_rec_key,1,5) = 'NDU50'
      """,
      alephID = alephID)

    columns = [
      "loan_number",
      "loan_date",
      "return_date",
      "bib_number",
      "author",
      "title",
      "publisher",
      "year_published",
      "item_number",
      "barcode",
      "call_number",
      "volume",
    ]
    outData = []
    for values in self.cursor:
      valueData = {}
      for index in xrange(len(columns)):
        valueData[columns[index]] = values[index]
      outData.append(valueData)
    return outData
