import json
import serviceHandler
import joinHandler

def debug(name, func, event=None):
  print "\n== %s ==" % name
  out = func(event, None)
  print "------ func returns with:"
  print json.dumps(out, indent = 2)
  print "== ~%s ==\n" % name

# event = {"path": "/items/pending/illiad"}
# debug("aleph - pending", serviceHandler.aleph, event)
# debug("illiad - pending", serviceHandler.illiad, event)

event = {"path": "/items/borrowed/illiad"}
# debug("aleph - borrowed", serviceHandler.aleph, event)
debug("illiad - borrowed", serviceHandler.illiad, event)

debug("borrowed", joinHandler.borrowed)
# debug("pending", joinHandler.pending)
