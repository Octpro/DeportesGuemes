"""
Modern styling configuration for Deportes Güemes desktop application
Provides consistent colors, fonts, and styling across the application
"""

import customtkinter as ctk

class ModernStyles:
    """Modern styling configuration class"""
    
    def __init__(self):
        # Color palette - Modern and consistent with web design
        self.colors = {
            # Primary colors
            'primary': '#2563eb',      # Modern blue
            'primary_hover': '#1d4ed8', # Darker blue for hover
            'primary_light': '#3b82f6', # Lighter blue
            
            # Secondary colors
            'secondary': '#64748b',     # Slate gray
            'secondary_hover': '#475569', # Darker slate
            'secondary_light': '#94a3b8', # Lighter slate
            
            # Accent colors
            'accent': '#10b981',        # Emerald green
            'accent_hover': '#059669',  # Darker emerald
            'warning': '#f59e0b',       # Amber
            'error': '#ef4444',         # Red
            'success': '#10b981',       # Emerald
            
            # Neutral colors
            'background': '#f8fafc',    # Very light gray
            'surface': '#ffffff',       # White
            'surface_dark': '#1e293b',  # Dark slate
            'text_primary': '#0f172a',  # Very dark slate
            'text_secondary': '#64748b', # Medium slate
            'text_light': '#94a3b8',    # Light slate
            'border': '#e2e8f0',       # Light border
            'border_dark': '#334155',   # Dark border
        }
        
        # Typography
        self.fonts = {
            'heading_large': ('Segoe UI', 24, 'bold'),
            'heading_medium': ('Segoe UI', 20, 'bold'),
            'heading_small': ('Segoe UI', 16, 'bold'),
            'body_large': ('Segoe UI', 14, 'normal'),
            'body_medium': ('Segoe UI', 12, 'normal'),
            'body_small': ('Segoe UI', 10, 'normal'),
            'button': ('Segoe UI', 12, 'bold'),
            'caption': ('Segoe UI', 10, 'normal'),
        }
        
        # Spacing
        self.spacing = {
            'xs': 4,
            'sm': 8,
            'md': 16,
            'lg': 24,
            'xl': 32,
            'xxl': 48,
        }
        
        # Border radius
        self.radius = {
            'sm': 4,
            'md': 8,
            'lg': 12,
            'xl': 16,
        }
        
        # Shadows (for future use with custom widgets)
        self.shadows = {
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        }
        
        # Responsive breakpoints
        self.breakpoints = {
            'xs': 480,   # Extra small screens
            'sm': 768,   # Small screens
            'md': 1024,  # Medium screens
            'lg': 1280,  # Large screens
            'xl': 1920,  # Extra large screens
        }
        
        # Grid system
        self.grid = {
            'columns': 12,
            'gutter': self.spacing['md'],
        }
    
    def configure_theme(self, appearance_mode="dark"):
        """Configure CustomTkinter theme with modern colors"""
        ctk.set_appearance_mode(appearance_mode)
        
        # Set custom color theme
        if appearance_mode == "dark":
            ctk.set_default_color_theme("dark-blue")
        else:
            ctk.set_default_color_theme("blue")
    
    def get_button_style(self, variant="primary", size="medium"):
        """Get button styling configuration"""
        styles = {
            'primary': {
                'fg_color': self.colors['primary'],
                'hover_color': self.colors['primary_hover'],
                'text_color': 'white',
                'border_width': 0,
            },
            'secondary': {
                'fg_color': self.colors['secondary'],
                'hover_color': self.colors['secondary_hover'],
                'text_color': 'white',
                'border_width': 0,
            },
            'success': {
                'fg_color': self.colors['success'],
                'hover_color': self.colors['accent_hover'],
                'text_color': 'white',
                'border_width': 0,
            },
            'warning': {
                'fg_color': self.colors['warning'],
                'hover_color': '#d97706',
                'text_color': 'white',
                'border_width': 0,
            },
            'error': {
                'fg_color': self.colors['error'],
                'hover_color': '#dc2626',
                'text_color': 'white',
                'border_width': 0,
            },
            'outline': {
                'fg_color': 'transparent',
                'hover_color': self.colors['background'],
                'text_color': self.colors['primary'],
                'border_width': 2,
                'border_color': self.colors['primary'],
            }
        }
        
        sizes = {
            'small': {
                'height': 32,
                'font': self.fonts['body_small'],
                'corner_radius': self.radius['sm'],
            },
            'medium': {
                'height': 40,
                'font': self.fonts['button'],
                'corner_radius': self.radius['md'],
            },
            'large': {
                'height': 48,
                'font': self.fonts['body_large'],
                'corner_radius': self.radius['lg'],
            }
        }
        
        style = styles.get(variant, styles['primary'])
        size_config = sizes.get(size, sizes['medium'])
        
        return {**style, **size_config}
    
    def get_frame_style(self, variant="default"):
        """Get frame styling configuration"""
        styles = {
            'default': {
                'corner_radius': self.radius['md'],
                'border_width': 1,
            },
            'card': {
                'corner_radius': self.radius['lg'],
                'border_width': 0,
            },
            'panel': {
                'corner_radius': self.radius['sm'],
                'border_width': 1,
            }
        }
        
        return styles.get(variant, styles['default'])
    
    def get_entry_style(self):
        """Get entry/input styling configuration"""
        return {
            'height': 40,
            'corner_radius': self.radius['md'],
            'border_width': 1,
            'font': self.fonts['body_medium'],
        }
    
    def get_label_style(self, variant="body"):
        """Get label styling configuration"""
        styles = {
            'heading': {
                'font': self.fonts['heading_medium'],
            },
            'subheading': {
                'font': self.fonts['heading_small'],
            },
            'body': {
                'font': self.fonts['body_medium'],
            },
            'caption': {
                'font': self.fonts['caption'],
            }
        }
        
        return styles.get(variant, styles['body'])
    
    def get_responsive_columns(self, window_width):
        """Get number of columns based on window width"""
        if window_width < self.breakpoints['sm']:
            return 1  # Mobile: 1 column
        elif window_width < self.breakpoints['md']:
            return 2  # Tablet: 2 columns
        elif window_width < self.breakpoints['lg']:
            return 3  # Desktop: 3 columns
        elif window_width < self.breakpoints['xl']:
            return 4  # Large desktop: 4 columns
        else:
            return 5  # Extra large: 5 columns
    
    def get_responsive_padding(self, window_width):
        """Get responsive padding based on window width"""
        if window_width < self.breakpoints['sm']:
            return self.spacing['sm']  # Small padding on mobile
        elif window_width < self.breakpoints['md']:
            return self.spacing['md']  # Medium padding on tablet
        else:
            return self.spacing['lg']  # Large padding on desktop
    
    def get_responsive_font_size(self, base_variant, window_width):
        """Get responsive font size based on window width"""
        size_adjustments = {
            'xs': -2,
            'sm': -1,
            'md': 0,
            'lg': 1,
            'xl': 2
        }
        
        # Determine current breakpoint
        current_breakpoint = 'xl'
        for breakpoint, width in self.breakpoints.items():
            if window_width < width:
                current_breakpoint = breakpoint
                break
        
        # Get base font
        base_font = self.fonts.get(base_variant, self.fonts['body_medium'])
        font_family, base_size, weight = base_font
        
        # Adjust size
        adjustment = size_adjustments.get(current_breakpoint, 0)
        new_size = max(8, base_size + adjustment)  # Minimum size of 8
        
        return (font_family, new_size, weight)
    
    def is_mobile_size(self, window_width):
        """Check if window is mobile size"""
        return window_width < self.breakpoints['sm']
    
    def is_tablet_size(self, window_width):
        """Check if window is tablet size"""
        return self.breakpoints['sm'] <= window_width < self.breakpoints['md']
    
    def is_desktop_size(self, window_width):
        """Check if window is desktop size"""
        return window_width >= self.breakpoints['md']

# Global instance
modern_styles = ModernStyles()