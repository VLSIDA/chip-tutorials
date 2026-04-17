---
title: Nix
nav_order: 14
---

# Installing Nix

Nix is a purely functional package manager. Unlike `apt` or `brew`, Nix
installs every package into its own hashed directory under `/nix/store/`
and composes ad-hoc environments on demand. The practical consequence for
this class is that a single `nix-shell` invocation can drop you into a
fully-working LibreLane, Magic, Netgen, or OpenROAD environment — no
`sudo apt install`, no "it works on my machine", no version drift.

We use Nix primarily to install **LibreLane** (see [LibreLane](librelane.md)).
Upstream ships a binary cache hosted by the FOSSi Foundation, so the first
`nix-shell` pulls prebuilt binaries rather than compiling anything from
scratch.

If you are running Windows, first set up [WSL](wsl.md) and then follow the
Linux instructions below inside your Ubuntu WSL instance.

## Requirements

- Linux or macOS (14+). On Windows, use WSL (Ubuntu 22.04+).
- `curl` installed. On Ubuntu: `sudo apt install -y curl`.
- Root / `sudo` access (the installer needs it to create `/nix` and set up
  the multi-user daemon).
- ~8 GB free disk for the Nix store once LibreLane has been downloaded.

## Installing Nix

Install Nix with the Determinate Systems installer, pre-configured with
the FOSSi binary cache and the `flakes` / `nix-command` experimental
features that LibreLane needs:

```bash
curl --proto '=https' --tlsv1.2 -fsSL https://artifacts.nixos.org/nix-installer | \
  sh -s -- install --no-confirm --extra-conf "
    extra-substituters = https://nix-cache.fossi-foundation.org
    extra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=
    extra-experimental-features = nix-command flakes
  "
```

Enter your password when prompted. Expect ~5 minutes.

The same command works on Ubuntu, other Linux distros, and macOS 14+.

**Do not `apt install nix`.** The Nix in the Ubuntu package archives is
badly out of date and will not interoperate with the FOSSi cache.

Once the installer finishes, **close every terminal** and open a fresh
one. Nix modifies shell init files, and existing shells won't see the new
`PATH` until they are restarted.

Verify:

```bash
nix --version
```

You should see something like `nix (Nix) 2.2x.x`.

## If you already had Nix installed

If a previous Nix installation exists (e.g. you installed it before
reading this tutorial), you need to add the FOSSi cache and experimental
features manually. Edit `/etc/nix/nix.conf` and ensure it contains:

```
extra-substituters = https://nix-cache.fossi-foundation.org
extra-trusted-public-keys = nix-cache.fossi-foundation.org:3+K59iFwXqKsL7BNu6Guy0v+uTlwsxYQxjspXzqLYQs=
extra-experimental-features = nix-command flakes
```

Then restart the Nix daemon:

```bash
sudo pkill nix-daemon
```

It will be respawned on the next Nix command.

## Basic concepts

### The Nix store

Everything Nix installs lives under `/nix/store/<hash>-<name>/`. Packages
never overwrite each other — two different versions of KLayout can
coexist because their hashes differ. Nothing is ever installed "globally";
your shell's `PATH` gets extended on demand.

### `nix-shell`

`nix-shell` is the everyday command. Running it inside a repository that
has a `shell.nix` or `flake.nix` file drops you into a temporary shell
with every declared dependency on `PATH`. Exiting the shell (Ctrl-D or
`exit`) returns you to your normal environment. Nothing in your home
directory changes.

```bash
cd librelane/
nix-shell           # ← 10 minutes first time (pulling from cache)
librelane --version # ← now available
exit                # ← back to normal
```

### Flakes

A *flake* is a directory with a `flake.nix` file that pins *exact*
versions of every dependency (including Nix itself). LibreLane and the
wafer.space project template both ship as flakes, which is why running
`nix-shell` in those repos gives you an environment guaranteed to match
what the maintainer tested.

### Binary cache

Building LibreLane's dependencies from source would take hours. The
`nix-cache.fossi-foundation.org` substituter we configured above hosts
prebuilt binaries so Nix can just download them. If you ever see Nix
actually *compiling* a toolchain dependency, it means the cache lookup
failed — usually because a trusted-public-key is missing. Re-check
`/etc/nix/nix.conf`.

## Verifying your install with LibreLane

The quickest end-to-end smoke test is:

```bash
git clone https://github.com/librelane/librelane
cd librelane
nix-shell
# inside the nix-shell:
librelane --smoke-test
```

The first `nix-shell` will take 5–15 minutes pulling binaries. Subsequent
shells open in seconds. See [LibreLane](librelane.md) for a full
walkthrough of running an actual design through the flow.

## Troubleshooting

**"experimental feature 'flakes' is disabled"** — the installer's
`--extra-conf` flag didn't land. Open `/etc/nix/nix.conf` and confirm
the three `extra-*` lines are present, then `sudo pkill nix-daemon`.

**"cannot connect to socket at /nix/var/nix/daemon-socket/socket"** —
close and reopen your terminal. The Nix daemon's socket isn't visible to
shells that predate the install.

**"substitute from 'https://nix-cache.fossi-foundation.org' failed:
no 'signature' or 'ca' key found"** — the `extra-trusted-public-keys`
line in `/etc/nix/nix.conf` is missing or mangled. The Nix daemon won't
accept signed packages without the public key.

**First `nix-shell` is downloading *everything* from scratch** — the
substituter URL is wrong or the daemon isn't seeing it. Double-check
`/etc/nix/nix.conf` and restart the daemon.

**Removing Nix entirely** — the Determinate installer ships an uninstall
command: `/nix/nix-installer uninstall`. This reverses every change
including the `/nix` directory and shell init modifications.
