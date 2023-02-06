import Box2D
import pygame

# from .car import Car
from mlgame.game.paia_game import GameResultState
from mlgame.utils.enum import get_ai_name
from .env import *
from .gameMode import GameMode
from .maze_wall import Wall
# from .points import End_point, Check_point, Outside_point
from .sound_controller import SoundController
from .tilemap import Map
from .tiledMap_to_box2d import TiledMap_box2d


class MazeMode(GameMode):
    def __init__(self, user_num: int, maze_no, time, sensor, sound_controller):
        super(MazeMode, self).__init__()
        '''load map data'''
        self.user_num = user_num
        self.maze_id = maze_no - 1
        self.map_file = f"level_{maze_no}.tmj"
        self.load_data()

        '''group of sprites'''
        self.world = None
        self.cars = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.slant_walls = pygame.sprite.Group()
        self.all_points = pygame.sprite.Group()  # Group inclouding end point, check points,etc.

        '''data set'''
        self.wall_info = []
        self.wall_vertices_for_Box2D = []
        self.car_info = []
        self.ranked_user = []  # pygame.sprite car
        self.result = []
        self.eliminated_user = []

        self.game_end_time = time  # int, decide how many frames the game will end even some users don't finish game
        pygame.font.init()
        self.state = GameResultState.FAIL
        self.is_end = False
        self.sensor_num = sensor
        self.x = 0
        self._init_world(user_num)
        self.new()
        '''sound'''
        self.sound_controller = SoundController(sound_controller)
        # self.world.contactListener.fixtureA = self.car
        # print(self.world.contactListener.m_contactList)

    def new(self):
        # initialize all variables and do all setup for a new game
        self.pygame_point = [10, 100]
        map = TiledMap_box2d(path.join(MAP_DIR, self.map_file), 32)
        walls = map.get_wall_info()
        # self.contact.fixtureA = self.car.box
        for wall in walls:
            vertices = map.transfer_to_box2d(wall)
            wall = Wall(self, vertices, self.world)
            self.walls.add(wall)
            # self.contact.fixtureB = wall.box
        obj = map.load_other_obj()
        self.load_map_object(obj)
        for wall in self.walls:
            vertices = [(wall.body.transform * v) for v in wall.box.shape.vertices]
            self.wall_info.append([vertices[0], vertices[1]])
            self.wall_info.append([vertices[2], vertices[1]])
            self.wall_info.append([vertices[3], vertices[0]])
            self.wall_info.append([vertices[2], vertices[3]])
        # self.limit_pygame_screen()

    def update_sprite(self, command):
        '''update the model of game,call this fuction per frame'''
        self.car_info.clear()
        self.frame += 1
        self.handle_event()
        self._is_game_end()
        self.command = command
        for car in self.cars:
            car.update(command[get_ai_name(car.car_no)])
            car.rect.center = self.trnsfer_box2d_to_pygame(car.body.position)
            self.car_info.append(car.get_info())
            car.detect_distance(self.frame, self.wall_info)

        self.all_points.update()
        if len(self.car.body.contacts) > 2:
            contact = 0
            for contact_edge in self.car.body.contacts:
                if contact_edge.contact.touching:
                    contact += 1
            if contact > 2:
                self.car.collide(self.frame)
        for point in self.all_points:
            point.rect.x, point.rect.y = self.trnsfer_box2d_to_pygame((point.x, point.y))
        self.world.Step(TIME_STEP, 10, 10)
        self.world.ClearForces()
        if self.is_end:
            self.running = False

    def limit_pygame_screen(self):
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_w]:
            self.pygame_point[1] += 0.2
        elif keystate[pygame.K_s]:
            self.pygame_point[1] -= 0.2
        elif keystate[pygame.K_a]:
            self.pygame_point[0] -= 0.2
        elif keystate[pygame.K_d]:
            self.pygame_point[0] += 0.2

        if self.pygame_point[1] > 0:
            self.pygame_point[1] = 0
        elif self.pygame_point[1] < TILE_HEIGHT / PPM - self.map.tileHeight:
            self.pygame_point[1] = TILE_HEIGHT / PPM - self.map.tileHeight
        else:
            pass
        if self.pygame_point[0] > self.map.tileWidth - TILE_WIDTH / PPM:
            self.pygame_point[0] = self.map.tileWidth - TILE_WIDTH / PPM
        elif self.pygame_point[0] < 0:
            self.pygame_point[0] = 0
        else:
            pass

    def load_data(self):
        map_folder = path.join(path.dirname(__file__), "map")
        try:
            self.map = Map(path.join(map_folder, self.map_file))
        except Exception:
            print(f"File '{self.map_file}' is not found.We will load first map for you.")
            self.map_file = "level_2.tmj"
            self.map = Map(path.join(map_folder, self.map_file))

    def _init_world(self, user_no: int):
        self.contact_man = Box2D.b2ContactManager()
        self.world = Box2D.b2.world(gravity=(0, 0), doSleep=True, CollideConnected=False, contactListener=self.contact_man.contactListener)


    def _is_game_end(self):
        """
            遊戲結束條件
            1. 全部玩家抵達終點
            2. 時間結束
        """
        if self.frame >= self.game_end_time:
            for car in self.cars:
                if car not in self.eliminated_user and car.is_running:
                    car.end_frame = self.frame
                    self.eliminated_user.append(car)
                    car.is_running = False
                    car.status = "GAME_OVER"
            self.is_end = True
            self.ranked_user = self.rank()
            self._print_result()
            self.status = "END"

        elif len(self.cars) == len(self.eliminated_user):
            self.is_end = True
            self.ranked_user = self.rank()
            self._print_result()
            self.status = "END"

