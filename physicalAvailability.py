from hesburgh import heslog, hesutil
from serviceRequests.helpers import xml, response
from serviceRequests.aleph import Aleph
from serviceRequests.primo import Primo
import re

# get start/end years for given serial
def startEndYears(fields):
  start = 9999
  end = 0

  # All documented 866:a cases
  # 2004:no.1-2004:no.6
  # 1995-2004
  # 2003:winter-2003:spring
  # 1998:2-1998:4
  # 2005:stycz.-2005:luty=2485-2492
  # v.16(1994/1995)-v.19(2001/2002)
  # v.20:no.1(2002:July)-v.20:no.2(2002:Nov.)
  # v.275:no.8728(1995:Oct.21)-v.280:no.8844(1998:Feb.7)
  # v.1:no.1(1967)-v.8:no.3(2004)
  # v.25:no.25(2001:out.16/24)-v.26:no.15(2002:maio 16/XX)

  # Years are:
  # a. inside parens
  # b. no parens:
    # before an "="
      # 1. the start of a string
      # 2. directly follows a dash
      # 3. directly follows a slash

  # to get everything within braces, we split with "yearRe"
  parensRe = re.compile('\((.*?)\)')
  # get sequences of 4 numbers, these should be years (used on data from parensRe)
  yearRe = re.compile('([\d]{4})')

  # Should match \A = start of string, / or - and then 4 numbers (the year)
  noParensRe = re.compile('[\A/-]([\d]{4})')

  for publishInfo in xml.iterateOnRecord(fields, 866):
    startYear = start
    endYear = end

    dateInfo = xml.fromRecord(publishInfo, subfield='a')

    # if there are parens, year is inside them
    if '(' in dateInfo:
      dates = parensRe.findall(dateInfo)
      for d in dates:
        split = yearRe.findall(d)
        for year in split:
          year = int(year)
          start = min(start, year)
          end = max(end, year)
    else:
      # split on "=" to be correct in the following case
      # 2005:stycz.-2005:luty=2485-2492
      dateInfo = dateInfo.split("=")[0]
      dates = noParensRe.findall(dateInfo)
      for year in dates:
        year = int(year)
        start = min(start, year)
        end = max(end, year)

  # if there is a note that spcifies this journal as "current", "remove" end year
  for location in xml.iterateOnRecord(fields, 852):
    for note in xml.iterateSubfield(location, 'z'):
      if "Currently received" in note:
        end = 9999

  return (start, end)


# query aleph for items that match the isbn or issn + year range
def queryAlephForMatch(isbn, issn, year):
  year = int(year)

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
    return 204

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
      isValidEntry = (year >= start) and (year <= end)

    if isValidEntry:
      # save this aleph id as valid entry
      validEntries.append(record.doc_number.cdata.strip())

  return validEntries


# given an isbn or issn and year, retrieve all
# primo item records that have physical holdings
# returned data contains record ids, location and availability information
def handler(event, context):
  params = event.get("queryStringParameters", {})
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
