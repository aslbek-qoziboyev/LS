# LS-Linux Tools

LS is a lightweight desktop utility for Linux laptops, focused initially on touchpad gesture configuration.

## Current scope
- Detect touchpads where possible, with manual device selection.
- Toggle two-finger window switching.
- Toggle three-finger downward gesture (minimize/show desktop, to avoid forcibly closing unsaved work).
- Toggle four-finger workspace switching.
- Toggle pinch-to-zoom in and out.
- Toggle two-finger rotation to cycle display orientations.

## Build a Debian package
On Debian/Kali/Ubuntu, install the build tools and run:

```bash
sudo apt update
sudo apt install -y dpkg-dev debhelper python3-gi gir1.2-gtk-3.0
dpkg-buildpackage -us -uc -b
```

The `.deb` is created in the parent directory. A GitHub Actions workflow also builds the package on pushes and can publish it as a workflow artifact.

## Runtime notes
- Designed for X11 sessions first, using Touchégg for multi-touch gesture recognition and XRandR for display rotation. Wayland support depends on the desktop compositor and is not guaranteed.
- Gesture support depends on the touchpad hardware, Touchégg version, desktop environment, and available display modes.
- “Three-finger downward gesture” minimizes/shows the desktop rather than force-closing every application, protecting unsaved work.
- Display aspect ratios can only be switched if the display exposes compatible modes. Rotation behavior differs between drivers and monitors.

## Install
```bash
sudo apt install ./ls-linux-tools_0.1.0_all.deb
```

## License
MIT