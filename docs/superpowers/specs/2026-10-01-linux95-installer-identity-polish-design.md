# Linux95 Installer Identity and Polish Design

**Date:** 2026-10-01

## Goal

Make the existing Linux95 graphical installer present itself consistently as **Linux95 Installer** while preserving Debian 13 and Calamares as the proven installation engine underneath.

The milestone is successful when a user can boot the Linux95 live ISO, launch **Install Linux95**, complete an installation, reboot, and reach the installed Linux95 system without seeing Debian-branded installer identity in the normal installation flow.

## Current State

Linux95 is a Debian 13 (Trixie) based live distribution using IceWM, PCManFM, custom Linux95 styling, a dedicated Linux95 desktop session, and Calamares.

The current installer package list includes both `calamares` and `calamares-settings-debian`.

The current desktop launcher is already named **Install Linux95**, but executes:

`/usr/bin/calamares-install-debian`

and uses the icon:

`install-debian`

This means the visible desktop entry is Linux95-branded while the launched Calamares environment still inherits Debian installer identity.

## Architecture

Keep the upstream Debian Calamares package and installer logic intact. Linux95 will add a thin project-owned branding and launch layer inside the live filesystem.

The Linux95 layer will be responsible only for product identity, artwork, launcher behavior, and presentation-level Calamares configuration. It must not fork or rewrite Calamares partitioning, filesystem creation, user creation, bootloader installation, or other installation engine logic.

Where Debian's Calamares settings provide required functional configuration, Linux95 may consume or copy the required settings during the ISO build, but the runtime launcher must be Linux95-owned and the visible installer identity must be Linux95.

## User Experience

The normal installation flow should present:

- Desktop entry: **Install Linux95**
- Installer window/product name: **Linux95 Installer**
- Linux95 icon and artwork instead of Debian installer artwork where configurable
- Linux95 naming on welcome, summary, progress, and finish screens where branding configuration supports it
- A clean installation progress view
- Detailed technical logs hidden by default when Calamares supports that behavior, while remaining accessible for troubleshooting
- Existing partitioning, user creation, locale, keyboard, bootloader, and filesystem behavior unchanged

The design should remain lightweight and visually consistent with the Linux95 retro desktop.

## Files and Responsibilities

The implementation should prefer focused project-owned files under the existing live-build tree.

Expected ownership boundaries:

- `config/includes.chroot/etc/skel/Desktop/Install Linux95.desktop`
  - Launches the Linux95 installer wrapper.
  - Uses a Linux95-owned installer icon.

- `config/includes.chroot/usr/bin/linux95-installer`
  - Linux95-owned entry point.
  - Starts Calamares with the Linux95 configuration/branding location.
  - Contains no partitioning or installation logic.

- `config/includes.chroot/etc/calamares/`
  - Linux95 Calamares configuration overrides only where required.
  - Keeps module behavior compatible with the Debian-provided Calamares setup.

- `config/includes.chroot/etc/calamares/branding/linux95/`
  - Linux95 product name, version strings, artwork references, and style configuration.

- `config/includes.chroot/usr/share/icons/...` or another existing project asset location
  - Linux95 installer icon/artwork used by the desktop entry and branding.

- `config/package-lists/linux95-installer.list.chroot`
  - Continues to install the runtime packages required for Calamares and BIOS/UEFI installation.
  - Debian settings may remain as a functional dependency if Linux95 overlays only presentation configuration.

- A new lightweight validation script/test area
  - Verifies the built source tree has Linux95 launcher/branding and does not regress to the Debian wrapper in the desktop entry.

Exact paths may be adjusted during implementation only when required by the installed Calamares version; any adjustment must preserve these responsibility boundaries.

## Functional Requirements

1. The desktop launcher must not directly execute `calamares-install-debian`.
2. The desktop launcher must execute the Linux95-owned wrapper.
3. The normal installer window/product identity must be **Linux95 Installer**.
4. Normal installer artwork/iconography must be Linux95-owned where Calamares exposes branding hooks.
5. Debian/Calamares remains the installation engine underneath.
6. Existing partitioning behavior must not be reimplemented.
7. Existing BIOS installation support must continue to work.
8. Existing UEFI installation support must continue to work.
9. Live mode must continue to work before installation.
10. The installed Linux95 system must boot after a successful install.
11. The installer must remain usable without network access once the ISO has booted, except for features that already inherently require the network.
12. A failure to load optional Linux95 artwork must not silently change installer execution to a different installer engine.
13. Technical installer output should not dominate the default progress UI when the installed Calamares version provides a supported configuration for hiding it.

## Non-Goals

This milestone does not:

- fork Calamares;
- replace Calamares with a custom installer;
- redesign disk partitioning;
- add new filesystems;
- modify GRUB behavior beyond what is needed to preserve existing BIOS/UEFI installation;
- modify the experimental from-scratch Linux95 kernel;
- remove Debian as Linux95's distribution base;
- rewrite the Linux95 desktop.

## Safety and Compatibility Constraints

- Preserve Debian 13 (Trixie) as the distribution base.
- Preserve the existing IceWM Linux95 live session.
- Preserve current package-management behavior through APT.
- Keep the installer usable in a VM and on physical BIOS/UEFI targets supported by the existing build.
- Do not overwrite Debian package-owned files at runtime when the same result can be achieved with project-owned build-time overlays.
- Keep Linux95-specific customization under project-controlled paths so package upgrades are easier to reason about.
- Do not claim that Linux95 owns or authored upstream Debian, Calamares, GRUB, or Linux components.

## Verification

The milestone requires three levels of verification.

### Static build-tree checks

Verify that:

- the desktop entry launches `linux95-installer`;
- the desktop entry no longer names the Debian installer icon;
- the Linux95 wrapper exists and is executable in the built filesystem;
- Linux95 Calamares branding declares the Linux95 product identity;
- required installer packages remain present;
- no project-owned launcher reimplements partitioning or installation engine logic.

### Live ISO smoke test

Boot the resulting ISO and verify:

- Linux95 desktop starts;
- **Install Linux95** launches successfully;
- the installer presents Linux95 identity;
- core pages open without configuration errors;
- the install can proceed through partition selection and summary.

### Full install acceptance test

In a disposable VM:

1. Boot the Linux95 ISO.
2. Install to an empty virtual disk.
3. Complete the installer.
4. Power off or reboot.
5. Remove/detach the live ISO.
6. Boot from the installed disk.
7. Verify the Linux95 desktop loads.
8. Verify the installed system reports the expected Debian/Linux95 base and retains networking, file manager, terminal, and package-management functionality.

## Completion Criteria

This milestone is complete only when:

- Linux95 branding is visible throughout the normal installer identity;
- the desktop entry no longer directly invokes Debian's installer wrapper;
- no installer-engine rewrite was introduced;
- the source validation checks pass;
- a live ISO smoke test passes;
- a clean VM installation boots successfully from the installed disk.
