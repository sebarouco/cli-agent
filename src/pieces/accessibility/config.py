"""
Accessibility configuration for Pieces CLI.

Handles detection of user accessibility preferences including:
- NO_COLOR environment variable support
- System color scheme detection
- High contrast mode detection
"""

import os
import sys
from enum import Enum
from typing import Optional


class ColorScheme(Enum):
    """Accessible color schemes following accessibility standards."""
    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    MONOCHROME = "monochrome"
    DEUTERANOPIA = "deuteranopia"  # Red-green colorblind
    PROTANOPIA = "protanopia"      # Red-green colorblind
    TRITANOPIA = "tritanopia"      # Blue-yellow colorblind


class AccessibilityConfig:
    """
    Manages accessibility configuration and preference detection.
    
    Follows standards from:
    - NO_COLOR: https://no-color.org/
    - WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
    """
    
    def __init__(self):
        self._color_scheme = self._detect_color_scheme()
        self._no_color = self._check_no_color()
        self._high_contrast = self._check_high_contrast()
        
    @property
    def color_scheme(self) -> ColorScheme:
        """Get the detected color scheme."""
        return self._color_scheme
    
    @property
    def no_color(self) -> bool:
        """Check if NO_COLOR is enabled."""
        return self._no_color
    
    @property
    def high_contrast(self) -> bool:
        """Check if high contrast mode is enabled."""
        return self._high_contrast
    
    @property
    def should_use_color(self) -> bool:
        """Determine if colors should be used based on preferences."""
        return not self._no_color
    
    def _detect_color_scheme(self) -> ColorScheme:
        """
        Detect user's preferred color scheme from environment and system settings.
        
        Priority order:
        1. NO_COLOR environment variable (forces monochrome - highest priority)
        2. PIECES_COLOR_SCHEME environment variable
        3. System high contrast mode
        4. Default
        """
        # Check NO_COLOR standard first (highest priority)
        if self._check_no_color():
            return ColorScheme.MONOCHROME
        
        # Check explicit environment variable
        env_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        if env_scheme:
            try:
                return ColorScheme(env_scheme.lower())
            except ValueError:
                pass  # Invalid scheme, continue detection
        
        # Check system high contrast
        if self._check_high_contrast():
            return ColorScheme.HIGH_CONTRAST
        
        return ColorScheme.DEFAULT
    
    def _check_no_color(self) -> bool:
        """
        Check for NO_COLOR environment variable.
        
        Following the standard from https://no-color.org/
        Command-line software which outputs colored text should check for the presence
        of this environment variable. When present (regardless of its value), the software
        should suppress color output.
        """
        return 'NO_COLOR' in os.environ
    
    def _check_high_contrast(self) -> bool:
        """
        Check if system high contrast mode is enabled.
        
        Currently supports Windows high contrast detection.
        Can be extended for other platforms.
        """
        if sys.platform == 'win32':
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Control Panel\Accessibility\HighContrast'
                )
                flags = winreg.QueryValueEx(key, 'Flags')[0]
                # HCF_HIGHCONTRASTON = 0x01
                if flags & 1:
                    return True
            except (OSError, ImportError):
                pass
        
        return False
    
    def get_accessible_color(self, semantic_color: str) -> Optional[str]:
        """
        Get accessible color mapping for semantic colors.
        
        Args:
            semantic_color: Semantic color name (success, error, warning, info, muted)
            
        Returns:
            Color string for the current scheme, or None if no color should be used
        """
        if not self.should_use_color:
            return None
        
        color_map = {
            ColorScheme.DEFAULT: {
                'success': 'green',
                'error': 'red',
                'warning': 'yellow',
                'info': 'blue',
                'muted': 'dim'
            },
            ColorScheme.HIGH_CONTRAST: {
                'success': 'bright_white',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_white',
                'muted': 'white'
            },
            ColorScheme.MONOCHROME: {
                # Use text decorations instead of colors
                'success': 'bold',
                'error': 'bold',
                'warning': 'underline',
                'info': 'default',
                'muted': 'dim'
            },
            ColorScheme.DEUTERANOPIA: {
                # Avoid red-green combinations for red-green colorblindness
                'success': 'blue',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_blue',
                'muted': 'dim'
            },
            ColorScheme.PROTANOPIA: {
                # Avoid red-green combinations for red-green colorblindness
                'success': 'blue',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_blue',
                'muted': 'dim'
            },
            ColorScheme.TRITANOPIA: {
                # Avoid blue-yellow combinations for blue-yellow colorblindness
                'success': 'green',
                'error': 'red',
                'warning': 'bright_magenta',
                'info': 'cyan',
                'muted': 'dim'
            }
        }
        
        scheme_colors = color_map.get(self._color_scheme, color_map[ColorScheme.DEFAULT])
        return scheme_colors.get(semantic_color)
    
    def get_text_indicator(self, semantic_color: str) -> str:
        """
        Get text-based indicators for semantic colors when color is not available.
        
        Args:
            semantic_color: Semantic color name
            
        Returns:
            Unicode character prefix for the semantic meaning
        """
        if self.should_use_color and self._color_scheme != ColorScheme.MONOCHROME:
            return ''
        
        indicators = {
            'success': '✓',
            'error': '✗',
            'warning': '⚠',
            'info': 'ℹ',
            'muted': ''
        }
        return indicators.get(semantic_color, '')