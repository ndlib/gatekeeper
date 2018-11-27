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
          z36_rec_key, z36_number, z36_loan_date, z36_returned_date, z36_due_date, TRIM(z36_material),
          z13_author, z13_title, z13_imprint, z13_year,
          DECODE(SUBSTR(z13_isbn_issn_code, 0, 3), '020', REGEXP_REPLACE(z13_isbn_issn, '[^0-9]+', ''), NULL) ISBN,
          DECODE(SUBSTR(z13_isbn_issn_code, 0, 3), '022', REGEXP_REPLACE(z13_isbn_issn, '[^0-9]+', ''), NULL) ISSN,
          z30_rec_key, TRIM(z30_barcode), TRIM(REGEXP_REPLACE(z30_call_no, '\$\$.', ' ')), z30_description,
          SUBSTR((SELECT z00r_text FROM ndu01.z00r WHERE z00r_doc_number = z13_rec_key AND z00r_field_code = '250'),4) AS edition
        FROM (
          SELECT
            z36_rec_key, z36_number, z36_loan_date, z36_returned_date, z36_due_date, z36_material
          FROM ndu50.z36
          WHERE z36_bor_status != '98'
            AND z36_id = :alephID
          UNION
          SELECT
            z36h_rec_key, z36h_number, z36h_loan_date, z36h_returned_date, z36h_due_date, z36h_material
          FROM ndu50.z36h
          WHERE z36h_bor_status != '98'
            AND z36h_id = :alephID
        ) z36
        LEFT JOIN ndu50.z30 ON z30_rec_key = z36.z36_rec_key
        LEFT JOIN ndu01.z13 ON z13_rec_key = SUBSTR(z30_rec_key,1,9)
        LEFT JOIN ndu01.z103 ON SUBSTR(z103_rec_key,6,9) = SUBSTR(z30_rec_key,1,9)
        WHERE SUBSTR(z103_rec_key,1,5) = 'NDU50'
        """,
      alephID = alephID)

    columns = [
      "bib_number",
      "loan_number",
      "loan_date",
      "return_date",
      "due_date",
      "material",
      "author",
      "title",
      "publisher",
      "year_published",
      "isbn",
      "issn",
      "item_number",
      "barcode",
      "call_number",
      "volume",
      "edition",
    ]
    outData = []
    for values in self.cursor:
      valueData = {}
      for index in xrange(len(columns)):
        valueData[columns[index]] = values[index]
      outData.append(valueData)
    return outData

  def userDetails(self, netID):
    self.cursor.execute("""
          SELECT
            TRIM(z303_rec_key) AS ALEPH_ID,
            TRIM(z303_name) AS NAME,
            TRIM(z303_home_library),
            TRIM(SUBSTR(z304_address, 201, 200)) AS ADDRESS_LINE_1,
            TRIM(SUBSTR(z304_address, 401, 200)) AS ADDRESS_LINE_2,
            TRIM(SUBSTR(z304_address, 601, 200)) AS ADDRESS_LINE_3,
            TRIM(SUBSTR(z304_address, 801, 200)) AS ADDRESS_LINE_4,
            TRIM(z304_zip),
            TRIM(z304_email_address),
            TRIM(z304_telephone),
            TRIM(z304_telephone_2),
            z305_open_date,
            z305_update_date,
            z305_expiry_date,
            z305_bor_status,
            z305_bor_type,
            TRIM(DECODE(a.z308_rec_key, NULL, SUBSTR(b.z308_rec_key, 3), SUBSTR(a.z308_rec_key, 3, 3))) AS CAMPUS,
            TRIM(DECODE(a.z308_rec_key, NULL, SUBSTR(b.z308_rec_key, 3), SUBSTR(a.z308_rec_key, 6))) AS CAMPUS_ID
          FROM pwd50.z308 ids
          LEFT JOIN pwd50.z303 ON TRIM(z303_rec_key) = ids.z308_id
          LEFT JOIN pwd50.z304 ON TRIM(z303_rec_key) = TRIM(SUBSTR(z304_rec_key, 1, 12)) AND z304_address_type = 2
          LEFT JOIN pwd50.z305 ON TRIM(z303_rec_key) = TRIM(SUBSTR(z305_rec_key, 1, 12)) AND SUBSTR(z305_rec_key, 13, 5) = 'ALEPH'
          LEFT JOIN pwd50.z308 a ON TRIM(z303_rec_key) = TRIM(a.z308_id) AND SUBSTR(a.z308_rec_key, 1, 2) = '03'
          LEFT JOIN pwd50.z308 b ON TRIM(z303_rec_key) = TRIM(b.z308_id) AND SUBSTR(b.z308_rec_key, 1, 2) = '01'
          WHERE ids.z308_verification_type = '02'
          AND SUBSTR(ids.z308_rec_key, 1, 2) = '04'
          AND TRIM(SUBSTR(ids.z308_rec_key, 3)) = UPPER(:netID)
        """,
      netID = netID)

    columns = [
      "aleph_id",
      "name",
      "home_library",
      "address_line_1",
      "address_line_2",
      "address_line_3",
      "address_line_4",
      "zip",
      "email_address",
      "telephone",
      "telephone2",
      "open_date",
      "update_date",
      "expiry_date",
      "borrower_status",
      "borrower_type",
      "campus",
      "campus_id",
    ]
    outData = []
    for values in self.cursor:
      valueData = {}
      for index in xrange(len(columns)):
        valueData[columns[index]] = values[index]
      outData.append(valueData)
    return outData
