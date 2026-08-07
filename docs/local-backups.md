# Local SaaS backups

BetterSaaS schedules one database-only backup at 01:30 in the Frappe system timezone.
The control site and every active `SaaS Sites` record are queued independently on the
long queue. Unused stock sites are cleaned but are not backed up.

Backups use Frappe's native format and remain under each site's `private/backups`
directory. The OneHash Backups page reads that directory directly. A System Manager
can request a temporary public/private files backup from the page; files backups are
not generated automatically.

Defaults can be overridden in `common_site_config.json`:

```json
{
  "local_backup_count": 7,
  "local_backup_min_free_gb": 20,
  "local_file_backup_retention_hours": 24,
  "local_backup_bench_command": "/path/to/bench"
}
```

The nightly cleanup retains the newest database/config sets, expires generated file
archives, and removes only timestamped legacy backup ZIPs directly under
`site/private`. It does not inspect or delete files in `private/files`.

These backups are local recovery points. They do not protect against loss of the
server or its disk.
