"""
Accessible console wrapper for Rich Console.

Provides accessibility-aware console output that respects:
- NO_COLOR environment variable
- Color scheme preferences
- Screen reader compatibility
"""

from typing import Any, Optional
from rich.console import Console
from rich.text import Text

from pieces.accessibility.config import AccessibilityConfig


class AccessibleConsole:
    """
    Accessible wrapper around Rich Console.
    
    Automatically applies accessibility preferences to all console output.
    """
    
    def __init__(self, config: Optional[AccessibilityConfig] = None, **console_kwargs):
        """
        Initialize accessible console.
        
        Args:
            config: AccessibilityConfig instance (creates default if None)
            **console_kwargs: Arguments to pass to Rich Console
        """
        self._config = config or AccessibilityConfig()
        
        # Force no colors if NO_COLOR is set
        if self._config.no_color:
            console_kwargs['no_color'] = True
        
        self._console = Console(**console_kwargs)
    
    @property
    def config(self) -> AccessibilityConfig:
        """Get the accessibility configuration."""
        return self._config
    
    @property
    def console(self) -> Console:
        """Get the underlying Rich Console."""
        return self._console
    
    def print(self, *args, **kwargs) -> None:
        """
        Print to console with accessibility-aware formatting.
        
        Automatically applies color scheme preferences and text indicators.
        """
        # Process args to add accessibility indicators
        processed_args = []
        for arg in args:
            processed_args.append(self._format_accessible(arg))
        
        self._console.print(*processed_args, **kwargs)
    
    def _format_accessible(self, content: Any) -> Any:
        """
        Format content for accessibility.
        
        Args:
            content: Content to format
            
        Returns:
            Formatted content with accessibility considerations
        """
        if isinstance(content, str):
            return self._format_string_accessible(content)
        elif isinstance(content, Text):
            return self._format_text_accessible(content)
        return content
    
    def _format_string_accessible(self, text: str) -> str:
        """
        Format string with accessibility indicators.
        
        Detects Rich markup patterns and adds text indicators when colors are disabled.
        """
        if not self._config.no_color:
            return text
        
        # Add text indicators for common Rich color patterns
        # [red]Error[/red] -> ✗ Error
        # [green]Success[/green] -> ✓ Success
        # [yellow]Warning[/yellow] -> ⚠ Warning
        
        import re
        
        # Pattern to match [color]text[/color]
        color_pattern = r'\[(red|green|yellow|blue|bright_red|bright_green|bright_yellow)\](.*?)\[/\1\]'
        
        def add_indicator(match):
            color = match.group(1)
            content = match.group(2)
            
            # Map Rich colors to semantic colors
            color_map = {
                'red': 'error',
                'green': 'success',
                'yellow': 'warning',
                'blue': 'info',
                'bright_red': 'error',
                'bright_green': 'success',
                'bright_yellow': 'warning'
            }
            
            semantic = color_map.get(color, 'info')
            indicator = self._config.get_text_indicator(semantic)
            
            if indicator:
                return f"{indicator} {content}"
            return content
        
        return re.sub(color_pattern, add_indicator, text, flags=re.IGNORECASE)
    
    def _format_text_accessible(self, text: Text) -> Text:
        """
        Format Rich Text object for accessibility.
        """
        if not self._config.no_color:
            return text
        
        # Remove styling when NO_COLOR is set
        accessible_text = Text(text.plain)
        return accessible_text
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate any other methods to the underlying Rich Console.
        """
        return getattr(self._console, name)
    
    def __enter__(self):
        """Context manager support."""
        return self._console.__enter__()
    
    def __exit__(self, *args):
        """Context manager support."""
        return self._console.__exit__(*args)