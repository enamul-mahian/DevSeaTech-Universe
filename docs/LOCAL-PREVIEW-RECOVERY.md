# Development Preview Login Recovery

**Only for an authorized owner of the local development preview.** This is not secure identity recovery for a production managed browser.

If both preview passwords are lost, close the preview and run the recovery tool from the **same local Windows/Linux account** that owns the profile data:

Windows PowerShell from the repository checkout:
```powershell
$env:PYTHONPATH="src"
python -m devseatech_browser.recovery
```

The tool requires an exact confirmation phrase. It archives the old `~/.devseatech-browser/auth.json` under `recovery-backups` and allows new credentials to be set at the next browser startup. It does not intentionally delete `profiles`, cookies, cache, or sessions.

**Limitations:** Access to the OS account is not sufficient identity proof for a centrally managed production browser. This operation resets local configuration and can break access to data encrypted with old secrets or disrupt web logins. Make a backup first. Never publish or share your auth archive. There is no cloud recovery or emergency token integration in this milestone. The new DevSeaTech neon login UI is a separate pending implementation task.
