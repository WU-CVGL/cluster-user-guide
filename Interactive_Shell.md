[English](Interactive_Shell.md) | [简体中文](Interactive_Shell.zh.md)

# Interactive shells, IDEs, and ports

Use the [agent workflow](Agent_Workflow.md) with [Determined Cluster MCP](https://github.com/WU-CVGL/determined_cluster_mcp) to plan and manage a shell. This page covers interactive access, IDE connections and the shell lifecycle; native CLI commands are included for manual operation.

A Determined shell is a temporary interactive development environment. Use it to inspect an image, reproduce an issue, or attach an IDE. Put edits, caches worth keeping, and debug outputs on shared storage.

For an unattended one-off script, use a command. For long training or overnight work, use an experiment with shared checkpoints.

## Start a shell

Check current scheduler slots first:

```bash
det slot list
```

Review [`examples/compute/shell.yaml`](examples/compute/shell.yaml), replace its placeholders, and start the shell:

```bash
det shell start --config-file examples/compute/shell.yaml
```

The command connects through SSH when the shell is ready. To detach immediately and print the ID:

```bash
det shell start --detach --config-file examples/compute/shell.yaml
```

Native `det shell start` can queue if no slot is available. The maintained MCP/`determined-compute` workflow checks current capacity and defaults to `allow_queue: false`; see [Agent Workflow](Agent_Workflow.md).

## Reconnect and stop

List your shells and reconnect:

```bash
det shell list
det shell open <shell-id>
```

Print the underlying SSH command when another tool needs it:

```bash
det shell show-ssh-command <shell-id>
```

`show-ssh-command` is the current spelling. The older `show_ssh_command` alias is deprecated upstream.

Stop the shell when finished:

```bash
det shell kill <shell-id>
```

## VS Code Remote SSH

1. Install the **Remote - SSH** extension.
2. Run `det shell show-ssh-command <shell-id>` on the computer running VS Code.
3. Add the printed command through **Remote-SSH: Add New SSH Host**.
4. Connect to the new host and open your mapped project directory, such as `/run/determined/workdir/home/project`.

The generated command includes a retained task key and Determined's proxy command. Generate a new entry for a new shell ID. Do not copy private-key material into the repository.

## PyCharm

1. Generate the SSH command with `det shell show-ssh-command <shell-id>`.
2. Translate it into an entry in your OpenSSH config, keeping its `ProxyCommand`, identity file, and other options.
3. In **Settings | Tools | SSH Configurations**, choose **OpenSSH config and authentication agent**.
4. Test the connection, then use it for a remote interpreter if needed.

PyCharm's UI may not represent every option in the generated command, so the OpenSSH config entry is the reliable source.

## Forward a local port

Pass SSH options after `--`. For example, forward container port `7007` to the same local port:

```bash
det shell open <shell-id> -- -L7007:localhost:7007
```

Then start the service inside the shell, binding it to the container's loopback interface, and open `http://localhost:7007` locally.

You can also forward a port on first connection:

```bash
det shell start --config-file examples/compute/shell.yaml -- -L7007:localhost:7007
```

Choose an unused local port if `7007` is already occupied. Expose only the ports you need, and do not bind unauthenticated services to public interfaces.

## Keep work recoverable

- Edit code under the mapped workspace.
- Write debug artifacts to a mapped output directory.
- Treat installed packages and files elsewhere in the container as disposable.
- Record the image tag and code revision needed to reproduce the session.
- Move long training or overnight work into an experiment with shared checkpoints.

## Verified shell cleanup policy

Verified on 2026-09-20, the cleanup rule applies to **shells** and measures container GPU utilization. It does not measure keyboard or SSH activity.

- Grafana evaluates the rule every 60 seconds.
- A shell becomes alerting after its maximum mapped GPU utilization remains below 10% for 15 minutes.
- The watchdog scans at the top of each hour. The first matching scan sends a warning; if the same alert is still present at the next top-of-hour scan, it stops the shell.
- The 30-minute query window is only the data-reading window; it is not another waiting period.
- No-data and query-error states are not treated as alerts by this rule. Other Determined workload kinds are not stopped by this shell watchdog.

With continuously low GPU utilization, warning and cleanup phases imply a theoretical stop time of roughly 75–135 minutes, depending on evaluation and hourly scan alignment. This is not a strict two-hour timeout or a guaranteed deadline; scan timing and service failures can change it.

A stopped shell cannot be reconnected. Keep work on shared storage and respond to warnings promptly. Use a command for an unattended one-off script, or an experiment for long training and overnight work.

The deployment source is linked from [Cluster Reference](Cluster_Reference.md); recheck this dated policy after watchdog or Grafana changes.
