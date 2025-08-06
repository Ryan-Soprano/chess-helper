"""
Configuration system for Chess Helper
"""
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ChessConfig:
    """Configuration settings for Chess Helper."""
    
    # Engine settings
    engine_depth: int = 15
    engine_time: float = 1.0
    engine_skill_level: int = 20
    auto_analysis: bool = True
    
    # Interface settings
    board_coordinates: bool = True
    move_history_notation: str = "san"  # "san" or "uci"
    sound_enabled: bool = False
    
    # Game settings  
    auto_save: bool = True
    auto_save_interval: int = 10  # moves
    pgn_export_path: str = "./saved_games/"
    
    # Display settings
    piece_style: str = "unicode"  # "unicode" or "letters"
    board_colors: Dict[str, str] = None
    gui_theme: str = "default"
    
    # Advanced settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.board_colors is None:
            self.board_colors = {
                "light": "#F0D9B5",
                "dark": "#B58863",
                "selected": "#FFFF99",
                "legal_move": "#90EE90"
            }

class ConfigManager:
    """Manages configuration for Chess Helper."""
    
    CONFIG_FILE = "chess_helper_config.json"
    
    def __init__(self):
        self.config = ChessConfig()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    
                # Update config with loaded data
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                        
                print(f"Configuration loaded from {self.CONFIG_FILE}")
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default settings.")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.CONFIG_FILE) if os.path.dirname(self.CONFIG_FILE) else ".", exist_ok=True)
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
                
            print(f"Configuration saved to {self.CONFIG_FILE}")
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
        else:
            raise KeyError(f"Configuration key '{key}' not found")
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = ChessConfig()
        self.save_config()
        print("Configuration reset to defaults")
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("\nCurrent Configuration:")
        print("-" * 30)
        
        config_dict = asdict(self.config)
        for key, value in config_dict.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")

# Usage example for your main files:
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager."""
    if not hasattr(get_config_manager, '_instance'):
        get_config_manager._instance = ConfigManager()
    return get_config_manager._instance

# Example integration in your CLI interface:
def add_config_commands_to_cli(cli_interface):
    """Add configuration commands to CLI interface."""
    
    def show_config():
        """Show current configuration."""
        config_manager = get_config_manager()
        config_manager.print_config()
    
    def set_config_value(key: str, value: str):
        """Set a configuration value."""
        config_manager = get_config_manager()
        
        # Convert string values to appropriate types
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        try:
            config_manager.set(key, value)
            print(f"✅ Set {key} = {value}")
        except KeyError as e:
            print(f"❌ {e}")
    
    def reset_config():
        """Reset configuration to defaults."""
        config_manager = get_config_manager()
        confirm = input("Reset all settings to defaults? (yes/no): ").strip().lower()
        if confirm == 'yes':
            config_manager.reset_to_defaults()
            print("✅ Configuration reset to defaults")
        else:
            print("Reset cancelled")
    
    # Add to your CLI interface help text:
    additional_help = """
Configuration Commands:
  config          - Show current settings
  set [key] [val] - Change a setting (e.g., set engine_depth 20)
  reset_config    - Reset all settings to defaults
    """
    
    return {
        'config': show_config,
        'set': lambda args: set_config_value(args[0], args[1]) if len(args) >= 2 else print("Usage: set <key> <value>"),
        'reset_config': reset_config
    }

# Auto-save functionality
class AutoSave:
    """Handles automatic game saving."""
    
    def __init__(self, game_tracker, config_manager):
        self.game_tracker = game_tracker
        self.config = config_manager
        self.last_save_move_count = 0
    
    def check_auto_save(self) -> None:
        """Check if auto-save should be triggered."""
        if not self.config.get('auto_save', True):
            return
        
        current_move_count = len(self.game_tracker.move_history)
        interval = self.config.get('auto_save_interval', 10)
        
        if current_move_count > 0 and current_move_count % interval == 0:
            if current_move_count != self.last_save_move_count:
                self._perform_auto_save()
                self.last_save_move_count = current_move_count
    
    def _perform_auto_save(self) -> None:
        """Perform automatic save."""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = self.config.get('pgn_export_path', './saved_games/')
            
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.join(save_dir, f"autosave_{timestamp}.pgn")
            
            self.game_tracker.export_pgn(filename)
            print(f"🔄 Auto-saved game to {filename}")
            
        except Exception as e:
            print(f"⚠️  Auto-save failed: {e}")