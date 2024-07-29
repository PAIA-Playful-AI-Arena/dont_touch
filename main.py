import sys

import pygame

sys.path.append(r"../..")

from mlgame.view.view import PygameView
from mlgame.game.generic import quit_or_esc
from src.Dont_touch import Dont_touch

FPS = 30
if __name__ == '__main__':
    pygame.init()
    game = Dont_touch(user_num=1, map_num=1, time_to_play=450, sound="off", dark_mode='dark', map_file=None)
    scene_init_info_dict = game.get_scene_init_data()
    game_view = PygameView(scene_init_info_dict)
    frame_count = 0
    while game.is_running and not quit_or_esc():
        pygame.time.Clock().tick_busy_loop(FPS)
        commands = game.get_keyboard_command()
        game.update(commands)
        game_progress_data = game.get_scene_progress_data()
        game_view.draw(game_progress_data)
        frame_count += 1

    pygame.quit()
