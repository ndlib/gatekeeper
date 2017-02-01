import heslog
import json
from requestType import RequestType
import hackyAPIKey

class Illiad(RequestType):
  def __init__(self, netid):
    super(Illiad, self).__init__(netid)

    self.name = "Illiad"
    self.url = "https://nd.illiad.oclc.org/ILLiadWebPlatform/Transaction/UserRequests/"

    self._setCallback('checkedOut', self.checkedOut)
    self._setCallback('web', self.web)
    self._setCallback('pending', self.pending)


  def _makeIlliadItem(self, data):
    return {
      "title": data.get("LoanTitle", None),
      "journalTitle": data.get("PhotoJournalTitle", None),
      "journalVolume": data.get("PhotoJournalVolume", None), # can hide
      "journalIssue": data.get("PhotoJournalIssue", None), #
      "journalMonth": data.get("PhotoJournalMonth", None), #
      "journalYear": data.get("PhotoJournalYear", None),
      "articleAuthor": data.get("PhotoArticleAuthor", None),
      "articleTitle": data.get("PhotoArticleTitle", None),
      "author": data.get("LoanAuthor", None),
      "publishedDate": data.get("LoanDate", None),
      "requestType": data.get("RequestType", None), #probably doesn't need to display - loan/photocopy
      "dueDate": data.get("DueDate", None),
      "transactionNumber": data.get("TransactionNumber", None),
      "transactionStatus": data.get("TransactionStatus", None), # only in pending
      "pages": data.get("Pages", None),
      # pickup location -- in patron record
      # artickles need link to scanned copy
    }


  def _format(self, data):
    return [ self._makeIlliadItem(i) for i in data ]


  def _illiad(self, path):
    url = self._formatUrl(self.url, path)
    headers = {
      'Content-Type': 'application/json',
      'ApiKey': hackyAPIKey.key,
    }

    response = self._makeReq(url, headers)
    try:
      loaded = json.loads(response)
    except ValueError:
      heslog.error("Response doesn't contain json %s" % response)
      return []

    return self._format(loaded)


  def checkedOut(self):
    path = "<<netid>>?$filter=(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)"
    return self._illiad(path)


  def web(self):
    path = "<<netid>>?$filter=(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)"
    return self._illiad(path)


  def pending(self):
    path = "<<netid>>?$filter=(TransactionStatus%20ne%20%27Request%20Finished%27)%20and%20not%20startswith(TransactionStatus,%20%27Cancel%27)%20and%20not%20(TransactionStatus%20eq%20%27Delivered%20to%20Web%27)%20and%20not%20(TransactionStatus%20eq%20%27Checked%20Out%20to%20Customer%27)"
    return self._illiad(path)
