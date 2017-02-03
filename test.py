import json
import serviceHandler
import joinHandler
from hesburgh import heslog

def debug(name, func, event=None, context=None):
  heslog.test("\n== %s ==" % name)
  out = func(event, context)
  heslog.test("------ func returns with:")
  heslog.test(json.dumps(out, indent = 2))
  heslog.test("== ~%s ==\n" % name)

event = {"path": "/items/pending/illiad"}
debug("aleph - pending", serviceHandler.aleph, event)
debug("illiad - pending", serviceHandler.illiad, event)

event = {"path": "/items/borrowed/illiad", "headers": {"Netid": "hbeachey"}}
debug("aleph - borrowed", serviceHandler.aleph, event)
debug("illiad - borrowed", serviceHandler.illiad, event)

event = {
  "requestContext": {
    "authorizer": {
      "netid": "hbeachey",
    },
  },
}
debug("borrowed", joinHandler.borrowed, event)
debug("pending", joinHandler.pending, event)
