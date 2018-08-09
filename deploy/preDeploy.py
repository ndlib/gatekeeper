from hesburgh import scriptutil, heslog
import json
import os

def gitVersion(stage):
  rev = scriptutil.executeCommand('git rev-parse --short HEAD')
  if rev.get("code") != 0:
    # there was an error, return the stage name
    heslog.warn("Couldn't get git rev %s" % rev)
    return stage
  return rev.get("output").strip()


def runTests():
  os.environ["CI"] = "Local"
  output = scriptutil.executeCommand("cd .. && yarn test")
  print output.get("code")
  print (output.get("code") == 0)
  return output.get("code") == 0


def run(stage):
  heslog.info("Running setup")
  scriptutil.executeCommand("cd .. && ./setup.sh")

  # test currently removed

  return { "env": { "GIT_VERSION": gitVersion(stage) } }
