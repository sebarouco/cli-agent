"""
Tests for accessibility configuration.
"""

import os
import sys
import pytest
from pieces.accessibility.config import AccessibilityConfig, ColorScheme


class TestAccessibilityConfig:
    """Test accessibility configuration detection and management."""
    
    def test_default_config(self):
        """Test default accessibility configuration."""
        # Ensure no environment variables interfere
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        if 'NO_COLOR' in os.environ:
            del os.environ['NO_COLOR']
        if 'PIECES_COLOR_SCHEME' in os.environ:
            del os.environ['PIECES_COLOR_SCHEME']
        
        try:
            config = AccessibilityConfig()
            assert config.color_scheme == ColorScheme.DEFAULT
            assert config.no_color is False
            assert config.high_contrast is False
            assert config.should_use_color is True
        finally:
            # Restore environment
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
    
    def test_no_color_detection(self):
        """Test NO_COLOR environment variable detection."""
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            assert config.no_color is True
            assert config.should_use_color is False
            assert config.color_scheme == ColorScheme.MONOCHROME
            
            # NO_COLOR should work with any value
            os.environ['NO_COLOR'] = 'any_value'
            config = AccessibilityConfig()
            assert config.no_color is True
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
    
    def test_color_scheme_env_variable(self):
        """Test PIECES_COLOR_SCHEME environment variable."""
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            
            os.environ['PIECES_COLOR_SCHEME'] = 'high_contrast'
            config = AccessibilityConfig()
            assert config.color_scheme == ColorScheme.HIGH_CONTRAST
            
            os.environ['PIECES_COLOR_SCHEME'] = 'monochrome'
            config = AccessibilityConfig()
            assert config.color_scheme == ColorScheme.MONOCHROME
            
            # Test invalid scheme (should fall back to default)
            os.environ['PIECES_COLOR_SCHEME'] = 'invalid_scheme'
            config = AccessibilityConfig()
            assert config.color_scheme == ColorScheme.DEFAULT
        finally:
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
    
    def test_no_color_overrides_color_scheme(self):
        """Test that NO_COLOR overrides PIECES_COLOR_SCHEME (NO_COLOR has highest priority)."""
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        try:
            os.environ['NO_COLOR'] = '1'
            os.environ['PIECES_COLOR_SCHEME'] = 'high_contrast'
            
            config = AccessibilityConfig()
            assert config.no_color is True
            assert config.color_scheme == ColorScheme.MONOCHROME  # NO_COLOR forces monochrome
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
    
    def test_accessible_color_mapping(self):
        """Test accessible color mapping for different schemes."""
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
            
            # Test default scheme
            config = AccessibilityConfig()
            assert config.get_accessible_color('success') == 'green'
            assert config.get_accessible_color('error') == 'red'
            assert config.get_accessible_color('warning') == 'yellow'
            
            # Test high contrast scheme
            os.environ['PIECES_COLOR_SCHEME'] = 'high_contrast'
            config = AccessibilityConfig()
            assert config.get_accessible_color('success') == 'bright_white'
            assert config.get_accessible_color('error') == 'bright_yellow'
            
            # Test monochrome scheme
            os.environ['PIECES_COLOR_SCHEME'] = 'monochrome'
            config = AccessibilityConfig()
            assert config.get_accessible_color('success') == 'bold'
            assert config.get_accessible_color('error') == 'bold'
            
            # Test with NO_COLOR
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            assert config.get_accessible_color('success') is None
            assert config.get_accessible_color('error') is None
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
    
    def test_text_indicators(self):
        """Test text-based indicators for semantic colors."""
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
            
            # Test with colors enabled (no indicators)
            config = AccessibilityConfig()
            assert config.get_text_indicator('success') == ''
            assert config.get_text_indicator('error') == ''
            
            # Test with NO_COLOR (indicators added)
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            assert config.get_text_indicator('success') == '✓'
            assert config.get_text_indicator('error') == '✗'
            assert config.get_text_indicator('warning') == '⚠'
            assert config.get_text_indicator('info') == 'ℹ'
            
            # Test with monochrome scheme (indicators added)
            del os.environ['NO_COLOR']
            os.environ['PIECES_COLOR_SCHEME'] = 'monochrome'
            config = AccessibilityConfig()
            assert config.get_text_indicator('success') == '✓'
            assert config.get_text_indicator('error') == '✗'
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
    
    def test_colorblind_friendly_schemes(self):
        """Test colorblind-friendly color schemes."""
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
            
            # Test deuteranopia (red-green colorblind)
            os.environ['PIECES_COLOR_SCHEME'] = 'deuteranopia'
            config = AccessibilityConfig()
            success_color = config.get_accessible_color('success')
            error_color = config.get_accessible_color('error')
            # Should avoid red-green combinations
            assert success_color not in ['green', 'red']
            assert error_color not in ['green', 'red']
            
            # Test tritanopia (blue-yellow colorblind)
            os.environ['PIECES_COLOR_SCHEME'] = 'tritanopia'
            config = AccessibilityConfig()
            warning_color = config.get_accessible_color('warning')
            # Should avoid blue-yellow combinations
            assert warning_color not in ['yellow', 'blue', 'cyan']
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']