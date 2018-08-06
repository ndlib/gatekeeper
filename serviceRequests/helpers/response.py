from hesburgh import hesutil
import json

def error(code):
  return {
    "statusCode": code,
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }


def success(data):
  return {
    "statusCode": 200,
    "body": json.dumps(data),
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "x-nd-version": hesutil.getEnv("VERSION", 0),
    },
  }