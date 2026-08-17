#Zubayer latest
# FINAL MAIN

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

# Car Control & Physics
class CarPhysics:
    def __init__(self):
        self.x = 0
        self.y = -500
        self.z = 10
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.max_reverse_speed = 2.5
        self.acceleration = 0.2
        self.deceleration = 0.1
        self.brake_deceleration = 0.4
        self.rotation_speed = 2.0
        self.gear = "NEUTRAL"
        self.is_braking = False
        self.turning_radius_factor = 0.8
        self.collision_active = False

    def update(self, forward, backward, left, right, brake):
        if self.collision_active:
            self.speed = 0
            self.gear = "NEUTRAL"
            return
        # Gear and acceleration
        if forward and not backward:
            self.gear = "FORWARD"
            if self.speed < self.max_speed:
                self.speed += self.acceleration
        elif backward and not forward:
            self.gear = "REVERSE"
            if self.speed > -self.max_reverse_speed:
                self.speed -= self.acceleration
        else:
            self.gear = "NEUTRAL"
        # Braking
        if brake:
            self.is_braking = True
            if self.speed > 0:
                self.speed -= self.brake_deceleration
                if self.speed < 0:
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.brake_deceleration
                if self.speed > 0:
                    self.speed = 0
        else:
            self.is_braking = False
            # Natural deceleration
            if self.speed > 0:
                self.speed -= self.deceleration
                if self.speed < 0:
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.deceleration
                if self.speed > 0:
                    self.speed = 0
        # Rotation
        if abs(self.speed) > 0.1:
            turn_factor = self.turning_radius_factor * (1 - abs(self.speed) / self.max_speed * 0.5)
            if left:
                self.angle += self.rotation_speed * turn_factor
            if right:
                self.angle -= self.rotation_speed * turn_factor
        # positioning
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

    def stop(self):
        self.speed = 0
        self.gear = "NEUTRAL"
        self.collision_active = True

    def reset_position(self, x, y):
        self.x = x
        self.y = y
        self.z = 10
        self.angle = 0
        self.speed = 0
        self.gear = "NEUTRAL"
        self.collision_active = False


# Environment & Collision

class ParkingEnvironment:
    def __init__(self):
        self.current_level = 1
        self.collision_detected = False
        self.parked_successfully = False
        self.collision_count = 0

    def get_level_config(self):
        configs = {
            1: {
                'parking_spot': (0, 200, 0),
                'parking_size': (80, 120),
                'start_pos': (0, -500),
                'obstacles': [
                    # # Traffic cones
                    {'type': 'cone', 'pos': (-100, 0, 0)},
                    {'type': 'cone', 'pos': (100, 0, 0)},
                    {'type': 'cone', 'pos': (-100, 100, 0)},
                    {'type': 'cone', 'pos': (100, 100, 0)},
                    # Trees along the edges
                    {'type': 'tree', 'pos': (-250, -200, 0)},
                    {'type': 'tree', 'pos': (-250, 100, 0)},
                    {'type': 'tree', 'pos': (250, -200, 0)},
                    {'type': 'tree', 'pos': (250, 100, 0)},
                    # Lamp posts
                    {'type': 'lamp', 'pos': (-200, -400, 0)},
                    {'type': 'lamp', 'pos': (200, -400, 0)},
                    # Bushes
                    {'type': 'bush', 'pos': (-200, 250, 0)},
                    {'type': 'bush', 'pos': (200, 250, 0)},
                    # Flower pots near parking
                    {'type': 'flower', 'pos': (-50, 280, 0)},
                    {'type': 'flower', 'pos': (50, 280, 0)},
                ],
                'walls': [
                    {'start': (-300, -300), 'end': (-300, 300)},
                    {'start': (300, -300), 'end': (300, 300)},
                    {'start': (-300, 300), 'end': (300, 300)},
                    {'start': (-300, -600), 'end': (300, -600)},
                ]
            },
            2: {
                'parking_spot': (200, 200, 0),
                'parking_size': (80, 120),
                'start_pos': (-200, -500),
                'obstacles': [
                    # # Traffic cones
                    {'type': 'cone', 'pos': (-50, -100, 0)},
                    {'type': 'cone', 'pos': (50, -100, 0)},
                    {'type': 'cone', 'pos': (0, 0, 0)},
                    {'type': 'cone', 'pos': (150, 0, 0)},
                    # Trees
                    {'type': 'tree', 'pos': (-350, -100, 0)},
                    {'type': 'tree', 'pos': (-350, 200, 0)},
                    {'type': 'tree', 'pos': (350, -100, 0)},
                    {'type': 'tree', 'pos': (350, 200, 0)},
                    # Barriers
                    {'type': 'barrier', 'pos': (-300, 130, 0), 'length': 80, 'angle': 0},
                    {'type': 'barrier', 'pos': (300, 130, 0), 'length': 80, 'angle': 0},
                    # Lamp posts
                    {'type': 'lamp', 'pos': (-300, -400, 0)},
                    {'type': 'lamp', 'pos': (0, -400, 0)},
                    {'type': 'lamp', 'pos': (300, -400, 0)},
                    # Benches
                    {'type': 'bench', 'pos': (-350, 0, 0), 'angle': 90},
                    {'type': 'bench', 'pos': (350, 0, 0), 'angle': -90},
                    # Trash cans
                    {'type': 'trash', 'pos': (-280, -250, 0)},
                    {'type': 'trash', 'pos': (280, -250, 0)},
                    # Bushes
                    {'type': 'bush', 'pos': (-100, 270, 0)},
                    {'type': 'bush', 'pos': (100, 270, 0)},
                    {'type': 'bush', 'pos': (300, 270, 0)},
                ],
                'walls': [
                    {'start': (-400, -300), 'end': (-400, 300)},
                    {'start': (400, -300), 'end': (400, 300)},
                    {'start': (-400, 300), 'end': (400, 300)},
                    {'start': (-400, -600), 'end': (400, -600)},
                ]
            },
            3: {
                'parking_spot': (-250, 250, 0),
                'parking_size': (80, 120),
                'start_pos': (250, -500),
                'obstacles': [
                    # Traffic cones
                    {'type': 'cone', 'pos': (100, -200, 0)},
                    {'type': 'cone', 'pos': (0, -100, 0)},
                    {'type': 'cone', 'pos': (-100, 0, 0)},
                    {'type': 'cone', 'pos': (-200, 100, 0)},
                    {'type': 'building', 'pos': (200, -200, 0)},
                    {'type': 'cone', 'pos': (200, 0, 0)},
                    {'type': 'cone', 'pos': (150, 100, 0)},
                    # Trees
                    {'type': 'tree', 'pos': (-450, -300, 0)},
                    {'type': 'tree', 'pos': (-450, 0, 0)},
                    {'type': 'tree', 'pos': (-450, 300, 0)},
                    {'type': 'tree', 'pos': (450, -300, 0)},
                    {'type': 'tree', 'pos': (450, 0, 0)},
                    {'type': 'tree', 'pos': (450, 300, 0)},
                    # Lamp posts
                    {'type': 'lamp', 'pos': (-350, -500, 0)},
                    {'type': 'lamp', 'pos': (0, -500, 0)},
                    {'type': 'lamp', 'pos': (350, -500, 0)},
                    {'type': 'lamp', 'pos': (-350, 350, 0)},
                    {'type': 'lamp', 'pos': (350, 350, 0)},
                    # Barriers
                    {'type': 'barrier', 'pos': (-300, -50, 0), 'length': 100, 'angle': 45},
                    {'type': 'barrier', 'pos': (50, 50, 0), 'length': 80, 'angle': -30},
                    # Benches
                    {'type': 'bench', 'pos': (-400, -150, 0), 'angle': 90},
                    {'type': 'bench', 'pos': (400, 150, 0), 'angle': -90},
                    # Bushes
                    {'type': 'bush', 'pos': (-350, 350, 0)},
                    {'type': 'bush', 'pos': (-150, 350, 0)},
                    {'type': 'bush', 'pos': (250, 350, 0)},
                    # Trash cans
                    {'type': 'trash', 'pos': (400, -400, 0)},
                    {'type': 'trash', 'pos': (-400, 350, 0)},
                    # Flower pots
                    {'type': 'flower', 'pos': (-350, 250, 0)},
                    {'type': 'flower', 'pos': (-150, 250, 0)},
                ],
                'walls': [
                    {'start': (-500, -400), 'end': (-500, 400)},
                    {'start': (500, -400), 'end': (500, 400)},
                    {'start': (-500, 400), 'end': (500, 400)},
                    {'start': (-500, -700), 'end': (500, -700)},
                ]
            },
            4: {
                'parking_spot': (-450, 400, 0),
                'parking_size': (70, 110),
                'start_pos': (450, -700),
                'obstacles': [
                    #Traffic cones
                    {'type': 'cone', 'pos': (350, -600, 0)},
                    {'type': 'cone', 'pos': (550, -600, 0)},
                    {'type': 'cone', 'pos': (300, -500, 0)},
                    {'type': 'cone', 'pos': (400, -500, 0)},
                    {'type': 'cone', 'pos': (500, -500, 0)},
                    {'type': 'cone', 'pos': (-50, -400, 0)},
                    {'type': 'cone', 'pos': (50, -400, 0)},
                    {'type': 'cone', 'pos': (150, -350, 0)},
                    {'type': 'cone', 'pos': (-150, -350, 0)},
                    {'type': 'cone', 'pos': (0, -300, 0)},
                    {'type': 'cone', 'pos': (-100, -250, 0)},
                    {'type': 'cone', 'pos': (100, -250, 0)},
                    {'type': 'cone', 'pos': (-200, -200, 0)},
                    {'type': 'cone', 'pos': (200, -200, 0)},
                    {'type': 'cone', 'pos': (-300, -50, 0)},
                    {'type': 'cone', 'pos': (-200, 0, 0)},
                    {'type': 'cone', 'pos': (-100, 50, 0)},
                    {'type': 'cone', 'pos': (0, 100, 0)},
                    {'type': 'cone', 'pos': (100, 150, 0)},
                    {'type': 'cone', 'pos': (200, 200, 0)},
                    {'type': 'cone', 'pos': (300, 250, 0)},
                    {'type': 'cone', 'pos': (-350, 300, 0)},
                    {'type': 'cone', 'pos': (-250, 350, 0)},
                    {'type': 'cone', 'pos': (-550, 350, 0)},
                    {'type': 'cone', 'pos': (-400, 480, 0)},
                    {'type': 'cone', 'pos': (-500, 480, 0)},
                    # Buildings
                    {'type': 'building', 'pos': (600, -400, 0)},
                    {'type': 'building', 'pos': (600, -200, 0)},
                    {'type': 'building', 'pos': (600, 0, 0)},
                    {'type': 'building', 'pos': (600, 200, 0)},
                    {'type': 'building', 'pos': (600, 400, 0)},
                    {'type': 'building', 'pos': (-600, -400, 0)},
                    {'type': 'building', 'pos': (-600, -100, 0)},
                    {'type': 'building', 'pos': (-600, 150, 0)},
                    {'type': 'building', 'pos': (0, 0, 0)},
                    {'type': 'building', 'pos': (-450, -100, 0)},
                    # Barriers
                    {'type': 'barrier', 'pos': (-200, -400, 0), 'length': 150, 'angle': 0},
                    {'type': 'barrier', 'pos': (300, -400, 0), 'length': 120, 'angle': 45},
                    {'type': 'barrier', 'pos': (-400, -50, 0), 'length': 100, 'angle': 90},
                    {'type': 'barrier', 'pos': (350, 0, 0), 'length': 80, 'angle': -30},
                    {'type': 'barrier', 'pos': (-100, 250, 0), 'length': 100, 'angle': 0},
                    {'type': 'barrier', 'pos': (150, 250, 0), 'length': 80, 'angle': 0},
                    {'type': 'barrier', 'pos': (-480, 330, 0), 'length': 60, 'angle': 90},
                    {'type': 'barrier', 'pos': (-420, 330, 0), 'length': 60, 'angle': 90},
                    # Trees
                    {'type': 'tree', 'pos': (-650, -600, 0)},
                    {'type': 'tree', 'pos': (-650, -400, 0)},
                    {'type': 'tree', 'pos': (-650, -200, 0)},
                    {'type': 'tree', 'pos': (-650, 0, 0)},
                    {'type': 'tree', 'pos': (-650, 200, 0)},
                    {'type': 'tree', 'pos': (-650, 400, 0)},
                    {'type': 'tree', 'pos': (-650, 550, 0)},
                    {'type': 'tree', 'pos': (650, -600, 0)},
                    {'type': 'tree', 'pos': (650, -400, 0)},
                    {'type': 'tree', 'pos': (650, -200, 0)},
                    {'type': 'tree', 'pos': (650, 0, 0)},
                    {'type': 'tree', 'pos': (650, 200, 0)},
                    {'type': 'tree', 'pos': (650, 400, 0)},
                    {'type': 'tree', 'pos': (650, 550, 0)},
                    {'type': 'tree', 'pos': (-350, -350, 0)},
                    {'type': 'tree', 'pos': (450, -350, 0)},
                    {'type': 'tree', 'pos': (-450, 350, 0)},
                    {'type': 'tree', 'pos': (450, 350, 0)},
                    # Lamp posts
                    {'type': 'lamp', 'pos': (-500, -750, 0)},
                    {'type': 'lamp', 'pos': (-200, -750, 0)},
                    {'type': 'lamp', 'pos': (200, -750, 0)},
                    {'type': 'lamp', 'pos': (500, -750, 0)},
                    {'type': 'lamp', 'pos': (-500, 550, 0)},
                    {'type': 'lamp', 'pos': (-200, 550, 0)},
                    {'type': 'lamp', 'pos': (200, 550, 0)},
                    {'type': 'lamp', 'pos': (500, 550, 0)},
                    # Benches
                    {'type': 'bench', 'pos': (-580, -500, 0), 'angle': 90},
                    {'type': 'bench', 'pos': (580, -500, 0), 'angle': -90},
                    {'type': 'bench', 'pos': (-580, 300, 0), 'angle': 90},
                    {'type': 'bench', 'pos': (580, 300, 0), 'angle': -90},
                    # Trash cans
                    {'type': 'trash', 'pos': (-600, -700, 0)},
                    {'type': 'trash', 'pos': (600, -700, 0)},
                    {'type': 'trash', 'pos': (-600, 500, 0)},
                    {'type': 'trash', 'pos': (600, 500, 0)},
                    {'type': 'trash', 'pos': (0, -550, 0)},
                    {'type': 'trash', 'pos': (0, 500, 0)},
                    # Bushes
                    {'type': 'bush', 'pos': (-350, 550, 0)},
                    {'type': 'bush', 'pos': (-150, 550, 0)},
                    {'type': 'bush', 'pos': (50, 550, 0)},
                    {'type': 'bush', 'pos': (250, 550, 0)},
                    {'type': 'bush', 'pos': (450, 550, 0)},
                    {'type': 'bush', 'pos': (-500, -550, 0)},
                    {'type': 'bush', 'pos': (-300, -550, 0)},
                    # Flower pots
                    {'type': 'flower', 'pos': (-380, 400, 0)},
                    {'type': 'flower', 'pos': (-520, 400, 0)},
                    {'type': 'flower', 'pos': (-450, 320, 0)},
                    {'type': 'flower', 'pos': (-450, 520, 0)},
                ],
                'walls': [
                    {'start': (-700, -600), 'end': (-700, 600)},
                    {'start': (700, -600), 'end': (700, 600)},
                    {'start': (-700, 600), 'end': (700, 600)},
                    {'start': (-700, -900), 'end': (700, -900)},
                ]
            }
        }
        return configs.get(self.current_level, configs[1])

    def check_collision(self, car):
        config = self.get_level_config()
        rad = math.radians(car.angle)
        offset = 18
        points = [
            (car.x, car.y), # Center
            (car.x + offset * math.cos(rad), car.y + offset * math.sin(rad)), # Front
            (car.x - offset * math.cos(rad), car.y - offset * math.sin(rad))  # Rear
        ]

        point_radius = 12

        for px, py in points:
            # Check wall collisions
            for wall in config['walls']:
                if self.check_wall_collision(px, py, point_radius, wall):
                    self.collision_detected = True
                    self.collision_count += 1
                    return True
            # Check obstacle collisions
            for obs in config['obstacles']:
                if obs['type'] == 'cone':
                    dx = px - obs['pos'][0]
                    dy = py - obs['pos'][1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < point_radius + 8:
                        self.collision_detected = True
                        self.collision_count += 1
                        return True
                elif obs['type'] in ['car', 'building']:
                    dx = abs(px - obs['pos'][0])
                    dy = abs(py - obs['pos'][1])
                    obs_w = 40 if obs['type'] == 'car' else 60
                    obs_h = 20 if obs['type'] == 'car' else 60
                    if dx < point_radius + obs_w/2 and dy < point_radius + obs_h/2:
                        self.collision_detected = True
                        self.collision_count += 1
                        return True
                elif obs['type'] in ['tree', 'lamp', 'barrier', 'bench', 'trash', 'flower', 'bush']:
                    dx = px - obs['pos'][0]
                    dy = py - obs['pos'][1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    obj_radius = 15
                    if dist < point_radius + obj_radius:
                        self.collision_detected = True
                        self.collision_count += 1
                        return True
        return False

    def check_wall_collision(self, x, y, radius, wall):
        x1, y1 = wall['start']
        x2, y2 = wall['end']
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.sqrt((x - x1)**2 + (y - y1)**2) < radius
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        dist = math.sqrt((x - closest_x)**2 + (y - closest_y)**2)
        return dist < radius

    def check_parking_success(self, car):
        config = self.get_level_config()
        spot = config['parking_spot']
        size = config['parking_size']

        # position
        dx = abs(car.x - spot[0])
        dy = abs(car.y - spot[1])
        in_position = dx < size[0]/2 and dy < size[1]/2
        normalized_angle = car.angle % 360
        # Acceptable angles
        correct_angle = (abs(normalized_angle - 90) < 20 or
                        abs(normalized_angle - 270) < 20 or
                        abs(normalized_angle + 90) < 20)

        # Check stopped
        stopped = abs(car.speed) < 0.1

        if in_position and correct_angle and stopped:
            self.parked_successfully = True
            return True
        return False



# Camera, UI & Scoring

class CameraSystem:
    def __init__(self):
        self.mode = "THIRD_PERSON"
        self.modes = ["THIRD_PERSON", "FIRST_PERSON", "TOP_DOWN"]
        self.current_mode_index = 0
        # Third-person camera parameters
        self.distance = 300
        self.height = 200
        self.angle_h = 0
        self.angle_v = 30
        self.min_distance = 100
        self.max_distance = 600
        # Top-down camera parameters
        self.top_down_height = 800

    def cycle_mode(self):
        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
        self.mode = self.modes[self.current_mode_index]

    def setup_camera(self, car):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, 1.25, 0.1, 3000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if self.mode == "THIRD_PERSON":
            cam_angle = math.radians(car.angle + 180 + self.angle_h)
            cam_x = car.x + self.distance * math.cos(cam_angle)
            cam_y = car.y + self.distance * math.sin(cam_angle)
            cam_z = car.z + self.height + self.angle_v
            gluLookAt(cam_x, cam_y, cam_z,
                     car.x, car.y, car.z,
                     0, 0, 1)
        elif self.mode == "FIRST_PERSON":
            # First-person camera parameters
            cam_angle = math.radians(car.angle)
            cam_x = car.x + 20 * math.cos(cam_angle)
            cam_y = car.y + 20 * math.sin(cam_angle)
            cam_z = car.z + 40

            look_x = car.x + 100 * math.cos(cam_angle)
            look_y = car.y + 100 * math.sin(cam_angle)

            gluLookAt(cam_x, cam_y, cam_z,
                     look_x, look_y, car.z + 35,
                     0, 0, 1)

        elif self.mode == "TOP_DOWN":
            # Bird's eye view
            cam_x = car.x
            cam_y = car.y
            cam_z = self.top_down_height
            gluLookAt(cam_x, cam_y, cam_z,
                     car.x, car.y, car.z,
                     0, 1, 0)

    def mouse_rotate(self, dx, dy):
        if self.mode == "THIRD_PERSON":
            self.angle_h += dx * 0.5
            self.angle_v += dy * 0.5
            self.angle_v = max(-30, min(60, self.angle_v))

    def mouse_zoom(self, delta):
        if self.mode == "THIRD_PERSON":
            self.distance += delta * 20
            self.distance = max(self.min_distance, min(self.max_distance, self.distance))
        elif self.mode == "TOP_DOWN":
            self.top_down_height += delta * 50
            self.top_down_height = max(400, min(1500, self.top_down_height))


class GameUI:
    def __init__(self):
        self.start_time = time.time()
        self.game_state = "PLAYING"
        self.best_times = [float('inf')] * 4
        self.level_times = [0] * 4
        self.score = 0
        self.max_collisions = 5

    def reset_timer(self):
        self.start_time = time.time()

    def calculate_score(self, level, elapsed_time, collisions):
        base_score = 1000 * level
        time_penalty = int(elapsed_time * 10)
        collision_penalty = collisions * 100
        return max(0, base_score - time_penalty - collision_penalty)

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        glWindowPos2i(int(x), int(y))
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        glEnable(GL_DEPTH_TEST)

    def draw_colored_text(self, x, y, text, color, font=GLUT_BITMAP_HELVETICA_18):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3f(color[0], color[1], color[2])
        glWindowPos2i(int(x), int(y))
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        glEnable(GL_DEPTH_TEST)

    def draw_start_screen(self):
        # Title
        self.draw_colored_text(300, 550, "3D PARKING SIMULATOR", (1, 1, 0), GLUT_BITMAP_TIMES_ROMAN_24)
        # Instructions
        self.draw_text(350, 450, "HOW TO PLAY:")
        self.draw_text(250, 410, "Navigate your car to the green parking spot")
        self.draw_text(280, 380, "Avoid obstacles and stay within bounds")
        # Controls
        self.draw_colored_text(380, 320, "CONTROLS:", (0.5, 1, 0.5))
        self.draw_text(300, 280, "Arrow Keys - Drive and Steer")
        self.draw_text(300, 250, "C - Switch Camera View")
        self.draw_text(300, 220, "H - Toggle Headlights")
        self.draw_text(300, 190, "R - Restart Level | T - Reset Game")
        # Start prompt
        self.draw_colored_text(320, 100, "Press SPACE to Start!", (0, 1, 0), GLUT_BITMAP_TIMES_ROMAN_24)

    def draw_game_over_screen(self, env):
        # Game Over title
        self.draw_colored_text(350, 500, "GAME OVER!", (1, 0.2, 0.2), GLUT_BITMAP_TIMES_ROMAN_24)
        # Stats
        self.draw_text(350, 420, f"Total Collisions: {env.collision_count}")
        self.draw_text(350, 380, f"Level Reached: {env.current_level}/4")
        self.draw_text(350, 340, f"Final Score: {self.score}")
        # Restart prompt
        self.draw_colored_text(300, 220, "Press T to Try Again", (1, 1, 0), GLUT_BITMAP_HELVETICA_18)
        self.draw_text(330, 180, "Press ESC to Exit")

    def draw_win_screen(self, env):
        elapsed = time.time() - self.start_time
        # Victory title
        self.draw_colored_text(280, 550, "CONGRATULATIONS!", (0, 1, 0), GLUT_BITMAP_TIMES_ROMAN_24)
        self.draw_colored_text(280, 500, "ALL LEVELS COMPLETED!", (1, 1, 0), GLUT_BITMAP_TIMES_ROMAN_24)
        # Final stats
        self.draw_text(350, 420, f"Total Score: {self.score}")
        self.draw_text(350, 380, f"Total Collisions: {env.collision_count}")
        # Restart prompt
        self.draw_colored_text(300, 250, "Press T to Play Again", (0.5, 1, 0.5))
        self.draw_text(330, 210, "Press ESC to Exit")

    def draw_hud(self, car, env, camera):
        elapsed = time.time() - self.start_time
        window_height = glutGet(GLUT_WINDOW_HEIGHT)
        y_top = window_height - 30
        # Level
        self.draw_colored_text(20, y_top, f"Level: {env.current_level}/4", (1, 1, 0))
        # Time
        self.draw_text(160, y_top, f"Time: {elapsed:.1f}s")
        # Speed
        speed_percent = abs(car.speed) / car.max_speed * 100
        speed_color = (0, 1, 0) if speed_percent < 50 else ((1, 1, 0) if speed_percent < 80 else (1, 0.3, 0.3))
        self.draw_colored_text(300, y_top, f"Speed: {abs(car.speed):.1f}", speed_color)
        # Gear
        gear_colors = {"FORWARD": (0, 1, 0), "REVERSE": (1, 0.5, 0), "NEUTRAL": (0.7, 0.7, 0.7)}
        self.draw_colored_text(450, y_top, f"Gear: {car.gear}", gear_colors.get(car.gear, (1, 1, 1)))
        # Collisions
        collision_color = (1, 1, 1)
        if env.collision_count >= self.max_collisions - 1:
            collision_color = (1, 0.3, 0.3)
        elif env.collision_count >= self.max_collisions - 2:
            collision_color = (1, 1, 0)
        self.draw_colored_text(620, y_top, f"Collisions: {env.collision_count}", collision_color)
        # Score (Right aligned roughly)
        self.draw_text(800, y_top, f"Score: {self.score}")
        # Controls
        y_ctrl = 50
        self.draw_text(20, y_ctrl + 30, "Controls: Arrow Keys=Drive | C=Camera | H=Lights | J=Doors | V=Model")
        self.draw_text(20, y_ctrl, "R=Restart Level | T=Restart Game | ESC=Exit")
        # Level Complete Message
        if env.parked_successfully:
            self.draw_text(350, 400, "LEVEL COMPLETE!", GLUT_BITMAP_TIMES_ROMAN_24)
            self.draw_text(300, 360, f"Time: {elapsed:.1f}s | Press SPACE for next level")



# DRAWING FUNCTIONS

def draw_car(car, lights_on, doors_open, model_type, steering_angle):
    glPushMatrix()
    glTranslatef(car.x, car.y, car.z)
    glRotatef(car.angle, 0, 0, 1)
    body_colors = {
        'sedan': (0.8, 0.2, 0.2),
        'suv': (0.2, 0.3, 0.8),
        'hatchback': (0.9, 0.7, 0.1),
        'sports': (0.1, 0.9, 0.3)
    }
    color = body_colors.get(model_type, (0.8, 0.2, 0.2))

    # Main body
    glColor3f(*color)
    glPushMatrix()
    if model_type == 'suv':
        glScalef(1.2, 1, 1.3)
    elif model_type == 'sports':
        glScalef(1.1, 1, 0.8)
    glScalef(40, 20, 15)
    glutSolidCube(1)
    glPopMatrix()
    # Roof
    glColor3f(color[0]*0.8, color[1]*0.8, color[2]*0.8)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(30, 18, 10)
    glutSolidCube(1)
    glPopMatrix()
    # Wheels
    glColor3f(0.1, 0.1, 0.1)
    wheel_positions = [(15, 12, -5), (15, -12, -5), (-15, 12, -5), (-15, -12, -5)]
    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 3, 10, 1)
        glPopMatrix()
    # Headlights
    if lights_on:
        glColor3f(1, 1, 0.8)
        glPushMatrix()
        glTranslatef(22, 8, 0)
        glutSolidSphere(3, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(22, -8, 0)
        glutSolidSphere(3, 10, 10)
        glPopMatrix()
    # Tail lights
    glColor3f(0.5, 0, 0)
    if car.is_braking:
        glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(-22, 8, 0)
    glutSolidSphere(2, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-22, -8, 0)
    glutSolidSphere(2, 10, 10)
    glPopMatrix()
    # Doors
    door_color = (color[0]*0.9, color[1]*0.9, color[2]*0.9)
    interior_color = (0.3, 0.25, 0.2)
    if doors_open:
        glPushMatrix()
        glTranslatef(5, 10, 2)
        glRotatef(60, 0, 0, 1)
        # Door outer panel
        glColor3f(*door_color)
        glPushMatrix()
        glTranslatef(-12, 12, 5)
        glScalef(24, 2, 16)
        glutSolidCube(1)
        glPopMatrix()
        # Door inner panel
        glColor3f(*interior_color)
        glPushMatrix()
        glTranslatef(-12, 10.5, 5)
        glScalef(22, 0.5, 14)
        glutSolidCube(1)
        glPopMatrix()
        # Door window frame
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(-10, 12, 13)
        glScalef(18, 2.5, 5)
        glutSolidCube(1)
        glPopMatrix()
        # Door handle
        glColor3f(0.8, 0.8, 0.8)
        glPushMatrix()
        glTranslatef(-15, 13.5, 5)
        glScalef(5, 1.5, 2)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()
        # IGHT DOOR
        glPushMatrix()
        glTranslatef(5, -10, 2)
        glRotatef(-60, 0, 0, 1)
        # Door outer panel
        glColor3f(*door_color)
        glPushMatrix()
        glTranslatef(-12, -12, 5)
        glScalef(24, 2, 16)
        glutSolidCube(1)
        glPopMatrix()
        # Door inner panel
        glColor3f(*interior_color)
        glPushMatrix()
        glTranslatef(-12, -10.5, 5)
        glScalef(22, 0.5, 14)
        glutSolidCube(1)
        glPopMatrix()
        # Door window frame
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(-10, -12, 13)
        glScalef(18, 2.5, 5)
        glutSolidCube(1)
        glPopMatrix()
        # Door handle
        glColor3f(0.8, 0.8, 0.8)
        glPushMatrix()
        glTranslatef(-15, -13.5, 5)
        glScalef(5, 1.5, 2)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()
        # HOOD
        glPushMatrix()
        glTranslatef(20, 0, 8)
        glRotatef(-50, 0, 1, 0)
        # Hood panel
        glColor3f(*door_color)
        glPushMatrix()
        glTranslatef(-8, 0, 1)
        glScalef(16, 18, 2)
        glutSolidCube(1)
        glPopMatrix()
        # Hood inner side
        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(-8, 0, -0.5)
        glScalef(14, 16, 0.5)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()
        # Engine bay
        glColor3f(0.15, 0.15, 0.15)
        glPushMatrix()
        glTranslatef(14, 0, 5)
        glScalef(10, 14, 6)
        glutSolidCube(1)
        glPopMatrix()
        # TRUNK
        glPushMatrix()
        glTranslatef(-20, 0, 8)
        glRotatef(50, 0, 1, 0)
        # Trunk lid
        glColor3f(*door_color)
        glPushMatrix()
        glTranslatef(6, 0, 1)
        glScalef(12, 18, 2)
        glutSolidCube(1)
        glPopMatrix()
        # Trunk inside
        glColor3f(0.25, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(6, 0, -0.5)
        glScalef(10, 16, 0.5)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()
        # Trunk space visible
        glColor3f(0.2, 0.18, 0.18)
        glPushMatrix()
        glTranslatef(-14, 0, 4)
        glScalef(8, 14, 5)
        glutSolidCube(1)
        glPopMatrix()
        # Draw door frame gaps
        glColor3f(0.05, 0.05, 0.05)
        glLineWidth(3)
        # Left door frame
        glBegin(GL_LINE_LOOP)
        glVertex3f(-8, 11, -5)
        glVertex3f(8, 11, -5)
        glVertex3f(8, 11, 12)
        glVertex3f(-8, 11, 12)
        glEnd()
        # Right door frame
        glBegin(GL_LINE_LOOP)
        glVertex3f(-8, -11, -5)
        glVertex3f(8, -11, -5)
        glVertex3f(8, -11, 12)
        glVertex3f(-8, -11, 12)
        glEnd()
    else:
        # Doors closed
        glColor3f(0.05, 0.05, 0.05)
        glLineWidth(2)
        # Left door outline
        glBegin(GL_LINE_LOOP)
        glVertex3f(-8, 10.5, -5)
        glVertex3f(8, 10.5, -5)
        glVertex3f(8, 10.5, 10)
        glVertex3f(-8, 10.5, 10)
        glEnd()
        # Right door outline
        glBegin(GL_LINE_LOOP)
        glVertex3f(-8, -10.5, -5)
        glVertex3f(8, -10.5, -5)
        glVertex3f(8, -10.5, 10)
        glVertex3f(-8, -10.5, 10)
        glEnd()
        # Hood outline
        glBegin(GL_LINE_LOOP)
        glVertex3f(12, -8, 8)
        glVertex3f(20, -8, 8)
        glVertex3f(20, 8, 8)
        glVertex3f(12, 8, 8)
        glEnd()
        # Trunk outline
        glBegin(GL_LINE_LOOP)
        glVertex3f(-20, -8, 8)
        glVertex3f(-12, -8, 8)
        glVertex3f(-12, 8, 8)
        glVertex3f(-20, 8, 8)
        glEnd()
        # Door handles
        glColor3f(0.8, 0.8, 0.8)
        glPushMatrix()
        glTranslatef(3, 10.5, 4)
        glScalef(5, 0.5, 2)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(3, -10.5, 4)
        glScalef(5, 0.5, 2)
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()

def draw_dashboard(car, steering_angle):
    # dashboard in first person view
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(0, 0, -20)
    glScalef(60, 30, 5)
    glutSolidCube(1)
    glPopMatrix()
    # Steering wheel
    glPushMatrix()
    glTranslatef(0, -5, -15)
    glRotatef(steering_angle, 0, 0, 1)
    glColor3f(0.1, 0.1, 0.1)
    glutSolidTorus(2, 12, 10, 20)
    glPopMatrix()

def draw_parking_spot(pos, size):
    x, y, z = pos
    w, h = size

    glColor3f(0, 1, 0)
    glLineWidth(5)
    glBegin(GL_LINE_LOOP)
    glVertex3f(x - w/2, y - h/2, z + 0.5)
    glVertex3f(x + w/2, y - h/2, z + 0.5)
    glVertex3f(x + w/2, y + h/2, z + 0.5)
    glVertex3f(x - w/2, y + h/2, z + 0.5)
    glEnd()
    # Bright marker
    glColor3f(0, 1, 0)
    glPushMatrix()
    glTranslatef(x, y, z + 30)
    glutSolidSphere(10, 10, 10)
    glPopMatrix()

def draw_cone(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 0.5, 0)
    glutSolidCone(8, 20, 10, 10)
    glPopMatrix()

def draw_obstacle_car(x, y, z, angle):
    glPushMatrix()
    glTranslatef(x, y, z + 7.5)
    glRotatef(-angle, 0, 0, 1)
    color_index = int(abs(x + y)) % 6
    colors = [
        (0.2, 0.4, 0.8),   # Blue
        (0.1, 0.6, 0.3),   # Green
        (0.6, 0.2, 0.6),   # Purple
        (0.9, 0.5, 0.1),   # Orange
        (0.8, 0.2, 0.2),   # Red
        (0.2, 0.7, 0.7),   # Cyan/Teal
    ]
    body_color = colors[color_index]

    # Main body
    glColor3f(*body_color)
    glPushMatrix()
    glScalef(40, 20, 15)
    glutSolidCube(1)
    glPopMatrix()
    # Roof
    glColor3f(body_color[0]*0.7, body_color[1]*0.7, body_color[2]*0.7)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glScalef(25, 16, 8)
    glutSolidCube(1)
    glPopMatrix()
    # Windows
    glColor3f(0.1, 0.1, 0.2)
    glPushMatrix()
    glTranslatef(5, 0, 12)
    glScalef(12, 14, 5)
    glutSolidCube(1)
    glPopMatrix()

    # Wheels (black)
    glColor3f(0.1, 0.1, 0.1)
    wheel_positions = [(12, 10, -6), (12, -10, -6), (-12, 10, -6), (-12, -10, -6)]
    for wx, wy, wz in wheel_positions:
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 4, 2, 8, 1)
        glPopMatrix()
    # Headlights (
    glColor3f(0.9, 0.9, 0.7)
    glPushMatrix()
    glTranslatef(20, 6, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(20, -6, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    # Taillights
    glColor3f(0.8, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(-20, 6, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-20, -6, 0)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    glPopMatrix()

def draw_building(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    glColor3f(0.6, 0.6, 0.7)
    glScalef(60, 60, 100)
    glutSolidCube(1)
    glPopMatrix()

def draw_tree(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Tree trunk
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix()
    gluCylinder(gluNewQuadric(), 8, 6, 40, 10, 10)
    glPopMatrix()
    # Foliage
    glColor3f(0.1, 0.5, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 40)
    glutSolidCone(25, 50, 12, 8)
    glPopMatrix()
    glColor3f(0.15, 0.6, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 60)
    glutSolidCone(20, 40, 12, 8)
    glPopMatrix()
    glColor3f(0.2, 0.7, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 80)
    glutSolidCone(15, 30, 12, 8)
    glPopMatrix()
    glPopMatrix()

def draw_bush(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.2, 0.45, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glutSolidSphere(15, 10, 10)
    glPopMatrix()
    glColor3f(0.15, 0.5, 0.1)
    glPushMatrix()
    glTranslatef(8, 5, 8)
    glutSolidSphere(12, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-8, -5, 12)
    glutSolidSphere(10, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_lamp_post(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Pole
    glColor3f(0.3, 0.3, 0.35)
    glPushMatrix()
    gluCylinder(gluNewQuadric(), 3, 3, 80, 8, 2)
    glPopMatrix()
    # Lamp head
    glColor3f(0.4, 0.4, 0.45)
    glPushMatrix()
    glTranslatef(0, 0, 80)
    glScalef(15, 15, 8)
    glutSolidCube(1)
    glPopMatrix()
    # Light
    glColor3f(1.0, 0.95, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, 75)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    glPopMatrix()

def draw_barrier(x, y, z, length=60, angle=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    # Posts
    glColor3f(0.8, 0.8, 0.8)
    for offset in [-length/2, 0, length/2]:
        glPushMatrix()
        glTranslatef(offset, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 3, 30, 6, 2)
        glPopMatrix()
    # Horizontal bar
    glColor3f(1.0, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glScalef(length, 4, 4)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def draw_bench(x, y, z, angle=0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    # Bench seat
    glColor3f(0.55, 0.35, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(40, 15, 3)
    glutSolidCube(1)
    glPopMatrix()
    # Bench back
    glPushMatrix()
    glTranslatef(0, -6, 25)
    glRotatef(10, 1, 0, 0)
    glScalef(40, 3, 15)
    glutSolidCube(1)
    glPopMatrix()
    # Legs
    glColor3f(0.3, 0.3, 0.35)
    for lx in [-15, 15]:
        glPushMatrix()
        glTranslatef(lx, 5, 0)
        glScalef(3, 10, 15)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(lx, -5, 0)
        glScalef(3, 10, 15)
        glutSolidCube(1)
        glPopMatrix()
    glPopMatrix()

def draw_trash_can(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Can body
    glColor3f(0.2, 0.35, 0.2)
    glPushMatrix()
    gluCylinder(gluNewQuadric(), 10, 8, 25, 10, 2)
    glPopMatrix()
    # Lid
    glColor3f(0.25, 0.4, 0.25)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glutSolidSphere(9, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_flower_pot(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    # Pot
    glColor3f(0.8, 0.4, 0.2)
    glPushMatrix()
    gluCylinder(gluNewQuadric(), 12, 8, 15, 10, 2)
    glPopMatrix()
    # Flowers
    glColor3f(1.0, 0.3, 0.4)
    for fx, fy in [(0, 0), (5, 3), (-5, 3), (3, -4), (-3, -4)]:
        glPushMatrix()
        glTranslatef(fx, fy, 20)
        glutSolidSphere(4, 6, 6)
        glPopMatrix()
    # Leaves
    glColor3f(0.2, 0.6, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glutSolidSphere(8, 8, 8)
    glPopMatrix()
    glPopMatrix()

def draw_ground(walls):
    # Main asphalt surface
    glColor3f(0.15, 0.15, 0.18)
    glBegin(GL_QUADS)
    glVertex3f(-1000, -1000, 0)
    glVertex3f(1000, -1000, 0)
    glVertex3f(1000, 1000, 0)
    glVertex3f(-1000, 1000, 0)
    glEnd()

    # Draw parking spot lines
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(3)

    # Horizontal parking row
    for row_y in [150, 250, 350]:
        for spot_x in range(-400, 450, 100):
            glBegin(GL_QUADS)
            glVertex3f(spot_x - 2, row_y - 50, 0.5)
            glVertex3f(spot_x + 2, row_y - 50, 0.5)
            glVertex3f(spot_x + 2, row_y + 50, 0.5)
            glVertex3f(spot_x - 2, row_y + 50, 0.5)
            glEnd()

    # lane markings
    glColor3f(1.0, 0.8, 0.0)
    for dash_y in range(-600, 100, 60):
        glBegin(GL_QUADS)
        glVertex3f(-3, dash_y, 0.5)
        glVertex3f(3, dash_y, 0.5)
        glVertex3f(3, dash_y + 30, 0.5)
        glVertex3f(-3, dash_y + 30, 0.5)
        glEnd()

    # Drive lane arrows
    glColor3f(1.0, 1.0, 1.0)
    for arrow_y in [-400, -200, 0]:
        # Arrow body
        glBegin(GL_QUADS)
        glVertex3f(-5, arrow_y - 20, 0.5)
        glVertex3f(5, arrow_y - 20, 0.5)
        glVertex3f(5, arrow_y + 20, 0.5)
        glVertex3f(-5, arrow_y + 20, 0.5)
        glEnd()
        # Arrow head
        glBegin(GL_TRIANGLES)
        glVertex3f(0, arrow_y + 35, 0.5)
        glVertex3f(-15, arrow_y + 15, 0.5)
        glVertex3f(15, arrow_y + 15, 0.5)
        glEnd()
    # Crosswalk at entrance
    glColor3f(1.0, 1.0, 1.0)
    for stripe_x in range(-200, 220, 40):
        glBegin(GL_QUADS)
        glVertex3f(stripe_x - 10, -550, 0.5)
        glVertex3f(stripe_x + 10, -550, 0.5)
        glVertex3f(stripe_x + 10, -520, 0.5)
        glVertex3f(stripe_x - 10, -520, 0.5)
        glEnd()
    # Handicap symbol area (blue square with pattern)
    glColor3f(0.2, 0.4, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(-60, 180, 0.3)
    glVertex3f(60, 180, 0.3)
    glVertex3f(60, 220, 0.3)
    glVertex3f(-60, 220, 0.3)
    glEnd()
    # Concrete curbs/walls
    glColor3f(0.5, 0.5, 0.5)
    for wall in walls:
        x1, y1 = wall['start']
        x2, y2 = wall['end']
        # Wall base
        glBegin(GL_QUADS)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(x2, y2, 40)
        glVertex3f(x1, y1, 40)
        glEnd()
        # Wall top
        glColor3f(0.6, 0.6, 0.6)
        glBegin(GL_QUADS)
        glVertex3f(x1, y1, 40)
        glVertex3f(x2, y2, 40)
        glVertex3f(x2, y2, 50)
        glVertex3f(x1, y1, 50)
        glEnd()
        # Yellow warning stripe
        glColor3f(1.0, 0.8, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(x1, y1, 25)
        glVertex3f(x2, y2, 25)
        glVertex3f(x2, y2, 30)
        glVertex3f(x1, y1, 30)
        glEnd()
        glColor3f(0.5, 0.5, 0.5)

def draw_environment(config):
    draw_ground(config['walls'])
    for obs in config['obstacles']:
        if obs['type'] == 'cone':
            draw_cone(*obs['pos'])
        elif obs['type'] == 'car':
            draw_obstacle_car(*obs['pos'], obs['angle'])
        elif obs['type'] == 'building':
            draw_building(*obs['pos'])
        elif obs['type'] == 'tree':
            draw_tree(*obs['pos'])
        elif obs['type'] == 'bush':
            draw_bush(*obs['pos'])
        elif obs['type'] == 'lamp':
            draw_lamp_post(*obs['pos'])
        elif obs['type'] == 'barrier':
            draw_barrier(*obs['pos'], obs.get('length', 60), obs.get('angle', 0))
        elif obs['type'] == 'bench':
            draw_bench(*obs['pos'], obs.get('angle', 0))
        elif obs['type'] == 'trash':
            draw_trash_can(*obs['pos'])
        elif obs['type'] == 'flower':
            draw_flower_pot(*obs['pos'])



# GLOBAL VARIABLES & INITIALIZATION

car = CarPhysics()
environment = ParkingEnvironment()
camera = CameraSystem()
ui = GameUI()

# Input
keys = {'forward': False, 'backward': False, 'left': False, 'right': False, 'brake': False}
lights_on = False
doors_open = False
car_model = 'sedan'
car_models = ['sedan', 'suv', 'hatchback', 'sports']
current_model_index = 0
steering_angle = 0
mouse_x, mouse_y = 0, 0

def reset_level():
    global car, ui
    config = environment.get_level_config()
    car.reset_position(*config['start_pos'])
    environment.collision_detected = False
    environment.parked_successfully = False
    environment.collision_count = 0
    ui.start_time = time.time()

def next_level():
    global environment, ui
    elapsed = time.time() - ui.start_time
    level_score = ui.calculate_score(environment.current_level, elapsed, environment.collision_count)
    ui.score += level_score
    if environment.current_level < 4:
        environment.current_level += 1
        reset_level()
    else:
        ui.game_state = "WIN"

def reset_game():
    global environment, ui
    environment.current_level = 1
    environment.collision_count = 0
    ui.score = 0
    ui.game_state = "PLAYING"
    reset_level()


# INPUT HANDLERS

def keyboard_listener(key, x, y):
    global lights_on, doors_open, car_model, current_model_index, keys

    if key == b'h' or key == b'H':
        lights_on = not lights_on
    elif key == b'j' or key == b'J':
        doors_open = not doors_open
    elif key == b'v' or key == b'V':
        config = environment.get_level_config()
        at_start = (abs(car.x - config['start_pos'][0]) < 50 and
                   abs(car.y - config['start_pos'][1]) < 50)
        if at_start:
            current_model_index = (current_model_index + 1) % len(car_models)
            car_model = car_models[current_model_index]
    elif key == b'c' or key == b'C':
        camera.cycle_mode()
    elif key == b'r' or key == b'R':
        # Restart current level
        reset_level()
        ui.game_state = "PLAYING"
    elif key == b't' or key == b'T':
        # Reset entire game
        reset_game()
    elif key == b' ':
        if ui.game_state == "START":
            ui.game_state = "PLAYING"
            ui.reset_timer()
        elif ui.game_state == "PLAYING" and environment.parked_successfully:
            next_level()
    elif key == b'\x1b':
        glutLeaveMainLoop()

def special_key_listener(key, x, y):
    global keys
    if key == GLUT_KEY_UP:
        keys['forward'] = True
    elif key == GLUT_KEY_DOWN:
        keys['backward'] = True
        if car.speed > 0.5:
            keys['brake'] = True
    elif key == GLUT_KEY_LEFT:
        keys['left'] = True
    elif key == GLUT_KEY_RIGHT:
        keys['right'] = True

def special_key_up_listener(key, x, y):
    global keys
    if key == GLUT_KEY_UP:
        keys['forward'] = False
    elif key == GLUT_KEY_DOWN:
        keys['backward'] = False
        keys['brake'] = False
    elif key == GLUT_KEY_LEFT:
        keys['left'] = False
    elif key == GLUT_KEY_RIGHT:
        keys['right'] = False

def mouse_listener(button, state, x, y):
    global mouse_x, mouse_y
    if button == 3:
        camera.mouse_zoom(-1)
    elif button == 4:
        camera.mouse_zoom(1)
    if state == GLUT_DOWN:
        mouse_x, mouse_y = x, y

def motion_listener(x, y):
    global mouse_x, mouse_y
    dx = x - mouse_x
    dy = y - mouse_y
    camera.mouse_rotate(dx, dy)
    mouse_x, mouse_y = x, y


# MAIN LOOP

def idle():
    global steering_angle

    # update game logic
    if ui.game_state == "PLAYING":
        # Update car physics
        car.update(keys['forward'], keys['backward'], keys['left'], keys['right'], keys['brake'])
        if keys['left']:
            steering_angle = min(steering_angle + 5, 45)
        elif keys['right']:
            steering_angle = max(steering_angle - 5, -45)
        else:
            steering_angle *= 0.8
        # Check for collisions
        if environment.check_collision(car):
            car.stop()
            # Check if collision limit exceeded
            if environment.collision_count >= ui.max_collisions:
                ui.game_state = "GAME_OVER"
        # Check if parked successfully
        environment.check_parking_success(car)
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    camera.setup_camera(car)
    config = environment.get_level_config()
    draw_environment(config)
    draw_parking_spot(config['parking_spot'], config['parking_size'])
    draw_car(car, lights_on, doors_open, car_model, steering_angle)
    if camera.mode == "FIRST_PERSON":
        draw_dashboard(car, steering_angle)
    if ui.game_state == "START":
        ui.draw_start_screen()
    elif ui.game_state == "PLAYING":
        ui.draw_hud(car, environment, camera)
    elif ui.game_state == "GAME_OVER":
        ui.draw_game_over_screen(environment)
    elif ui.game_state == "WIN":
        ui.draw_win_screen(environment)
    glutSwapBuffers()


# MAIN
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Parking Simulator")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutSpecialUpFunc(special_key_up_listener)
    glutMouseFunc(mouse_listener)
    glutMotionFunc(motion_listener)
    reset_level()
    glutMainLoop()

if __name__ == "__main__":
    main()