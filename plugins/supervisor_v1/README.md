# Uninstalled supervisor v1 plugin

This source-controlled package is outside `.journal/plugins` and is not installed or enabled by deployment packaging. The manifest uses the existing journal plugin service lifecycle: `PluginServices` starts/stops `bridge`, `PluginHealth` checks its Unix health socket, and the `when` condition keeps it off until an owner/operator creates `STAGING_AUTHORIZED` in the plugin data directory.

The service spools only task/check row references and timestamps to the dedicated `supervisor_hints` volume. It does not read journal rows, credentials or source files and does not call a model or apply journal mutations. Gateway mounts the spool read-only. A later runtime adapter consumes the hints through the shared journal admission route; timer and hints must use that same route. Until the private routes, the task-111 stdio client, bounded cost controls, and B10 isolation checks exist, keep the plugin uninstalled and enrollment disabled.

An owner/operator may install the package in authorized disposable staging only after reviewing the manifest and runbook:

```sh
journal plugin install ./plugins/supervisor_v1
```

This command is documentation for the later authorized staging procedure; artifact packaging does not run it.
