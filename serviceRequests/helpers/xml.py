def iterateSubfield(data, subfield):
  for sub in data.subfield:
    if sub["label"] == subfield:
      yield sub.cdata.strip()


# helper so we don't have to have if logic on every field below
def iterateOnRecord(data, idToGet, i1=None, i2=None):
  # make sure our identifiers are strings
  idToGet = str(idToGet)
  if i1 is not None:
    i1 = str(i1)
  if i2 is not None:
    i2 = str(i2)

  # iterate over all fields, yielding only those that match our identifiers
  for field in data:
    if ((field["id"] == idToGet or field["label"] == idToGet) and
        (not i1 or (i1 and field["i1"] == i1)) and
        (not i2 or (i2 and field["i2"] == i2))
      ):
      yield field

# helper to get first (or only) element of a field
def fromRecord(data, idToGet=None, i1=None, i2=None, subfield=None):
  # ensure we're using strings
  if subfield is not None:
    subfield = str(subfield)

  # get the record, use given data if we don't have ids (gettings subfield)
  found = None
  if not idToGet:
    found = data
  else:
    # this allows us to reuse code, we have to start a loop to deref the iterator
    for x in iterateOnRecord(data, idToGet, i1, i2):
      found = x
      break

  # If we want to find a subfield of the above field
  if found and subfield:
    for sub in found.subfield:
      if sub["label"] == subfield:
        # Found the desired subfield, return it's data
        return sub.cdata.strip()
    # Didn't find the subfield, return failure
    return None
  return found

# helper to append to a string with a newline
def appendDataStr(data, key, toAppend):
  return toAppend.strip() if key not in data else ("%s\n%s" % (data.get(key, ""), toAppend.strip()))
