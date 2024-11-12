import json
from os import path

def parse_game_version(file_path):
    """
    Parse the version from the game_config.json file.
    
    :param file_path: Path to the game_config.json file
    :return: The version string
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        game_config = json.load(file)
        return game_config.get("version")

# Example usage
version = parse_game_version(path.join(path.dirname(__file__), '..', 'game_config.json'))
