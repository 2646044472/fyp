# Archived palm demo utilities

The active application now has only the web entry point at
`code/palm_demo/debug_ui.py`.

This directory preserves the retired fixed-crop Fast-CC CLI, PalmBigData
preparation/calibration/evaluation tools, RAW capability probe, SSH shortcuts,
offline installer and Windows driver. They are not included in deployment ZIPs.

The CLI and dataset tools use the active application's dependencies and paths;
they are retained for reproducing historical comparisons. Run the CLI from the
repository root with `python archive/palm_demo_legacy/cli.py --help`.
The archived shell installers are historical snapshots, not maintained setup
instructions; their old relative layout assumptions no longer apply.
