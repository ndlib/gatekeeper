from aleph import Aleph
from illiad import Illiad

class Requester(object):
  def __init__(self, netid):
    super(Requester, self).__init__()
    self.netid = netid

    self.callers = [
      Aleph(netid),
      Illiad(netid),
    ]


  def itemsForType(self, callType):
    ret = []
    for caller in self.callers:
      data = caller.request(callType)
      if isinstance(data, list):
        ret.extend(data)
      else:
        print "The %s data type isn't supported for items at the moment, must be list" % type(data)

    return ret


  def checkedOut(self):
    return self.itemsForType('checked_out')


  def web(self):
    return self.itemsForType('web')


  def pending(self):
    return self.itemsForType('pending')
