# Linux95 Installer Identity and Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Debian-facing Calamares identity in Linux95 with a Linux95-owned launcher and branding layer while preserving Debian 13 / Calamares installation behavior.

**Architecture:** Keep `calamares` and `calamares-settings-debian` as the functional installer engine. Add project-owned Linux95 branding under `/etc/calamares/branding/linux95`, switch the installed Calamares settings to `branding: linux95` during the live-build, and launch through a tiny Linux95 wrapper that delegates to Debian's proven `/usr/bin/calamares-install-debian` helper. This keeps partitioning, user creation, bootloader setup, EFI support, and Debian live-media handling unchanged while replacing only the visible product identity.

**Tech Stack:** Debian 13 (Trixie), live-build, Calamares, POSIX shell, Python 3 source checks, IceWM/PCManFM desktop integration.

**Spec:** `docs/superpowers/specs/2026-10-01-linux95-installer-identity-polish-design.md`

## Global Constraints

- Preserve Debian 13 (Trixie) as the distribution base.
- Preserve the existing IceWM Linux95 live session and APT package-management behavior.
- Keep `calamares` and `calamares-settings-debian`; do not fork or replace the Calamares installer engine.
- Preserve existing partitioning, filesystem creation, user creation, BIOS install, UEFI install, and live-media handling.
- The desktop launcher must not directly execute `/usr/bin/calamares-install-debian`.
- The desktop launcher must execute `/usr/bin/linux95-installer`.
- `/usr/bin/linux95-installer` must delegate to `/usr/bin/calamares-install-debian`; it must not duplicate Debian's fstab, X11, privilege-escalation, or installer-engine logic.
- The live image must select `branding: linux95` in `/etc/calamares/settings.conf` at build time, not by modifying package-owned configuration when the installer is launched.
- Linux95 branding lives at `/etc/calamares/branding/linux95/branding.desc`.
- Branding `componentName` is `linux95`.
- Branding `productName` and `shortProductName` are `Linux95`.
- Branding `version` and `shortVersion` are `4.2`.
- Branding `versionedName` and `shortVersionedName` are `Linux95 4.2`.
- Branding `bootloaderEntryName` is `Linux95`.
- The installer desktop entry remains named `Install Linux95`.
- The installer desktop entry must use a Linux95-owned icon name, `linux95-installer`, rather than `install-debian`.
- Reuse existing Linux95 artwork where suitable; do not add unrelated artwork or redesign the whole desktop.
- Do not modify the experimental from-scratch `Linux95-Kernel` repository.
- Stage only task files; do not merge or publish without explicit user direction.

## Review Focus

- If Debian changes `/etc/calamares/settings.conf` formatting, the build-time branding selector must fail loudly instead of silently leaving `branding: debian`; Task 2 tests this.
- If `/usr/bin/calamares-install-debian` is missing from a built image, the Linux95 wrapper must return a clear non-zero failure; Task 1 tests this.
- The Linux95 wrapper must not copy Debian's partitioning/fstab/xhost/pkexec implementation into project code; Task 1 source checks pin the one-line delegation boundary.
- Branding must not alter bootloader behavior or module sequence; Task 2 compares the branding-only build change and keeps Debian module settings untouched.
- A built ISO must still complete a clean installation and boot from disk in both the normal VM smoke path and at least one firmware mode; Task 4 owns acceptance coverage.

---

### Task 1: Add a Linux95-owned installer entry point and source checks

**Files:**
- Create: `tests/installer_source_checks.py`
- Create: `config/includes.chroot/usr/bin/linux95-installer`
- Modify: `config/includes.chroot/etc/skel/Desktop/Install Linux95.desktop`

**Interfaces:**
- Consumes: Debian-provided `/usr/bin/calamares-install-debian`.
- Produces: `/usr/bin/linux95-installer`, the stable Linux95 launcher used by the desktop entry and later acceptance tests.

- [ ] **Step 1: Write the failing launcher/source checks**

Create `tests/installer_source_checks.py` with assertions that:
- `config/includes.chroot/usr/bin/linux95-installer` exists;
- its shebang is `/bin/sh`;
- it checks that `/usr/bin/calamares-install-debian` is executable;
- it delegates with `exec /usr/bin/calamares-install-debian "$@"`;
- it contains none of `parted`, `mkfs`, `mount`, `grub-install`, `xhost`, `pkexec`, or `/etc/fstab`;
- `Install Linux95.desktop` contains `Exec=/usr/bin/linux95-installer`;
- the desktop entry does not contain `Exec=/usr/bin/calamares-install-debian`;
- the desktop entry contains `Icon=linux95-installer`;
- the desktop entry does not contain `Icon=install-debian`.

- [ ] **Step 2: Run the check to verify RED**

Run:

```bash
python3 tests/installer_source_checks.py
```

Expected: FAIL because the Linux95 wrapper is absent and the existing desktop entry still points directly at the Debian wrapper and Debian icon.

- [ ] **Step 3: Add the minimal Linux95 wrapper**

Create executable `config/includes.chroot/usr/bin/linux95-installer` with this behavior:
- `#!/bin/sh`
- `set -eu`
- if `/usr/bin/calamares-install-debian` is not executable, print `Linux95 Installer: Debian Calamares helper not found` to stderr and exit `127`;
- otherwise `exec /usr/bin/calamares-install-debian "$@"`.

Do not add any installer-engine logic to this file.

- [ ] **Step 4: Point the desktop launcher at Linux95**

In `config/includes.chroot/etc/skel/Desktop/Install Linux95.desktop` preserve:
- `Name=Install Linux95`
- `Comment=Install Linux95 onto this computer`
- `Terminal=false`
- `Categories=System;`

Change exactly:
- `Exec=/usr/bin/linux95-installer`
- `Icon=linux95-installer`

- [ ] **Step 5: Run Task 1 GREEN**

Run:

```bash
python3 tests/installer_source_checks.py
sh -n config/includes.chroot/usr/bin/linux95-installer
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add \
  tests/installer_source_checks.py \
  config/includes.chroot/usr/bin/linux95-installer \
  "config/includes.chroot/etc/skel/Desktop/Install Linux95.desktop"
git commit -m "Add Linux95 installer launcher"
```

### Task 2: Add Linux95 Calamares branding and select it at ISO build time

**Files:**
- Create: `config/includes.chroot/etc/calamares/branding/linux95/branding.desc`
- Create: `config/hooks/live/0910-linux95-calamares-branding.hook.chroot`
- Modify: `tests/installer_source_checks.py`

**Interfaces:**
- Consumes: Debian package-owned `/etc/calamares/settings.conf` installed by `calamares-settings-debian`.
- Produces: Linux95 branding component `linux95` and a deterministic live-build hook that switches only the `branding:` selector.

- [ ] **Step 1: Extend source checks for branding**

Add assertions that:
- `branding.desc` exists and contains `componentName: linux95`;
- `productName: Linux95`;
- `shortProductName: Linux95`;
- `version: "4.2"`;
- `shortVersion: "4.2"`;
- `versionedName: "Linux95 4.2"`;
- `shortVersionedName: "Linux95 4.2"`;
- `bootloaderEntryName: Linux95`;
- `welcomeStyleCalamares: false`;
- `windowExpanding: normal`;
- `windowSize: 800px,520px`;
- `navigation: widget`;
- `sidebar: widget`;
- the hook targets `/etc/calamares/settings.conf`;
- the hook requires exactly one active `branding: debian` line before replacement;
- the hook replaces it with `branding: linux95`;
- the hook exits non-zero if the expected Debian branding line is absent;
- the hook contains no edits to module sequence, partition, bootloader, users, unpackfs, mount, or package configuration.

- [ ] **Step 2: Run checks to verify RED**

Run:

```bash
python3 tests/installer_source_checks.py
```

Expected: FAIL because the Linux95 branding component and hook do not exist.

- [ ] **Step 3: Create `branding.desc`**

Use the Calamares branding schema with these exact values:
- `componentName: linux95`
- `welcomeStyleCalamares: false`
- `welcomeExpandingLogo: true`
- `windowExpanding: normal`
- `windowSize: 800px,520px`
- `windowPlacement: center`
- `sidebar: widget`
- `navigation: widget`
- strings from Global Constraints
- empty external URLs unless a Linux95 project URL already exists in the repository and is deliberately selected during implementation
- `slideshow: false` for this milestone so technical output is not replaced by an untested QML slideshow.

Do not add or change Calamares module configuration in this task.

- [ ] **Step 4: Create the build-time branding-selector hook**

Create executable `config/hooks/live/0910-linux95-calamares-branding.hook.chroot` that:
1. uses `set -eu`;
2. fails if `/etc/calamares/settings.conf` does not exist;
3. counts active lines matching `^[[:space:]]*branding:[[:space:]]*debian[[:space:]]*$`;
4. requires the count to equal `1`;
5. replaces that one line with `branding: linux95`;
6. verifies exactly one active `branding: linux95` line exists afterward.

Do not touch any other Calamares setting.

- [ ] **Step 5: Run Task 2 GREEN**

Run:

```bash
python3 tests/installer_source_checks.py
sh -n config/hooks/live/0910-linux95-calamares-branding.hook.chroot
```

Expected: PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add \
  tests/installer_source_checks.py \
  config/includes.chroot/etc/calamares/branding/linux95/branding.desc \
  config/hooks/live/0910-linux95-calamares-branding.hook.chroot
git commit -m "Add Linux95 Calamares branding"
```

### Task 3: Add Linux95 installer artwork without duplicating the desktop theme

**Files:**
- Create: `config/includes.chroot/etc/calamares/branding/linux95/linux95-installer.svg`
- Create: `config/includes.chroot/usr/share/pixmaps/linux95-installer.svg`
- Modify: `config/includes.chroot/etc/calamares/branding/linux95/branding.desc`
- Modify: `tests/installer_source_checks.py`

**Interfaces:**
- Consumes: existing Linux95 visual language and the existing wallpaper assets under `config/includes.chroot/usr/share/backgrounds/linux95/`.
- Produces: one small project-owned SVG reused as Calamares `productIcon`, `productLogo`, and desktop launcher icon.

- [ ] **Step 1: Extend tests for installer artwork**

Add assertions that:
- both SVG paths exist;
- both contain an SVG root;
- neither references an external network resource;
- `branding.desc` sets:
  - `productIcon: "linux95-installer.svg"`
  - `productLogo: "linux95-installer.svg"`
- the desktop icon file exists at `/usr/share/pixmaps/linux95-installer.svg` in the live-build tree.

- [ ] **Step 2: Run checks to verify RED**

Run:

```bash
python3 tests/installer_source_checks.py
```

Expected: FAIL because the artwork files are absent.

- [ ] **Step 3: Add the minimal SVG asset**

Create a simple square Linux95 installer mark that:
- uses only vector shapes/text;
- contains no Windows logo or Microsoft marks;
- contains the text `Linux95` or a simple `L95` mark;
- remains legible at 16x16;
- has no external font, image, or network dependency.

Copy the same SVG content to both required paths rather than introducing two different designs.

- [ ] **Step 4: Wire the branding images**

In `branding.desc`, add:

```yaml
images:
  productIcon: "linux95-installer.svg"
  productLogo: "linux95-installer.svg"
```

Do not add a slideshow in this milestone.

- [ ] **Step 5: Run Task 3 GREEN**

Run:

```bash
python3 tests/installer_source_checks.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add \
  tests/installer_source_checks.py \
  config/includes.chroot/etc/calamares/branding/linux95/branding.desc \
  config/includes.chroot/etc/calamares/branding/linux95/linux95-installer.svg \
  config/includes.chroot/usr/share/pixmaps/linux95-installer.svg
git commit -m "Add Linux95 installer artwork"
```

### Task 4: Build the ISO and prove installer behavior in a disposable VM

**Files:**
- Modify if needed only for test automation: `tests/installer_source_checks.py`
- Create: `docs/testing/linux95-installer-smoke.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: reproducible acceptance evidence for the live ISO and installed system.

- [ ] **Step 1: Run the complete static gate**

Run:

```bash
python3 tests/installer_source_checks.py
git diff --check
```

Expected: PASS.

- [ ] **Step 2: Build the Linux95 ISO with the repository's existing live-build command**

Use the same documented/local build command already used for Linux95 releases. Do not introduce a second build system.

Expected:
- build exits `0`;
- generated ISO exists;
- build log contains no Calamares configuration error;
- live-build hook `0910-linux95-calamares-branding.hook.chroot` completes successfully.

- [ ] **Step 3: Inspect the built filesystem or booted live system**

Verify in the built/live environment:

```bash
grep -E '^[[:space:]]*branding:' /etc/calamares/settings.conf
test -x /usr/bin/linux95-installer
test -x /usr/bin/calamares-install-debian
test -f /etc/calamares/branding/linux95/branding.desc
```

Expected:
- only `branding: linux95`;
- all tests exit `0`.

- [ ] **Step 4: Perform the live ISO smoke test**

In a disposable VM:
- boot Linux95 ISO;
- confirm the Linux95 desktop loads;
- click **Install Linux95**;
- confirm the installer launches;
- confirm visible product identity says Linux95 rather than Debian;
- visit Welcome, Location, Keyboard, Partitions, Users, Summary;
- stop before destructive installation on the first smoke run.

Record results in `docs/testing/linux95-installer-smoke.md`.

- [ ] **Step 5: Perform a full disposable-disk install**

With a fresh empty virtual disk:
- boot the ISO;
- complete install;
- reboot;
- detach the ISO;
- boot the installed disk;
- confirm Linux95 desktop loads;
- confirm terminal, file manager, networking, and `apt` are usable;
- record firmware mode used.

If available, repeat with the other firmware mode (BIOS or UEFI). If only one is available in the current VM setup, record the untested mode explicitly rather than claiming it passed.

- [ ] **Step 6: Record exact acceptance evidence**

In `docs/testing/linux95-installer-smoke.md` record:
- ISO filename;
- SHA-256;
- VM firmware mode(s);
- disk size;
- install result;
- reboot result;
- visible installer name;
- `grep branding` result;
- any warnings or known limitations.

- [ ] **Step 7: Final regression check**

Run:

```bash
python3 tests/installer_source_checks.py
git diff --check
git status --short
```

Expected:
- source checks PASS;
- no whitespace errors;
- only intended milestone files are modified/untracked before final commit.

- [ ] **Step 8: Commit Task 4**

```bash
git add \
  tests/installer_source_checks.py \
  docs/testing/linux95-installer-smoke.md
git commit -m "Verify Linux95 installer branding"
```

## Self-Review

- Spec coverage: launcher identity, Linux95 branding, project-owned icon, build-time selection, no installer-engine fork, live smoke test, and full install/reboot acceptance are covered.
- Step scan: each implementation step changes one focused unit and each verification command has an explicit pass condition.
- Interface consistency: Tasks 2–4 consume `/usr/bin/linux95-installer` and branding component `linux95` exactly as defined in Task 1/2.
- Review Focus: stale Debian settings formatting, missing Debian helper, accidental installer-engine duplication, module-sequence drift, and real installed-disk boot are each pinned to a task.
- Proportion: four task boundaries correspond to launcher, branding, artwork, and acceptance; no extra installer functionality is introduced.
