#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]

wrapper = root / "config/includes.chroot/usr/bin/linux95-installer"
desktop = root / "config/includes.chroot/etc/skel/Desktop/Install Linux95.desktop"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


require(wrapper.exists(), "linux95-installer wrapper is missing")

wrapper_text = wrapper.read_text()

require(
    wrapper_text.startswith("#!/bin/sh"),
    "linux95-installer must use /bin/sh",
)
require(
    "/usr/bin/calamares-install-debian" in wrapper_text,
    "wrapper must use Debian Calamares helper",
)
require(
    'exec /usr/bin/calamares-install-debian "$@"' in wrapper_text,
    "wrapper must delegate arguments with exec",
)

require(
    '[ ! -x /usr/bin/calamares-install-debian ]' in wrapper_text,
    "wrapper must verify Debian Calamares helper is executable",
)
require(
    "Linux95 Installer: Debian Calamares helper not found" in wrapper_text,
    "wrapper must print a clear missing-helper error",
)
require(
    "exit 127" in wrapper_text,
    "wrapper must exit 127 when Debian helper is missing",
)

for forbidden in (
    "parted",
    "mkfs",
    "mount",
    "grub-install",
    "xhost",
    "pkexec",
    "/etc/fstab",
):
    require(
        forbidden not in wrapper_text,
        f"wrapper must not contain installer-engine logic: {forbidden}",
    )

require(desktop.exists(), "Install Linux95.desktop is missing")

desktop_text = desktop.read_text()

require(
    "Exec=/usr/bin/linux95-installer" in desktop_text,
    "desktop launcher must use linux95-installer",
)
require(
    "Exec=/usr/bin/calamares-install-debian" not in desktop_text,
    "desktop launcher must not directly use Debian wrapper",
)
require(
    "Icon=linux95-installer" in desktop_text,
    "desktop launcher must use Linux95 installer icon",
)
require(
    "Icon=install-debian" not in desktop_text,
    "desktop launcher must not use Debian installer icon",
)

print("installer source checks: PASS")
