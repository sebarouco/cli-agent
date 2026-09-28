"""
Accessibility module for Pieces CLI.

This module provides accessibility features including:
- NO_COLOR support (https://no-color.org/)
- Color scheme detection
- Screen reader friendly output
- High contrast mode support
"""

from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.console import AccessibleConsole

__all__ = ['AccessibilityConfig', 'AccessibleConsole']
