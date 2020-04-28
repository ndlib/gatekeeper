from hesburgh import heslog, hesutil, hestest
from serviceRequests.aleph import Aleph
from serviceRequests.illiad import Illiad
from serviceRequests.primo import Primo
from serviceRequests.helpers import response

hestest.init(__file__, "testdata")

def aleph(event, context):
  path = event.get("path")
  requestType = path.split('/')[-1]

  queryParams = event.get("queryStringParameters") or {}
  library = queryParams.get("library")
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)

  heslog.addLambdaContext(event, context, fn="aleph", requestType=requestType)

  if netid is None:
    clientId = event.get("requestContext", {}).get("authorizer", {}).get("clientid", None)
    authorizedClients = hesutil.getEnv("AUTHORIZED_CLIENTS", throw=True).split(',')

    if clientId is None:
      heslog.error("Invalid token or no token provided")
      return response.error(400)
    elif clientId not in authorizedClients:
      heslog.error("Okta client " + clientId + " is not authorized to perform this action.")
      return response.error(401)
    else:
      netid = queryParams.get("netid")

  if requestType is None:
    heslog.error("no query type specified")
    return response.error(400)

  if library is None:
    heslog.info("No library specified, using ndu50")
    library = "ndu50"

  heslog.info("Starting request")
  data = Aleph(netid, library).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
  return response.success(data)


def illiad(event, context):
  path = event.get("path")
  requestType = path.split('/')[-1]
  queryParams = event.get("queryStringParameters") or {}
  netid = event.get("requestContext", {}).get("authorizer", {}).get("netid", None)

  heslog.addLambdaContext(event, context, fn="illiad", requestType=requestType)

  if netid is None:
    clientId = event.get("requestContext", {}).get("authorizer", {}).get("clientid", None)
    authorizedClients = hesutil.getEnv("AUTHORIZED_CLIENTS", throw=True).split(',')

    if clientId is None:
      heslog.error("Invalid token or no token provided")
      return response.error(400)
    elif clientId not in authorizedClients:
      heslog.error("Okta client " + clientId + " is not authorized to perform this action.")
      return response.error(401)
    else:
      netid = queryParams.get("netid")

  if requestType is None:
    heslog.error("no query type specified")
    return response.error(400)

  heslog.info("Starting request")
  data = Illiad(netid).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
  return response.success(data)


def primo(event, context):
  queryParams = event.get("queryStringParameters", {})
  requestType = queryParams.get("type", None)
  userId = queryParams.get("aleph-id", None)

  heslog.addLambdaContext(event, context, fn="primo", requestType=requestType)

  if userId is None:
    heslog.error("no userId")
    return response.error(400)

  if requestType is None:
    heslog.error("no query type specified")
    return response.error(400)

  heslog.info("Starting request")
  data = Primo(userId).request(requestType)

  if data is None:
    heslog.info("No information returned from request")
  return response.success(data)

