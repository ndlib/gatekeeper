from hesburgh import heslog, hesutil, hestest
import json
from requestType import RequestType

class Primo(RequestType):
  def __init__(self):
    super(Primo, self).__init__()

    self.name = "Primo"
    self.institution = "NDU"
    self.url = hesutil.getEnv("SEARCH_PRIMO_URL", throw=True)

    self._setCallback('search', self.search)


  def search(self):
    url = self.url \
              .replace("<<query>>", "book") \
              .replace("<<institution>>", self.institution)

    heslog.info("Getting primo favorites")
    res = self._makeReq(url, {})

    if not res:
      heslog.error("Contacting primo failed - likely because of permissions")
      return None

    res = json.loads(res)

    if res.get("errorCode"):
      heslog.error(res)
      return {}

    return res

    items = res.get("basket-items")
    heslog.info("Got %s item(s)" % len(items))

    ret = []
    for item in items:
      docId = item.get("pnxId")
      display = None
      if docId:
        display = self.displayUrl \
                      .replace("<<institution>>", self.institution) \
                      .replace("<<docId>>", docId)

      ret.append({
        "title": item.get("title"),
        "author": item.get("author"),
        "display": display,
        "type": item.get("@TYPE"),
        "id": item.get("@id"),
      })

    return ret
