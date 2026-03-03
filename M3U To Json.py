import re
import json
import os
import tkinter as tk
from tkinter import filedialog

def slugify(text):
    """
    Converts a given text string into a slug-like format suitable for dictionary keys.
    It removes common country code prefixes (like "IN: "), converts to lowercase,
    removes non-alphanumeric characters, and replaces spaces/hyphens with underscores.
    """
    # Remove "IN: " prefix if present at the beginning (case-insensitive)
    if text.lower().startswith('in: '):
        text = text[4:] # Remove "IN: "

    text = text.lower()
    # Remove any character that is not a word character (alphanumeric, underscore) or a space/hyphen
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace one or more spaces or hyphens with a single underscore
    text = re.sub(r'[\s-]+', '_', text)
    # Remove leading/trailing underscores
    return text.strip('_')

def convert_m3u_to_json(m3u_filepath, json_filepath):
    """
    Converts an M3U playlist file into a JSON file.
    Each channel in the M3U is represented as an entry in the JSON,
    with a slugified channel name as the key.
    The user is prompted to provide a description for each group,
    with the M3U's 'group-title' as the default.
    Channels without a group will still prompt for individual descriptions.
    """
    channels_data = {}
    unique_group_titles = set()
    channels_to_process = [] # Store parsed channel info before processing descriptions
    
    print(f"Attempting to read M3U file from: {m3u_filepath}")
    try:
        with open(m3u_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print("Warning: M3U file is empty.")
            return

        if not lines[0].strip().startswith('#EXTM3U'):
            print("Warning: M3U file does not start with #EXTM3U header. Attempting to parse anyway.")

        current_channel_temp_info = {}
        for i in range(len(lines)):
            line = lines[i].strip()

            if line.startswith('#EXTINF:'):
                group_title_match = re.search(r'group-title="([^"]*)"', line)
                group_title = group_title_match.group(1) if group_title_match else ""
                
                channel_name_match = re.search(r',([^,]+)$', line)
                channel_name = channel_name_match.group(1).strip() if channel_name_match else "Unknown Channel"
                
                current_channel_temp_info = {
                    'group_title': group_title,
                    'name': channel_name
                }
                if group_title: # Only add non-empty group titles to the set
                    unique_group_titles.add(group_title)

            elif line.startswith('http') and 'name' in current_channel_temp_info:
                current_channel_temp_info['url'] = line
                channels_to_process.append(current_channel_temp_info)
                current_channel_temp_info = {} # Reset for next channel

    except FileNotFoundError:
        print(f"Error: M3U file not found at '{m3u_filepath}'. Please check the path and try again.")
        return
    except Exception as e:
        print(f"An unexpected error occurred during M3U parsing: {e}")
        print("Please ensure the M3U file format is correct (e.g., #EXTINF line followed by a URL on the next line).")
        return

    # Collect descriptions for each unique group title
    group_descriptions = {}
    print("\n--- Please provide descriptions for each group ---")
    for group in sorted(list(unique_group_titles)):
        user_description = input(
            f"Enter description for group '{group}' (Default: '{group}'): "
        ).strip()
        group_descriptions[group] = user_description if user_description else group

    # Process channels and assign descriptions
    key_counter = {}
    for channel_info in channels_to_process:
        group_title = channel_info.get('group_title', '')
        channel_name = channel_info['name']
        channel_url = channel_info['url']
        
        description_to_use = ""
        if group_title and group_title in group_descriptions:
            description_to_use = group_descriptions[group_title]
        else:
            # If no group-title or group-title was empty/not collected, ask for individual description
            user_description = input(
                f"Enter description for channel '{channel_name}' (No group found, Default: '{channel_name}'): "
            ).strip()
            description_to_use = user_description if user_description else channel_name

        # Generate a unique slugified key for the channel
        base_key = slugify(channel_name)
        key = base_key
        count = key_counter.get(base_key, 0)
        while key in channels_data:
            count += 1
            key = f"{base_key}_{count}"
        key_counter[base_key] = count

        channels_data[key] = {
            "name": channel_name,
            "url": channel_url,
            "Group": description_to_use
        }

    print(f"\nAttempting to save JSON file to: {json_filepath}")
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(channels_data, f, indent=4, ensure_ascii=False)
        print(f"\nSuccessfully converted '{m3u_filepath}' to '{json_filepath}'")
    except Exception as e:
        print(f"An error occurred while saving JSON file: {e}")

# --- Script Execution ---
if __name__ == "__main__":
    # Hide the main Tkinter window
    root = tk.Tk()
    root.withdraw()

    # Open GUI file picker for M3U file
    m3u_input_path = filedialog.askopenfilename(
        title="Select M3U Playlist File",
        filetypes=[("M3U files", "*.m3u"), ("All files", "*.*")]
    )

    if not m3u_input_path:
        print("M3U file selection cancelled. Exiting.")
        exit()

    # Open GUI save file dialog for JSON output
    json_output_path = filedialog.asksaveasfilename(
        title="Save JSON Output File As",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )

    if not json_output_path:
        print("JSON output file selection cancelled. Exiting.")
        exit()

    # Ensure the output directory exists (though asksaveasfilename usually handles this for the file itself)
    output_dir = os.path.dirname(json_output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error creating directory '{output_dir}': {e}")
            print("Please ensure the output path is valid and you have write permissions.")
            exit()

    # Perform the conversion
    convert_m3u_to_json(m3u_input_path, json_output_path)
