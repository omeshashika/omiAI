#!/usr/bin/env python3
"""
Configuration script for omiAI bot.
This script helps users set up their configuration file based on example.cfg.
"""

import json
import os
from pathlib import Path


def get_user_input(prompt, default_value=None, input_type=str):
    """Get user input with optional default value."""
    if default_value:
        prompt += f" (default: {default_value})"
    
    user_input = input(prompt + ": ").strip()
    
    if not user_input and default_value is not None:
        return default_value
    
    if input_type == bool:
        return user_input.lower() in ['true', '1', 'yes', 'y', 'on']
    elif input_type == int:
        try:
            return int(user_input) if user_input else default_value
        except ValueError:
            print(f"Invalid input. Using default value: {default_value}")
            return default_value
    elif input_type == list:
        if user_input:
            # Split by comma and strip spaces
            return [item.strip() for item in user_input.split(',')]
        else:
            return default_value or []
    else:
        return user_input.strip() if user_input else default_value


def configure_models():
    """Configure AI models section."""
    print("\n--- Model Configuration ---")
    print("You can configure one or more AI models for the bot.")
    print("Press enter to skip a parameter and set it to default")
    
    models = []
    model_count = 0
    
    while True:
        model_count += 1
        print(f"\nConfiguring Model #{model_count}:")
        
        model_id = get_user_input(
            f"Enter model ID (e.g., qwen3:1.7b)",
            "gemma3n:e2b"
        )
        
        title = get_user_input(
            f"Enter model title (e.g., Qwen 3 {model_count}.0B)",
            model_id
        )
        
        api_url = get_user_input(
            "Enter API URL (or 'ollama' for local Ollama)",
            "ollama"
        )
        
        api_key = ""
        if api_url != "ollama":
            api_key = get_user_input("Enter API key (skip if using Ollama)")
        else:
            api_key = "-"
        
        model = {
            "id": model_id,
            "title": title,
            "apiurl": api_url,
            "apikey": api_key
        }
        
        models.append(model)
        
        add_another = get_user_input(
            "Add another model? (y/n)",
            "n",
            bool
        )
        
        if not add_another:
            break
    
    return models


def main():
    print("omiAI Bot Configuration Script")
    print("===============================")
    print("This script will help you create a configuration file for the omiAI bot.")
    print("Based on the example.cfg file, we'll guide you through the setup.\n")
    
    config = {}
    
    # Basic settings
    print("--- Basic Configuration ---")
    config["token"] = get_user_input("Enter your Discord bot token", "None")
    config["baseDir"] = get_user_input("Enter base directory for data", "omiAI_data")
    
    # Models configuration
    config["models"] = configure_models()
    
    # Default model selection
    model_ids = [model["id"] for model in config["models"]]
    default_model_prompt = f"Enter default model ID {model_ids}"
    if model_ids:
        config["defaultModel"] = get_user_input(default_model_prompt, model_ids[0])
    else:
        config["defaultModel"] = get_user_input("Enter default model ID", "qwen3:1.7b")
    
    # Fallback API settings
    print("\n--- Default API Configuration ---")
    config["defaultAPIurl"] = get_user_input(
        "Enter default API URL (used if not specified in models, skip if it's Ollama)",
        "ollama"
    )
    config["defaultAPIkey"] = get_user_input(
        "Enter default API key (leave empty if not needed)"
    )
    
    # Streaming and system settings
    print("\n--- Behavior Settings ---")
    config["doStreaming"] = get_user_input("Enable streaming responses? (y/n)", "true", bool)
    config["systemPromptFix"] = False
    
    # Discord settings
    print("\n--- Discord Configuration ---")
    config["discordAllowDM"] = get_user_input("Allow DMs? (y/n)", "true", bool)
    config["discordGuildLock"] = get_user_input("Restrict to specific guilds? (y/n)", "false", bool)
    
    if config["discordGuildLock"]:
        guild_list = get_user_input(
            "Enter allowed guild IDs separated by commas (e.g., 123456789,987654321)",
            input_type=list
        )
        config["discordAllowedGuilds"] = guild_list
    else:
        config["discordAllowedGuilds"] = []
    
    owner_id = get_user_input("Enter your Discord user ID", "")
    config["discordBotOwnerID"] = owner_id
    
    config["useStatusesInsteadOfModel"] = get_user_input(
        "Use custom statuses instead of showing model name? (y/n)",
        False,
        bool
    )
    
    if config["useStatusesInsteadOfModel"]:
        status_texts = get_user_input(
            "Enter status texts separated by commas",
            "thinking, ready to talk",
            list
        )
        config["discordStatuses"] = status_texts
    else:
        config["discordStatuses"] = []
    # Memory and performance settings
    print("\n--- Memory and Performance Settings ---")
    config["secondsBetweenMessageUpdates"] = get_user_input(
        "Seconds between message updates when streaming",
        1,
        int
    )
    config["numOfMessagesInMemory"] = get_user_input(
        "Number of messages to keep in context",
        40,
        int
    )
    config["experimentalCompressedMemory"] = get_user_input(
        "Use experimental compressed memory? (y/n)",
        True,
        bool
    )
    config["autogenUserProfiles"] = get_user_input(
        "Auto-generate user profiles? (y/n)",
        True,
        bool
    )
    config["hoursBetweenMemorySaves"] = get_user_input(
        "Hours between full memory saves",
        1,
        int
    )
    
    # API Options (empty by default)
    config["APIOptions"] = {}
    
    # Write configuration to file
    print("Name the config file.")
    print("If you want the config load by default, put '_default' at the end.")
    print("Example: omiAI_default.cfg")
    output_file = (get_user_input("Name:") + ".cfg").removesuffix(".cfg")

    print(f"\n--- Saving Configuration ---")
    print(f"Configuration will be saved to '{output_file}'")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    print(f"\n✅ Configuration successfully saved to '{output_file}'!")
    print("\nTo use this configuration with the bot:")
    print("1. Make sure the file is named 'config_default.json' in the bot's directory")
    print("2. Review the generated file to ensure all settings are correct")
    print("3. Run the bot using 'python omiAI_V2.py'")
    
    # Show a preview of the important settings
    print(f"\n📋 Configuration Preview:")
    print(f"- Token: {'*' * len(config['token']) if config['token'] != 'Your token here' else 'NOT SET'}")
    print(f"- Base Directory: {config['baseDir']}")
    print(f"- Number of Models: {len(config['models'])}")
    print(f"- Default Model: {config['defaultModel']}")
    print(f"- Allow DMs: {config['discordAllowDM']}")
    print(f"- Guild Lock: {config['discordGuildLock']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        exit(1)