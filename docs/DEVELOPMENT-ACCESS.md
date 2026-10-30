# Development Access and Repository Visibility

## Repository visibility
The owner requests public repository visibility temporarily so Claude can inspect the project. This has NOT been applied by the codebase. Visibility changes require an authorized GitHub account in Settings > General > Danger Zone. Before switching, audit full Git history for secrets, personal identifiers, licenses, and non-redistributable binaries. Remember that making a repository public exposes its commit history, not just current files.

A safer alternative is read-only collaborator/GitHub App access to the private repository.

## Development login
The development preview currently uses one Master password and a separate Administrator password. There is not yet a username-based login or production license authentication.
- Administrator authorization is now cached **in memory for the current application session** after successful verification, reducing repeated prompts.
- Restarting the app clears the admin unlock.
- Do NOT hardcode shared demo credentials into a public repository or published executable.
- A future test-only demo account may be provisioned through per-install, randomly generated credentials and clearly segregated demo storage, with no production privileges.
- To regain access to the existing preview, use the owner-confirmed preview recovery flow. Do not delete profile directories.
- Trial licensing and paid subscriptions remain requirements under development, not authorization bypasses.

## Security boundary
The in-memory admin-unlock is acceptable for this early local development preview only; production requires a time-limited privileged session and reauthentication for destructive actions such as license revocation, profile deletion, key changes and remote policy updates.
