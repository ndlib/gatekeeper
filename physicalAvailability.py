from hesburgh import heslog, hesutil
from serviceRequests.helpers import xml, response
from serviceRequests.aleph import Aleph
from serviceRequests.primo import Primo
import re

# get start/end years for given serial
def startEndYears(fields):
  start = 9999
  end = 0

  # to get sequences of 4 numbers (years)
  yearRe = re.compile('([\d]{4})')

  for publishInfo in xml.iterateOnRecord(fields, 866):
    startYear = 0
    endYear = 9999

    dateInfo = xml.fromRecord(publishInfo, subfield='a')
    date = yearRe.findall(dateInfo)
    if len(date) == 1:
      startYear = date
    elif len(date) == 2:
      startYear, endYear = date
    # else we have <=0 or >2 years, which... ???

    startYear, endYear = (int(startYear), int(endYear))
    start = min(start, startYear)
    end = max(end, endYear)

  # if there is a note that spcifies this journal as "current", "remove" end year
  for location in xml.iterateOnRecord(fields, 852):
    for note in xml.iterateSubfield(location, 'z'):
      if "Currently received" in note:
        end = 9999

  return (start, end)


# query aleph for items that match the isbn or issn + year range
def queryAlephForMatch(isbn, issn, year):
  # WTP is resource type
  query = "%s=%s+NOT+WTP=electronic+resource"
  # 020 and 022 are field searches
  if isbn:
    query = query % ("020", isbn)
  else:
    query = query % ("022", issn)

  aleph = Aleph()
  data = aleph.query(query)

  if not data:
    heslog.error("No data found for entry")
    return 500

  validEntries = []
  for record in data.present.record:
    fields = record.metadata.oai_marc.varfield

    # is valid entry if we're checking a book, or an article without a year
    isValidEntry = not year or isbn is not None

    # we want the year from the 866:a field
    # but we only care if we have an article and year to check against
    if year and issn:
      start, end = startEndYears(fields)
      # if we have an article and a year, entry is only valid if given year is within range
      isValidEntry = year > start and year < end

    if isValidEntry:
      # save this aleph id as valid entry
      validEntries.append(record.doc_number.cdata.strip())

  return validEntries


# given an isbn or issn and year, retrieve all
# primo item records that have physical holdings
# returned data contains record ids, location and availability information
def handler(event, context):
  params = event.get("pathParameters", {})
  year = int(params.get("year", 0))
  isbn = params.get("isbn")
  issn = params.get("issn")

  validEntries = queryAlephForMatch(isbn, issn, year)
  if type(validEntries) is int:
    return response.error(validEntries)

  if len(validEntries) == 0:
    return response.success([])

  # query all the valid aleph ids in primo
  docids = "ndu_aleph" + "+OR+ndu_aleph".join(validEntries)
  # rarely get more than 1 record, but when we do it's valid
  primo = Primo()
  validEntries = primo.query(docids)

  return response.success(validEntries)
