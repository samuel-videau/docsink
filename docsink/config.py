import os
import json
from datetime import datetime

CONFIG_FILE = 'docsink_config.json'

DEFAULT_CONFIG = {
    "last_update": datetime.min.isoformat(),
    "docs_folder": "docs",
    "readme_file": "README.md"
}

def load_config():
    """
    Load the configuration from the JSON file.
    If the file doesn't exist, create it with default values.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Ensure all default keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
    else:
        config = DEFAULT_CONFIG.copy()
        save_config(config)
    return config

def save_config(config):
    """Save the configuration to the JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_last_update_time(config):
    """Get the last update time from the config."""
    return datetime.fromisoformat(config['last_update'])

def set_last_update_time(config, time):
    """Set the last update time in the config and save it."""
    config['last_update'] = time.isoformat()
    save_config(config)

def update_config(key, value):
    """Update a specific configuration value and save the config."""
    config = load_config()
    config[key] = value
    save_config(config)

def get_config_value(key):
    """Get a specific configuration value."""
    config = load_config()
    return config.get(key, DEFAULT_CONFIG.get(key))

if __name__ == "__main__":
    # This block allows you to test the config functions
    config = load_config()
    print("Current configuration:")
    print(json.dumps(config, indent=2))

    # Example of updating a config value
    update_config("docs_folder", "new_docs")
    print("\nUpdated docs_folder:")
    print(get_config_value("docs_folder"))

    # Example of setting last update time
    set_last_update_time(config, datetime.now())
    print("\nNew last update time:")
    print(get_last_update_time(config))