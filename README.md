# gatekeeper
Lambdas that interact with Aleph, Primo and ILLiad

## Install
run `./setup.sh`

## Deploy
### Requirements
[hesdeploy](https://github.com/ndlib/hesburgh_utilities/blob/master/scripts/HESDEPLOY.md) (pip install hesdeploy)
Access to

## API
Retrieve aleph information about a user denoted by the JWT
```
GET /aleph?type=[borrowed|pending|user]&library=[ndu50|hcc50|bci50|smc50]
headers:
  Authorization: [JWT]
```
Retrieve ILLiad information about a user denoted by the JWT
```
GET /illiad?type=[borrowed|pending]
headers:
  Authorization: [JWT]
```
Retrieve Primo information about a user denoted by the aleph-id query parameter
```
GET /primo?type=[favorites]&aleph-id=[alephId]
headers:
  Authorization: [JWT]
```
Retrieve aleph information about a specific item
```
GET /aleph/{systemId}
```
Renew Aleph Item for user specified by aleph-id
```
post /aleph/renew?barcode=[barcode]&aleph-id=[alephId]
headers:
  Authorization: [JWT]
```
Update Aleph home library for user specified by aleph-id
```
post /aleph/update?library=[libraryId]&aleph-id=[alephId]
headers:
  Authorization: [JWT]
```
