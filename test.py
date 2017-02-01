import json
import serviceHandler
import joinHandler
import heslog

def debug(name, func, event=None):
  heslog.test("\n== %s ==" % name)
  out = func(event, None)
  heslog.test("------ func returns with:")
  heslog.test(json.dumps(out, indent = 2))
  heslog.test("== ~%s ==\n" % name)

event = {"path": "/items/pending/illiad"}
debug("aleph - pending", serviceHandler.aleph, event)
debug("illiad - pending", serviceHandler.illiad, event)

event = {"path": "/items/borrowed/illiad"}
debug("aleph - borrowed", serviceHandler.aleph, event)
debug("illiad - borrowed", serviceHandler.illiad, event)

debug("borrowed", joinHandler.borrowed)
debug("pending", joinHandler.pending)
