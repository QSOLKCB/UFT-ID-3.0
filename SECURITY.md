# Security Policy

UFT-ID 3.0 is primarily a research and reproducibility repository. Security issues can still arise in experiment runners, dependency files, data parsers, CI workflows, and future formalization tooling.

## Reporting a vulnerability

Please use GitHub's private security-advisory mechanism for vulnerabilities that could expose secrets, execute untrusted code, corrupt data, or compromise users running repository tools.

For ordinary scientific errors, incorrect equations, questionable assumptions, citation problems, or failed reproductions, open a normal issue or pull request instead. Scientific disagreement is not a security vulnerability.

## Scope

Security-relevant examples include:

- command injection in experiment tooling;
- unsafe handling of downloaded datasets or archives;
- dependency confusion or malicious package substitution;
- secret leakage in CI;
- path traversal or destructive file operations;
- unsafe deserialization;
- code execution from untrusted research artifacts.

## Research integrity issues

If a result appears fabricated, irreproducible, incorrectly attributed, or materially overstated, report it as a research-integrity issue with enough information to reproduce the concern. The project should preserve disputed results and their resolution history rather than silently rewriting the record.
