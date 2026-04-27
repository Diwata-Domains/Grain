# Security Policy

## Supported Versions

Only the latest released version of grain-kit receives security fixes.

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |
| Older   | No        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities by email to: **ss@diwata.domains**

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- The version of grain-kit affected
- Any suggested mitigations if known

You can expect an acknowledgement within **5 business days** and a resolution update within **30 days** for confirmed issues.

We will credit reporters in the release notes unless you prefer to remain anonymous.

## Scope

Grain is a local CLI tool that reads and writes files on the local filesystem. It does not run a server, open network ports, or transmit data to external services unless an agent CLI (e.g. Claude Code, Codex) is explicitly configured to do so by the operator.

Security issues most likely to be relevant:
- Path traversal or unintended file writes in `grain init`, `grain onboard`, or `grain upgrade`
- Command injection via `workflow_loop.yaml` agent configuration
- Unsafe handling of untrusted repository input during `grain onboard` scanning

## Disclosure Policy

We follow coordinated disclosure. Once a fix is available, we will publish a security advisory on GitHub and note the fix in the changelog.
