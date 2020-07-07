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
    query = """
      SELECT
        z36_rec_key, z36_number, z36_loan_date, z36_returned_date, z36_due_date, z36_material,
        z13_rec_key, z13_author, z13_title, z13_imprint, z13_year,
        isbn,
        issn,
        z30_barcode, z30_call_no, z30_description,
        edition,
        institution
      FROM ndrep.circ_history_mv
      WHERE netid = UPPER(:netID)
    """
    self.cursor.execute(query, netID = netID)

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
            aleph_id,
            patron_name,
            home_library,
            local_address_line_1,
            local_address_line_2,
            local_address_line_3,
            local_address_line_4,
            local_address_zip,
            local_email_address,
            local_address_telephone,
            local_address_telephone_2,
            open_date,
            last_update_date,
            expiry_date,
            bor_status,
            bor_type,
            loan_permission,
            hold_permission,
            renew_permission,
            nd_balance + hc_balance AS balance,
            SUBSTR(campus_id, 1, 3) AS campus,
            SUBSTR(campus_id, 4) AS campus_id
          FROM ndrep.patron_mv
          WHERE netid = UPPER(:netID)
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
