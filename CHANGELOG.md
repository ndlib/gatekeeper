# Change Log

## [v2018.5](https://github.com/ndlib/gatekeeper/tree/v2018.5)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2018.4...v2018.5)

### New Features:
- Add `/location` endpoint to get the physical holdings location of an issn or isbn [#36](https://github.com/ndlib/gatekeeper/pull/36)

### Bug Fixes:
- Don't strip characters (like ()) from the ends of titles. Only strip `.` and ` ` [#35](https://github.com/ndlib/gatekeeper/pull/35)


## [v2018.4](https://github.com/ndlib/gatekeeper/tree/v2018.4)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2018.3...v2018.4)

### Bug Fixes:
- Students shouldn't see fines - they use Student accounts - make sure other fines are correct [#34](https://github.com/ndlib/gatekeeper/pull/34)

## [v2018.3](https://github.com/ndlib/gatekeeper/tree/v2018.3)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2018.2...v2018.3)

### New features/enhancements:
- Add account balance to user information [#33](https://github.com/ndlib/gatekeeper/pull/33)


## [v2018.2](https://github.com/ndlib/gatekeeper/tree/v2018.2) (v2018.2)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2018.1...v2018.2)

### Bug fixes:
- Fix aleph renew funcitonality [#32](https://github.com/ndlib/gatekeeper/pull/32)


## [v2018.1](https://github.com/ndlib/gatekeeper/tree/v2018.1) (v2018.1)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2017.2...v2018.1)

### New features/enhancements:
- Allow Aleph requests to specify library to query [#25](https://github.com/ndlib/gatekeeper/pull/25)
- Return more aleph information on findItem results [#29](https://github.com/ndlib/gatekeeper/pull/29)


## [v2017.2](https://github.com/ndlib/gatekeeper/tree/v2017.2) (v2017.2)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2017.1...v2017.2)

### New features/enhancements:
- Add ability to query primo favorites [#26](https://github.com/ndlib/gatekeeper/pull/26)


## [v2017.1](https://github.com/ndlib/gatekeeper/tree/v2017.1) (v2017.1)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v2017.0...v2017.1)

### New features/enhancements:
- Split aleph/ill queries [#22](https://github.com/ndlib/gatekeeper/pull/22)
- Add ability to update home library [#21](https://github.com/ndlib/gatekeeper/pull/21)


## [2017.0](https://github.com/ndlib/gatekeeper/tree/v2017.0) (2017-08-24)
[Full Changelog](https://github.com/ndlib/gatekeeper/compare/v0.1.0...v2017.0)

### New features/enhancements:
- Added Aleph renew functionality [#19](https://github.com/ndlib/gatekeeper/pull/19)
- Added version header to all API calls [#18](https://github.com/ndlib/gatekeeper/pull/18)
- Add manual creation of log groups for lambdas [#20](https://github.com/ndlib/gatekeeper/pull/20)

### Bug fixes:
- Make sure cors headers are on error responses
