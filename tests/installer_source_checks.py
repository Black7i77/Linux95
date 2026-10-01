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

branding = root / "config/includes.chroot/etc/calamares/branding/linux95/branding.desc"
hook = root / "config/hooks/live/0910-linux95-calamares-branding.hook.chroot"

require(
    branding.exists(),
    "Linux95 Calamares branding.desc is missing",
)

branding_text = branding.read_text()

for expected in (
    "componentName: linux95",
    "productName: Linux95",
    "shortProductName: Linux95",
    'version: "4.2"',
    'shortVersion: "4.2"',
    'versionedName: "Linux95 4.2"',
    'shortVersionedName: "Linux95 4.2"',
    "bootloaderEntryName: Linux95",
    "welcomeStyleCalamares: false",
    "windowExpanding: normal",
    "windowSize: 800px,520px",
    "navigation: widget",
    "sidebar: widget",
):
    require(
        expected in branding_text,
        f"branding.desc missing: {expected}",
    )

require(
    hook.exists(),
    "Linux95 Calamares branding hook is missing",
)

hook_text = hook.read_text()

require(
    "/etc/calamares/settings.conf" in hook_text,
    "branding hook must target settings.conf",
)
require(
    "branding: debian" in hook_text,
    "branding hook must expect Debian branding",
)
require(
    "branding: linux95" in hook_text,
    "branding hook must select Linux95 branding",
)

for forbidden in (
    "partition",
    "bootloader",
    "unpackfs",
    "mkfs",
    "grub-install",
):
    require(
        forbidden not in hook_text,
        f"branding hook must not modify installer engine behavior: {forbidden}",
    )

require(
    "grep -Ec" in hook_text,
    "branding hook must count matching branding lines",
)
require(
    '"$count" -ne 1' in hook_text,
    "branding hook must require exactly one Debian branding line",
)
require(
    "sed -i -E" in hook_text,
    "branding hook must use one targeted branding replacement",
)
require(
    "branding:[[:space:]]*debian" in hook_text,
    "branding hook must specifically match Debian branding",
)
require(
    "branding: linux95" in hook_text,
    "branding hook must replace Debian branding with Linux95 branding",
)
