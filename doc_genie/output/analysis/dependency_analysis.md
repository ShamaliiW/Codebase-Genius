# Dependency Analysis

## Overview

This document provides a comprehensive analysis of the project dependencies for geveoFinal.

## Summary

- **Total Dependencies:** 41
- **Production Dependencies:** 22
- **Development Dependencies:** 19

## Dependencies by Package Manager


### NPM

#### Production Dependencies

- **@angular/animations** `~8.2.0`
- **@angular/cdk** `~8.2.3`
- **@angular/common** `~8.2.0`
- **@angular/compiler** `~8.2.0`
- **@angular/core** `~8.2.0`
- **@angular/fire** `^5.2.1`
- **@angular/forms** `~8.2.0`
- **@angular/material** `^8.2.3`
- **@angular/platform-browser** `~8.2.0`
- **@angular/platform-browser-dynamic** `~8.2.0`
- **@angular/router** `~8.2.0`
- **bootstrap** `^4.3.1`
- **firebase** `^7.3.0`
- **hammerjs** `^2.0.8`
- **jquery** `^3.4.1`
- **ngx-bootstrap** `^5.2.0`
- **ngx-editor** `^4.1.0`
- **popper.js** `^1.16.0`
- **rxjs** `~6.4.0`
- **stompjs** `^2.3.3`
- **tslib** `^1.10.0`
- **zone.js** `~0.9.1`

#### Development Dependencies

- **@angular-devkit/build-angular** `^0.802.2`
- **@angular/cli** `~8.2.2`
- **@angular/compiler-cli** `~8.2.0`
- **@angular/language-service** `~8.2.0`
- **@types/jasmine** `~3.3.8`
- **@types/jasminewd2** `~2.0.3`
- **@types/node** `~8.9.4`
- **codelyzer** `^5.0.0`
- **jasmine-core** `~3.4.0`
- **jasmine-spec-reporter** `~4.2.1`
- **karma** `~4.1.0`
- **karma-chrome-launcher** `~2.2.0`
- **karma-coverage-istanbul-reporter** `~2.0.1`
- **karma-jasmine** `~2.0.1`
- **karma-jasmine-html-reporter** `^1.4.0`
- **protractor** `~5.4.0`
- **ts-node** `~7.0.0`
- **tslint** `~5.15.0`
- **typescript** `~3.5.3`


## Security Considerations

1. **Regular Updates:** Keep dependencies up to date to avoid security vulnerabilities
2. **Vulnerability Scanning:** Use tools like `npm audit`, `safety`, or `cargo audit`
3. **License Compliance:** Review licenses of all dependencies

## Recommendations

1. **Dependency Management:** Use lock files to ensure consistent builds
2. **Minimal Dependencies:** Remove unused dependencies to reduce attack surface
3. **Version Pinning:** Consider pinning critical dependencies to specific versions

---

*Generated on 2025-09-02 23:24:34*