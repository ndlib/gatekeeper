from hesburgh import heslog, hesutil, hestest
import json
from requestType import RequestType

class Illiad(RequestType):
  def __init__(self, netid):
    super(Illiad, self).__init__(netid)

    self.name = "Illiad"
    self.url = hesutil.getEnv("ILLIAD_URL", throw=True)

    self._setCallback('borrowed', self.borrowed)
    self._setCallback('pending', self.pending)


  def _makeIlliadItem(self, data):
    if data.get("RequestType") == "Loan":
      title = data.get("LoanTitle")
      author = data.get("LoanAuthor")
      published = data.get("LoanDate")
    else:
      title = data.get("PhotoArticleTitle")
      author = data.get("PhotoArticleAuthor")
      published = data.get("PhotoJournalYear")

    # 2017-06-28T00:00:00 => 2017-06-28
    dueDate = data.get("DueDate", "")
    if dueDate:
      dueDate = dueDate.split("T")[0]

    return {
      "title": title,
      "author": author,
      "dueDate": dueDate,
      "published": published,
      "status": data.get("TransactionStatus", None),

      "transactionNumber": data.get("TransactionNumber", None),
      # pickup location -- in patron record
      # artickles need link to scanned copy
    }


  def _format(self, data):
    return [ self._makeIlliadItem(i) for i in data ]


  def _illiad(self, path, requestType):
    url = self._formatUrl(self.url, path)
    headers = {
      'Content-Type': 'application/json',
      'ApiKey': hesutil.getEnv("ILLIAD_KEY", throw=True),
    }

    data = hestest.get(self.netid)
    if data:
      response = data.get("illiad_" + requestType , "")
    else:
      response = self._makeReq(url, headers)

    try:
      loaded = json.loads(response)
    except ValueError:
      heslog.error("Response doesn't contain json %s" % response)
      return []

    return self._format(loaded)


  def borrowed(self):
    return {
      "checkedOut": self.checkedOut(),
      "web": self.web(),
    }


  def checkedOut(self):
    path = "<<netid>>?$filter=(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)"
    return self._illiad(path, "checkedOut")


  def web(self):
    path = "<<netid>>?$filter=(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)"
    return self._illiad(path, "web")


  def pending(self):
    path = "<<netid>>?$filter=(TransactionStatus%20ne%20%27Request%20Finished%27)%20and%20not%20startswith(TransactionStatus,%20%27Cancel%27)%20and%20not%20(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)%20and%20not%20(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)"
    return self._illiad(path, "pending")
