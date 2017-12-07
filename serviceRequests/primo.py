from hesburgh import heslog, hesutil, hestest
import json
from requestType import RequestType

class Primo(RequestType):
  def __init__(self, userId):
    super(Primo, self).__init__(userId)

    self.name = "Primo"

    self.userId = userId
    self.institution = "NDU"
    self.url = hesutil.getEnv("PRIMO_URL", throw=True)
    self.displayUrl = hesutil.getEnv("PRIMO_DISPLAY_URL", throw=True)

    self._setCallback('favorites', self.favorites)


  def favorites(self):
    url = self.url \
              .replace("<<api>>", "eshelf") \
              .replace("<<institution>>", self.institution) \
              .replace("<<userId>>", self.userId)

    heslog.info("Getting primo favorites")
    res = self._makeReq(url, {})

    if not res:
      heslog.error("Contacting primo failed - likely because of permissions")
      return None

    res = json.loads(res)

    if res.get("errorCode"):
      heslog.error(res)
      return {}

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
