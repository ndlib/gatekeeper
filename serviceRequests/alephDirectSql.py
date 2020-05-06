import os
import sys
import ConfigParser
from hesburgh import heslog, hesutil

# make sure the library is in the import path so python can find it
ldPath = os.path.dirname(os.path.realpath(__file__ + "../../")) + '/lib'
sys.path.append(ldPath)

cfgPath = os.path.dirname(os.path.realpath(__file__ + "../../")) + '/config'

import cx_Oracle


class AlephOracle(object):
  def __init__(self):
    super(AlephOracle, self).__init__()

    user = hesutil.getEnv("ALEPH_ORACLE_USER", throw=True)
    pwd = hesutil.getEnv("ALEPH_ORACLE_PWD", throw=True)
    host = hesutil.getEnv("ALEPH_ORACLE_HOST", throw=True)
    sid = hesutil.getEnv("ALEPH_ORACLE_SID", throw=True)

    # oracle requires the machine name must be the same as the hosts file entry for 127.0.0.1
    # this is used by the client to create a unique id to connect to the db with
    # taken from https://stackoverflow.com/questions/39201869/aws-python-lambda-with-oracle-oid-generation-failed
    f = open('/tmp/HOSTALIASES','w')
    str_host = os.uname()[1]
    f.write(str_host + ' localhost\n')
    f.close()
    os.environ['HOSTALIASES'] = '/tmp/HOSTALIASES'

    self.connection = cx_Oracle.connect(user, pwd, host + "/" + sid)
    self.cursor = self.connection.cursor()


  def userCircHistory(self, netID):
    # First get their aleph id. It's quicker and easier to do this in its own query
    alephID = None
    query = """
      SELECT TRIM(z308_id) alephId
      FROM pwd50.z308
      WHERE z308_verification_type = '02'
        AND SUBSTR(z308_rec_key, 1, 2) = '04'
        AND TRIM(SUBSTR(z308_rec_key, 3)) = UPPER(:netID)
    """
    self.cursor.execute(query, netID = netID)
    for values in self.cursor:
      alephID = values[0]

    # if we didn't find an aleph account for the netid, don't bother continuing.
    if alephID is None:
      return None

    sql = """
      SELECT
        z36.*,
        z13_rec_key, z13_author, z13_title, z13_imprint, z13_year,
        DECODE(SUBSTR(z13_isbn_issn_code, 0, 3), '020', REGEXP_REPLACE(z13_isbn_issn, '[^0-9]+', ''), NULL) ISBN,
        DECODE(SUBSTR(z13_isbn_issn_code, 0, 3), '022', REGEXP_REPLACE(z13_isbn_issn, '[^0-9]+', ''), NULL) ISSN,
        TRIM(z30_barcode), TRIM(REGEXP_REPLACE(z30_call_no, '\$\$.', ' ')), TRIM(z30_description),
        SUBSTR((SELECT z00r_text FROM ndu01.z00r WHERE z00r_doc_number = z13_rec_key AND z00r_field_code = '250'),4) AS edition,
        SUBSTR(z103_rec_key,1,3) AS institution
      FROM (
        SELECT
          z36_rec_key, z36_number, z36_loan_date, z36_returned_date, z36_due_date, TRIM(z36_material)
        FROM <inst>50.z36
        WHERE z36_bor_status != '98'
          AND TRIM(z36_id) = :alephID
        UNION
        SELECT
          z36h_rec_key, z36h_number, z36h_loan_date, z36h_returned_date, z36h_due_date, TRIM(z36h_material)
        FROM <inst>50.z36h
        WHERE z36h_bor_status != '98'
          AND TRIM(z36h_id) = :alephID
      ) z36
      LEFT JOIN <inst>50.z30 ON z30_rec_key = z36.z36_rec_key
      LEFT JOIN <inst>01.z103 ON z103_lkr_doc_number = SUBSTR(z30_rec_key,1,9)
      LEFT JOIN <inst>01.z13 ON z13_rec_key = SUBSTR(z103_rec_key_1,6,9)
      WHERE SUBSTR(z103_rec_key,1,5) = '<inst>50' AND SUBSTR(z103_rec_key_1,1,5) = '<inst>01' AND z103_lkr_library = '<inst>50'
    """
    query = sql.replace('<inst>', 'NDU')
    query += ' UNION ALL ' + sql.replace('<inst>', 'HCC')
    self.cursor.execute(query, alephID = alephID)

    columns = [
      "adm_number",
      "loan_number",
      "loan_date",
      "return_date",
      "due_date",
      "material",
      "bib_number",
      "author",
      "title",
      "publisher",
      "year_published",
      "isbn",
      "issn",
      "barcode",
      "call_number",
      "volume",
      "edition",
      "institution",
    ]
    outData = []
    for values in self.cursor:
      valueData = {}
      for index in xrange(len(columns)):
        valueData[columns[index]] = values[index]
      outData.append(valueData)
    return outData

  def userInfo(self, netID, library):
    # NOTE: This query requires library param because it gets a user's balance within a specific library.
    # It could be adapted to bring back amounts from all libraries, but that would break backwards-compatibility.
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
            UPPER(z305_bor_type),
            z305_loan_permission,
            z305_hold_permission,
            z305_renew_permission,
            NVL(bal.amount, 0) AS BALANCE,
            TRIM(DECODE(a.z308_rec_key, NULL, SUBSTR(b.z308_rec_key, 3), SUBSTR(a.z308_rec_key, 3, 3))) AS CAMPUS,
            TRIM(DECODE(a.z308_rec_key, NULL, SUBSTR(b.z308_rec_key, 3), SUBSTR(a.z308_rec_key, 6))) AS CAMPUS_ID
          FROM pwd50.z308 ids
            JOIN pwd50.z303 ON TRIM(z303_rec_key) = TRIM(ids.z308_id)
            LEFT JOIN pwd50.z308 a ON TRIM(a.z308_id) = TRIM(ids.z308_id) AND SUBSTR(a.z308_rec_key, 1, 2) = '03'
            LEFT JOIN pwd50.z308 b ON TRIM(b.z308_id) = TRIM(ids.z308_id) AND SUBSTR(b.z308_rec_key, 1, 2) = '01'
            LEFT JOIN pwd50.z304 ON TRIM(SUBSTR(z304_rec_key, 1, 12)) = TRIM(ids.z308_id) AND z304_address_type = 2
            LEFT JOIN pwd50.z305 ON TRIM(SUBSTR(z305_rec_key, 1, 12)) = TRIM(ids.z308_id) AND SUBSTR(z305_rec_key, 13, 5) = 'ALEPH'
            LEFT JOIN (
              SELECT
                TRIM(SUBSTR(z31_rec_key, 1, 12)) rec_key,
                SUM(DECODE(
                  z31_credit_debit,
                  'C', (CASE WHEN z31_status = 'O' THEN z31_sum/100 ELSE 0 END),
                  'D', -(CASE WHEN z31_status = 'O' THEN z31_sum/100 ELSE 0 END),
                  0
                )) AS amount
              FROM """ + library + """.z31
              GROUP BY SUBSTR(z31_rec_key, 1, 12)
            ) bal ON TRIM(bal.rec_key) = TRIM(ids.z308_id)
          WHERE ids.z308_verification_type = '02'
            AND SUBSTR(ids.z308_rec_key, 1, 2) = '04'
            AND TRIM(SUBSTR(ids.z308_rec_key, 3)) = UPPER(:netID)
        """,
      netID = netID)

    columns = [
      "alephId",
      "name",
      "homeLibraryCode",
      "address1",
      "address2",
      "address3",
      "address4",
      "zip",
      "emailAddress",
      "telephone",
      "telephone2",
      "openDate",
      "updateDate",
      "expiryDate",
      "borrowerStatusCode",
      "borrowerTypeCode",
      "loanPermission",
      "holdPermission",
      "renewPermission",
      "balance",
      "campus",
      "campusId",
    ]
    outData = {}
    for values in self.cursor:
      for index in xrange(len(columns)):
        # convert Y/N flag columns to booleans for easier consumption
        if columns[index] in ['loanPermission', 'holdPermission', 'renewPermission']:
          outData[columns[index]] = (values[index] == 'Y')
        else:
          outData[columns[index]] = values[index] if values[index] else '' # Disallow nulls. Return empty string.

    # if we didn't find an aleph account for the netid, don't bother continuing.
    if 'alephId' not in outData:
      return None

    # map codes to descriptions and save them as separate fields
    config = ConfigParser.ConfigParser()
    config.read(cfgPath + '/aleph_mappings.cfg')
    if (config.has_option('HOMELIBRARY', outData['homeLibraryCode'])):
      outData['homeLibrary'] = config.get('HOMELIBRARY', outData['homeLibraryCode'])
    if (config.has_option('BORSTATUS', outData['borrowerStatusCode'])):
      outData['status'] = config.get('BORSTATUS', outData['borrowerStatusCode'])
    if (config.has_option('BORTYPE', outData['borrowerTypeCode'])):
      outData['type'] = config.get('BORTYPE', outData['borrowerTypeCode'])

    return outData
