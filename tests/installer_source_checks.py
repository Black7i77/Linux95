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
    'version: "4.3"',
    'shortVersion: "4.3"',
    'versionedName: "Linux95 4.3"',
    'shortVersionedName: "Linux95 4.3"',
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

branding_art = (
    root
    / "config/includes.chroot/etc/calamares/branding/linux95/linux95-installer.svg"
)

desktop_art = (
    root
    / "config/includes.chroot/usr/share/pixmaps/linux95-installer.svg"
)

require(
    branding_art.exists(),
    "Linux95 Calamares installer artwork is missing",
)

require(
    desktop_art.exists(),
    "Linux95 desktop installer icon is missing",
)

branding_art_text = branding_art.read_text()
desktop_art_text = desktop_art.read_text()

for name, text in (
    ("branding artwork", branding_art_text),
    ("desktop artwork", desktop_art_text),
):
    require(
        "<svg" in text,
        f"{name} must contain an SVG root",
    )
    lowered = text.lower()

    external_refs = (
        'href="http://',
        'href="https://',
        "href='http://",
        "href='https://",
        'xlink:href="http://',
        'xlink:href="https://',
        "xlink:href='http://",
        "xlink:href='https://",
        "url(http://",
        "url(https://",
    )

    require(
        not any(ref in lowered for ref in external_refs),
        f"{name} must not depend on external network resources",
    )

require(
    'productIcon: "linux95-installer.svg"' in branding_text,
    "branding.desc must use Linux95 installer productIcon",
)

require(
    'productLogo: "linux95-installer.svg"' in branding_text,
    "branding.desc must use Linux95 installer productLogo",
)

about = root / "config/includes.chroot/usr/local/bin/linux95-about"
system_info = root / "config/includes.chroot/usr/local/bin/linux95-system-info"
packages = root / "config/package-lists/linux95.list.chroot"
time_hook = root / "config/hooks/live/0920-linux95-time-sync.hook.chroot"

require(about.exists(), "Linux95 About script is missing")
about_text = about.read_text()

require(
    "Version: 4.3" in about_text,
    "About Linux95 must report version 4.3",
)
require(
    "Creator: Scott Pollock" in about_text,
    "About Linux95 must credit Scott Pollock as Creator",
)

require(system_info.exists(), "Linux95 System Info script is missing")
system_info_text = system_info.read_text()

require(
    "Linux95 4.3" in system_info_text,
    "System Info must report Linux95 4.3",
)
require(
    "Linux95 4.1" not in system_info_text,
    "System Info must not report the old 4.1 version",
)

require(packages.exists(), "Linux95 package list is missing")
packages_text = packages.read_text()

require(
    "systemd-timesyncd" in packages_text,
    "Linux95 must include systemd-timesyncd for automatic clock synchronization",
)

require(
    time_hook.exists(),
    "Linux95 time synchronization build hook is missing",
)

time_hook_text = time_hook.read_text()

require(
    "systemd-timesyncd.service" in time_hook_text,
    "time synchronization hook must enable systemd-timesyncd",
)

legacy_system_info = (
    root / "config/includes.chroot/etc/skel/Desktop/System-Info.desktop"
)
linux95_system_info_launcher = (
    root / "config/includes.chroot/etc/skel/Desktop/linux95-system-info.desktop"
)

require(
    not legacy_system_info.exists(),
    "old duplicate Fastfetch System Info desktop launcher must be removed",
)
require(
    linux95_system_info_launcher.exists(),
    "Linux95 System Info desktop launcher must remain",
)
require(
    "Exec=/usr/local/bin/linux95-system-info"
    in linux95_system_info_launcher.read_text(),
    "Linux95 System Info launcher must use the Linux95 system-info tool",
)
