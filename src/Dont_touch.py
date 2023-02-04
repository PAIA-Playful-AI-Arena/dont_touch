import math
from mlgame.game.paia_game import PaiaGame
from mlgame.utils.enum import get_ai_name
from mlgame.view.decorator import check_game_progress, check_game_result
from mlgame.view.view_model import create_text_view_data, create_asset_init_data, create_image_view_data, \
    create_line_view_data, Scene, create_polygon_view_data, create_rect_view_data
from .mazeMode import MazeMode
from .sound_controller import *

'''need some fuction same as arkanoid which without dash in the name of fuction'''


class Dont_touch(PaiaGame):
    def __init__(self, user_num, game_type, map, time_to_play, sensor_num, sound, *args, **kwargs):
        super().__init__(user_num=user_num)
        self.game_type = game_type
        self.user_num = user_num
        self.is_single = False
        if self.user_num == 1:
            self.is_single = True
        self.maze_id = map - 1
        self.game_end_time = time_to_play
        self.sensor_num = sensor_num
        self.is_sound = sound
        self.set_game_mode()
        self.game_mode.sound_controller.play_music()
        self.is_running = self.isRunning()
        self.map_width = self.game_mode.map.width
        self.map_height = self.game_mode.map.height
        self.scene = Scene(WIDTH, HEIGHT, "#000000", 500 - self.map_width, 480 - self.map_height)
        self.origin_car_pos = [0, 0]

    # self.origin_car_pos = self.game_mode.car_info[0]["center"]

    def update(self, cmd_dict):
        # self.game_mode.ticks()
        self.frame_count += 1
        self.game_mode.handle_event()
        self.game_mode.update_sprite(cmd_dict)
        if not self.isRunning():
            self.is_running = False
            return "RESET"
        for car in self.game_mode.cars:
            if self.origin_car_pos != [0, 0]:
                break
            self.origin_car_pos = car.get_info()["center"]

    def get_data_from_game_to_player(self):
        scene_info = self.get_scene_info
        player_info = {}
        for car in self.game_mode.car_info:
            # type of car is dictionary
            player_info[get_ai_name(int(car["id"]))] = {"frame": scene_info["frame"],
                                                        "status": car["status"],
                                                        "x": car["coordinate"][0],
                                                        "y": car["coordinate"][1],
                                                        "angle": (car["angle"] * 180 / math.pi) % 360,
                                                        "R_sensor": car["r_sensor_value"]["distance"],
                                                        "L_sensor": car["l_sensor_value"]["distance"],
                                                        "F_sensor": car["f_sensor_value"]["distance"],
                                                        "L_T_sensor": car["l_t_sensor_value"]["distance"],
                                                        "R_T_sensor": car["r_t_sensor_value"]["distance"],
                                                        "crash_times": car["crash_times"],
                                                        "end_x": self.game_mode.end_point.get_info()["coordinate"][0],
                                                        "end_y": self.game_mode.end_point.get_info()["coordinate"][1],
                                                        }
        return player_info

    def reset(self):
        self.frame_count = 0
        self.set_game_mode()
        self.game_mode.sound_controller.play_music()

    def isRunning(self):
        return self.game_mode.isRunning()

    @property
    def get_scene_info(self):
        """
        Get the scene information
        """
        scene_info = {
            "frame": self.game_mode.frame,
        }

        for car in self.game_mode.car_info:
            # type of car is dictionary
            scene_info[str(car["id"]) + "P_position"] = car["topleft"]
        return scene_info

    def get_scene_init_data(self) -> dict:
        """
        Get the scene and object information for drawing on the web
        """
        game_info = {"scene": self.scene.__dict__,
                     "assets": []}
        game_info["map_width"] = self.game_mode.map.tileWidth * 20
        game_info["map_height"] = self.game_mode.map.tileHeight * 20
        logo_path = path.join(ASSET_IMAGE_DIR, LOGO)
        logo_url = LOGO_URL
        game_info["assets"].append(create_asset_init_data("logo", 40, 40, logo_path, logo_url))
        bg_path = path.join(ASSET_IMAGE_DIR, BG_IMG)
        bg_url = BG_URL
        game_info["assets"].append(create_asset_init_data("bg_img", 600, 600, bg_path, bg_url))
        for i in range(0, 7):
            game_info["assets"].append(create_asset_init_data(f"car{i}", 50, 50,
                                                              path.join(ASSET_IMAGE_DIR, f"car{i}.png"), "url"))

        return game_info

    @check_game_progress
    def get_scene_progress_data(self) -> dict:
        """
        Get the position of game objects for drawing on the web
        """
        game_progress = {
            "frame": self.frame_count,
            "background": [],
            "object_list": [],
            "toggle_with_bias": [],
            "toggle": [],
            "foreground": [],
            "user_info": [],
            "game_sys_info": {}
        }
        game_progress["game_sys_info"] = {"view_center_coordinate": [200, -1200]}
        for p in self.game_mode.all_points:
            game_progress["object_list"].append(p.get_progress_data())

        # wall
        for wall in self.game_mode.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.trnsfer_box2d_to_pygame(v) for v in vertices]
            game_progress["object_list"].append(create_polygon_view_data("wall", vertices, "#ffffff"))
        for wall in self.game_mode.slant_walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            vertices = [self.game_mode.trnsfer_box2d_to_pygame(v) for v in vertices]
            game_progress["object_list"].append(create_polygon_view_data("wall", vertices, "#ffffff"))

        # end point
        game_progress["background"].append(self.game_mode.end_point.get_progress_data())
        # rect
        # game_progress["background"].append(create_image_view_data("bg_img", 0, 0, 860, 560))
        game_progress["background"].append(create_image_view_data("bg_img", -200, 1200, 800, 800))
        p = self.game_mode.trnsfer_box2d_to_pygame((0, 0))
        # car
        for car in self.game_mode.car_info:
            game_progress["object_list"].append(
                create_image_view_data(car["image"], car["topleft"][0], car["topleft"][1], 50, 40,
                                       car["angle"])
            )
        # game_progress["object_list"].append(
        #     create_rect_view_data("car_r", self.game_mode.car.rect.x, self.game_mode.car.rect.y, self.game_mode.car.rect.width,
        #                           self.game_mode.car.rect.height, RED))

        # text
        game_progress["toggle"].append(
            create_text_view_data("{0:05d} frames".format(self.frame_count), 820, 100, WHITE, font_style="26px Arial"))
        for car in self.game_mode.car_info:
            game_progress["toggle"].append(
                create_text_view_data(f"crash time:{car['crash_times']}", 820, 130, WHITE, font_style="26px Arial"))
            x = 900

            if car["is_running"]:
                #         game_progress["toggle"].append(
                #             create_text_view_data("{:04.1f}".format(car["l_sensor_value"]["distance"]), x-88,
                #                                   178 + 60 + 105 * (car["id"] // 2), "#FFFF00",
                #                                   "15px Arial"))
                #         game_progress["toggle"].append(
                #             create_text_view_data("{:04.1f}".format(car["f_sensor_value"]["distance"]), x-48,
                #                                   178 + 28 + 105 * (car["id"] // 2), "#FF0000",
                #                                   "15px Arial"))
                #         game_progress["toggle"].append(
                #             create_text_view_data("{:04.1f}".format(car["r_sensor_value"]["distance"]), x,
                #                                   178 + 60 + 105 * (car["id"] // 2), "#21A1F1",
                #                                   "15px Arial"))
                #         if car["r_t_sensor_value"]["distance"]!=-1 and car["l_t_sensor_value"]["distance"]!=-1:
                #             game_progress["toggle"].append(
                #                 create_text_view_data("{:04.1f}".format(car["r_t_sensor_value"]["distance"]), x,
                #                                       178 + 30 + 105 * (car["id"] // 2), "#21A1F1",
                #                                       "15px Arial"))
                #             game_progress["toggle"].append(
                #                 create_text_view_data("{:04.1f}".format(car["l_t_sensor_value"]["distance"]), x-88,
                #                                       178 + 30 + 105 * (car["id"] // 2), "#FFFF00",
                #                                       "15px Arial"))
                game_progress["object_list"].append(
                    create_line_view_data("l_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["l_sensor_value"]["coordinate"])[1],
                                          "#FFFF00", 5))

                game_progress["object_list"].append(
                    create_line_view_data("l_top_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["l_t_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["l_t_sensor_value"]["coordinate"])[1],
                                          "#FFFF00", 5))

                game_progress["object_list"].append(
                    create_line_view_data("r_top_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["r_t_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["r_t_sensor_value"]["coordinate"])[1],
                                          "#21A1F1", 5))
                game_progress["object_list"].append(
                    create_line_view_data("r_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["r_sensor_value"]["coordinate"])[1],
                                          "#21A1F1", 5))
                game_progress["object_list"].append(
                    create_line_view_data("f_sensor", car["center"][0], car["center"][1],
                                          self.trnsfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[0],
                                          self.trnsfer_box2d_to_pygame(car["f_sensor_value"]["coordinate"])[1],
                                          "#FF0000", 5))
            else:
                game_progress["toggle"].append(create_text_view_data("{0:05d} frames".format(car["end_frame"]),
                                                                     x - 48, 178 + 30 + 105 * (car["id"] // 2),
                                                                     "#FFFFFF",
                                                                     "16px Arial"))

        return game_progress

    @check_game_result
    def get_game_result(self):
        """
        Get the game result for the web
        """
        scene_info = self.get_scene_info
        result = self.game_mode.result
        rank = []
        # TODO refactor
        for ranking in self.game_mode.ranked_user:
            for user in ranking:
                if self.game_mode.check_point_num:
                    pass_percent = round(user.check_point / self.game_mode.check_point_num, 5) * 100
                    remain_point = self.game_mode.check_point_num - user.check_point
                    remain_percent = 100 - pass_percent
                else:
                    pass_percent = 0
                    remain_point = 0
                    remain_percent = 0
                # same_rank = {"玩家編號": str(user.car_no + 1) + "P",
                #              "單局排名": self.game_mode.ranked_user.index(ranking) + 1,
                #              "使用總幀數": user.end_frame,
                #              "遊戲總幀數限制":self.game_end_time,
                #              "使用時間百分比":round(user.end_frame/self.game_end_time,5)*100,
                #              "檢查點總數量":self.game_mode.check_point_num,
                #              "玩家通過檢查點數量": user.check_point,
                #              "玩家未通過檢查點數量": remain_point,
                #              "檢查點通過率": pass_percent,
                #              "檢查點未通過率": remain_percent,
                # }
                same_rank = {"player": str(user.car_no + 1) + "P",
                             "rank": self.game_mode.ranked_user.index(ranking) + 1,
                             "used_frame": user.end_frame,
                             "frame_limit": self.game_end_time,
                             "frame_percent": round(user.end_frame / self.game_end_time * 100, 3),
                             "total_checkpoints": self.game_mode.check_point_num,
                             "check_points": user.check_point,
                             "remain_points": remain_point,
                             "pass_percent": pass_percent,
                             "remain_percent": remain_percent,
                             "score": (user.end_frame + 120 * user.collide_times) * 100 - user.check_point
                             }
                rank.append(same_rank)

        return {"frame_used": scene_info["frame"],
                "state": self.game_mode.state,
                "attachment": rank,
                }

        pass

    def get_keyboard_command(self):
        """
        Get the command according to the pressed keys
        """
        if not self.isRunning():
            return {"1P": "RESET",
                    "2P": "RESET",
                    "3P": "RESET",
                    "4P": "RESET",
                    "5P": "RESET",
                    "6P": "RESET",
                    }
        key_pressed_list = pygame.key.get_pressed()
        cmd_1P = {"left_PWM": 0, "right_PWM": 0}
        cmd_2P = {"left_PWM": 0, "right_PWM": 0}
        cmd_3P = {"left_PWM": 0, "right_PWM": 0}
        cmd_4P = {"left_PWM": 0, "right_PWM": 0}
        cmd_5P = {"left_PWM": 0, "right_PWM": 0}
        cmd_6P = {"left_PWM": 0, "right_PWM": 0}

        if key_pressed_list[pygame.K_UP]:
            cmd_1P["left_PWM"] = 100
            cmd_1P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_DOWN]:
            cmd_1P["left_PWM"] = -100
            cmd_1P["right_PWM"] = -100
        if key_pressed_list[pygame.K_LEFT]:
            cmd_1P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_RIGHT]:
            cmd_1P["left_PWM"] += 100

        if key_pressed_list[pygame.K_w]:
            cmd_2P["left_PWM"] = 100
            cmd_2P["right_PWM"] = 100
        elif key_pressed_list[pygame.K_s]:
            cmd_2P["left_PWM"] = -100
            cmd_2P["right_PWM"] = -100
        elif key_pressed_list[pygame.K_a]:
            cmd_2P["right_PWM"] += 100
        elif key_pressed_list[pygame.K_d]:
            cmd_2P["left_PWM"] += 100

        return {"1P": cmd_1P,
                "2P": cmd_2P,
                "3P": cmd_3P,
                "4P": cmd_4P,
                "5P": cmd_5P,
                "6P": cmd_6P}

    def set_game_mode(self):
        self.game_mode = MazeMode(self.user_num, self.maze_id + 1, self.game_end_time, self.sensor_num,
                                  self.is_sound)
        self.game_type = "MAZE"

    def trnsfer_box2d_to_pygame(self, coordinate):
        '''
        :param coordinate: vertice of body of box2d object
        :return: center of pygame rect
        '''
        return (
            (coordinate[0] - self.game_mode.pygame_point[0]) * PPM,
            (self.game_mode.pygame_point[1] - coordinate[1]) * PPM)
