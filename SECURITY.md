# Security Policy

## Scope
SQL Playground Local is a local SQLite utility. It does not provide a network service and does not send telemetry.

## Trust model
- Treat SQL passed to `exec` as trusted code for the selected database. It can modify or destroy data.
- `query` and `export` intentionally accept only read-oriented statement families and use SQLite's single-statement `execute` API.
- CLI named parameters are bound through SQLite rather than interpolated into SQL.
- Object names used by `describe` are quoted before use.
- Database files may contain sensitive information; protect them with filesystem permissions and backups.

## Reporting
Please report suspected vulnerabilities privately through GitHub's security reporting facilities when available. Do not include real credentials, private databases, or personal data in public issues.

## Supported versions
Security fixes target the latest release on the default branch.

Author: Radwan Abdulhadi Ahmed / @rad03i2
