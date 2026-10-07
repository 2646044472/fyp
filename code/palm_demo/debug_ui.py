#!/usr/bin/env python3
"""Compatibility entry point for the Pi camera web service."""
import sys
from palm_app import debug_ui as application

if __name__ == "__main__":
    raise SystemExit(application.main())
else:
    sys.modules[__name__] = application
