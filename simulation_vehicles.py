import random
import math
from background_element import BackgroundElement

class SimulationVehicle(BackgroundElement):
    def __init__(self, x, y, vehicle_type="sedan", direction="right"):
        self.vehicle_type = vehicle_type
        self.direction = direction
        
        width, height = self.get_vehicle_dimensions(vehicle_type, direction)
        super().__init__(x, y, width, height)
        
        self.element_type = "simulation_vehicle"
        self.set_depth(-86)
        self.add_tag("simulation_vehicle")
        self.add_tag("simulator_ui")
        
        self.vehicle_colors = self.get_vehicle_colors(vehicle_type)
        self.set_color(self.vehicle_colors['body'])
        
        self.max_speed = random.uniform(80, 150)
        self.current_speed = self.max_speed
        self.acceleration = 50.0
        self.deceleration = 100.0
        
        if direction == "right":
            self.set_velocity(self.current_speed, 0)
        elif direction == "left":
            self.set_velocity(-self.current_speed, 0)
        elif direction == "down":
            self.set_velocity(0, self.current_speed)
        elif direction == "up":
            self.set_velocity(0, -self.current_speed)
        
        self.canvas_items = []
        self.clip_bounds = None
    
    def get_vehicle_dimensions(self, vehicle_type, direction):
        base_dimensions = {
            'compact': (40, 25),
            'sedan': (50, 25),
            'suv': (55, 25),
            'coupe': (45, 25),
            'van': (65, 25),
            'pickup': (60, 25),
            'bus': (80, 25),
            'truck': (70, 25),
            'semi': (90, 25),
            'motorcycle': (30, 25)
        }
        
        base_width, base_height = base_dimensions.get(vehicle_type, (50, 25))
        
        if direction in ["right", "left"]:
            return (base_width, base_height)
        else:
            return (base_height, base_width)
    
    def get_vehicle_colors(self, vehicle_type):
        color_palettes = [
            {'body': '#E53935', 'details': '#B71C1C', 'windows': '#1E88E5'},
            {'body': '#1E88E5', 'details': '#0D47A1', 'windows': '#81D4FA'},
            {'body': '#43A047', 'details': '#1B5E20', 'windows': '#A5D6A7'},
            {'body': '#FDD835', 'details': '#F9A825', 'windows': '#FFF59D'},
            {'body': '#FB8C00', 'details': '#E65100', 'windows': '#FFE0B2'},
            {'body': '#8E24AA', 'details': '#4A148C', 'windows': '#CE93D8'},
            {'body': '#00ACC1', 'details': '#006064', 'windows': '#B2EBF2'},
            {'body': '#212121', 'details': '#000000', 'windows': '#616161'},
            {'body': '#FFFFFF', 'details': '#BDBDBD', 'windows': '#E0E0E0'},
            {'body': '#6D4C41', 'details': '#3E2723', 'windows': '#A1887F'},
            {'body': '#F06292', 'details': '#C2185B', 'windows': '#F8BBD0'},
            {'body': '#9575CD', 'details': '#512DA8', 'windows': '#D1C4E9'},
            {'body': '#4DD0E1', 'details': '#00838F', 'windows': '#B2EBF2'},
            {'body': '#AED581', 'details': '#558B2F', 'windows': '#DCEDC8'},
            {'body': '#FF8A65', 'details': '#D84315', 'windows': '#FFCCBC'}
        ]
        
        return random.choice(color_palettes)
    
    def update(self, delta_time):
        if not self.active:
            return

        if self.direction == "right":
            self.set_velocity(self.current_speed, 0)
        elif self.direction == "left":
            self.set_velocity(-self.current_speed, 0)
        elif self.direction == "down":
            self.set_velocity(0, self.current_speed)
        elif self.direction == "up":
            self.set_velocity(0, -self.current_speed)

        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
    
    def deactivate(self):
        super().deactivate()
        self.cleanup_canvas_items()
    
    def cleanup_canvas_items(self):
        if hasattr(self, 'canvas_items') and self.canvas_items:
            for item_id in self.canvas_items:
                try:
                    if hasattr(self, 'canvas') and self.canvas:
                        self.canvas.delete(item_id)
                except:
                    pass
            self.canvas_items.clear()
    
    def set_canvas(self, canvas):
        self.canvas = canvas
    
    def set_clip_bounds(self, bounds):
        self.clip_bounds = bounds
    
    def is_in_clip_bounds(self, x, y, width, height):
        if not self.clip_bounds:
            return True
        
        right = x + width
        bottom = y + height
        
        if right < self.clip_bounds['left'] or x > self.clip_bounds['right']:
            return False
        if bottom < self.clip_bounds['top'] or y > self.clip_bounds['bottom']:
            return False
        
        return True
    
    def draw(self, canvas):
        if not hasattr(self, 'canvas') or self.canvas is None:
            self.canvas = canvas
        
        if not self.visible or self.opacity <= 0.01:
            if hasattr(self, 'canvas_items') and self.canvas_items:
                for item_id in self.canvas_items:
                    try:
                        canvas.itemconfig(item_id, state='hidden')
                    except:
                        pass
            return
        
        final_x = self.x + self.offset_x
        final_y = self.y + self.offset_y
        
        if self.clip_bounds:
            vehicle_left = final_x
            vehicle_right = final_x + self.width
            vehicle_top = final_y
            vehicle_bottom = final_y + self.height
            
            if (vehicle_right < self.clip_bounds['left'] or 
                vehicle_left > self.clip_bounds['right'] or
                vehicle_bottom < self.clip_bounds['top'] or 
                vehicle_top > self.clip_bounds['bottom']):
                
                if hasattr(self, 'canvas_items') and self.canvas_items:
                    for item_id in self.canvas_items:
                        try:
                            canvas.itemconfig(item_id, state='hidden')
                        except:
                            pass
                return
        
        if not hasattr(self, 'canvas_items') or not self.canvas_items:
            self.canvas_items = self.create_vehicle_visual(canvas, final_x, final_y)
        else:
            self.update_vehicle_position(canvas, final_x, final_y)
        
        if hasattr(self, 'canvas_items') and self.canvas_items:
            for item_id in self.canvas_items:
                try:
                    canvas.itemconfig(item_id, state='normal')
                except:
                    pass
    
    def create_vehicle_visual(self, canvas, x, y):
        items = []
        
        if self.direction in ["right", "left"]:
            items.extend(self.draw_horizontal_vehicle(canvas, x, y))
        else:
            items.extend(self.draw_vertical_vehicle(canvas, x, y))
        
        return items
    
    def draw_horizontal_vehicle(self, canvas, x, y):
        items = []
        colors = self.vehicle_colors
        
        body = canvas.create_rectangle(
            int(x), int(y),
            int(x + self.width), int(y + self.height),
            fill=colors['body'], outline='#000000', width=1,
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(body)
        
        if self.direction == "right":
            window_x1 = x + self.width * 0.6
            window_x2 = x + self.width * 0.95
            light_x = x + self.width - 3
        else:
            window_x1 = x + self.width * 0.05
            window_x2 = x + self.width * 0.4
            light_x = x + 3
        
        windshield = canvas.create_rectangle(
            int(window_x1), int(y + 4),
            int(window_x2), int(y + self.height - 4),
            fill=colors['windows'], outline='#000000', width=1,
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(windshield)
        
        light = canvas.create_oval(
            int(light_x - 2), int(y + self.height // 2 - 3),
            int(light_x + 2), int(y + self.height // 2 + 3),
            fill='#FFFF88', outline='',
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(light)
        
        return items
    
    def draw_vertical_vehicle(self, canvas, x, y):
        items = []
        colors = self.vehicle_colors
        
        body = canvas.create_rectangle(
            int(x), int(y),
            int(x + self.width), int(y + self.height),
            fill=colors['body'], outline='#000000', width=1,
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(body)
        
        if self.direction == "down":
            window_y1 = y + self.height * 0.6
            window_y2 = y + self.height * 0.95
            light_y = y + self.height - 3
        else:
            window_y1 = y + self.height * 0.05
            window_y2 = y + self.height * 0.4
            light_y = y + 3
        
        windshield = canvas.create_rectangle(
            int(x + 4), int(window_y1),
            int(x + self.width - 4), int(window_y2),
            fill=colors['windows'], outline='#000000', width=1,
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(windshield)
        
        light = canvas.create_oval(
            int(x + self.width // 2 - 3), int(light_y - 2),
            int(x + self.width // 2 + 3), int(light_y + 2),
            fill='#FFFF88', outline='',
            tags=('simulator_ui', 'simulation_vehicle', 'vehicle_layer')
        )
        items.append(light)
        
        return items
    
    def update_vehicle_position(self, canvas, x, y):
        if not self.canvas_items:
            return
        
        dx = x - (self.original_x if hasattr(self, 'original_x') else self.x)
        dy = y - (self.original_y if hasattr(self, 'original_y') else self.y)
        
        for item_id in self.canvas_items:
            try:
                canvas.move(item_id, dx, dy)
            except:
                pass
        
        self.original_x = x
        self.original_y = y


class SimulationVehicleManager:
    def __init__(self, canvas, sim_area_x, sim_area_y, sim_area_width, sim_area_height):
        self.canvas = canvas
        self.sim_area_x = sim_area_x
        self.sim_area_y = sim_area_y
        self.sim_area_width = sim_area_width
        self.sim_area_height = sim_area_height
        
        self.clip_bounds = {
            'left': sim_area_x,
            'right': sim_area_x + sim_area_width,
            'top': sim_area_y,
            'bottom': sim_area_y + sim_area_height
        }
        
        self.vehicles = []
        self.max_vehicles_per_lane = 5
        
        self.spawn_cooldowns = {
            'horizontal_bottom': 0,
            'horizontal_top': 0,
            'vertical_left': 0,
            'vertical_right': 0
        }
        
        self.spawn_interval = 2.0
        
        self.vehicle_types = [
            'compact', 'sedan', 'suv', 'coupe', 'van',
            'pickup', 'bus', 'truck', 'semi', 'motorcycle'
        ]
        
        center_x = sim_area_x + sim_area_width // 2
        center_y = sim_area_y + sim_area_height // 2
        road_width = 100
        
        self.lane_positions = {
            'horizontal_bottom': center_y + road_width // 4,
            'horizontal_top': center_y - road_width // 4,
            'vertical_left': center_x - road_width // 4,
            'vertical_right': center_x + road_width // 4
        }
    
    def update(self, delta_time):
        # Handle spawning new vehicles
        for lane in self.spawn_cooldowns:
            self.spawn_cooldowns[lane] -= delta_time
        
        for lane in ['horizontal_bottom', 'horizontal_top', 'vertical_left', 'vertical_right']:
            lane_vehicles = [v for v in self.vehicles if v.has_tag(lane)]
            
            if self.spawn_cooldowns[lane] <= 0 and len(lane_vehicles) < self.max_vehicles_per_lane:
                new_vehicle = self.spawn_vehicle(lane)
                if new_vehicle:
                    self.vehicles.append(new_vehicle)
                    self.spawn_cooldowns[lane] = self.spawn_interval
        
        # Adjust speeds for all vehicles based on their leaders
        self.adjust_vehicle_speeds(delta_time)

        # Update, draw, and manage lifecycle of each vehicle
        for vehicle in self.vehicles[:]:
            if not vehicle.is_active():
                vehicle.cleanup_canvas_items()
                self.vehicles.remove(vehicle)
                continue

            vehicle.update(delta_time)
            vehicle.draw(self.canvas)

            if self.is_vehicle_completely_out_of_bounds(vehicle):
                vehicle.deactivate()
                vehicle.cleanup_canvas_items()
                self.vehicles.remove(vehicle)

    def adjust_vehicle_speeds(self, delta_time):
        leaders = {}
        lanes = {
            'horizontal_bottom': [], 'horizontal_top': [],
            'vertical_left': [], 'vertical_right': []
        }
        for v in self.vehicles:
            for lane_tag in lanes:
                if v.has_tag(lane_tag):
                    lanes[lane_tag].append(v)
                    break

        lane_list = sorted(lanes['horizontal_bottom'], key=lambda v: v.x)
        for i in range(len(lane_list) - 1):
            leaders[lane_list[i]] = lane_list[i+1]

        lane_list = sorted(lanes['horizontal_top'], key=lambda v: v.x)
        for i in range(len(lane_list) - 1):
            leaders[lane_list[i+1]] = lane_list[i]

        lane_list = sorted(lanes['vertical_left'], key=lambda v: v.y)
        for i in range(len(lane_list) - 1):
            leaders[lane_list[i]] = lane_list[i+1]

        lane_list = sorted(lanes['vertical_right'], key=lambda v: v.y)
        for i in range(len(lane_list) - 1):
            leaders[lane_list[i+1]] = lane_list[i]

        safe_distance_margin = 25.0
        for vehicle in self.vehicles:
            leader = leaders.get(vehicle)

            if leader:
                if vehicle.direction == 'right':
                    distance = leader.x - (vehicle.x + vehicle.width)
                elif vehicle.direction == 'left':
                    distance = vehicle.x - (leader.x + leader.width)
                elif vehicle.direction == 'down':
                    distance = leader.y - (vehicle.y + vehicle.height)
                else:
                    distance = vehicle.y - (leader.y + leader.height)

                if distance < safe_distance_margin:
                    vehicle.current_speed = max(0, vehicle.current_speed - vehicle.deceleration * delta_time)
                elif distance < safe_distance_margin * 2 and vehicle.current_speed > leader.current_speed:
                    vehicle.current_speed = max(leader.current_speed, vehicle.current_speed - vehicle.deceleration * delta_time * 0.5)
                else:
                    vehicle.current_speed = min(vehicle.max_speed, vehicle.current_speed + vehicle.acceleration * delta_time)
            else:
                vehicle.current_speed = min(vehicle.max_speed, vehicle.current_speed + vehicle.acceleration * delta_time)
    
    def is_vehicle_completely_out_of_bounds(self, vehicle):
        margin = 10
        
        if vehicle.direction == "right":
            return vehicle.x > self.sim_area_x + self.sim_area_width + margin
        elif vehicle.direction == "left":
            return vehicle.x + vehicle.width < self.sim_area_x - margin
        elif vehicle.direction == "down":
            return vehicle.y > self.sim_area_y + self.sim_area_height + margin
        elif vehicle.direction == "up":
            return vehicle.y + vehicle.height < self.sim_area_y - margin
        
        return False
    
    def spawn_vehicle(self, lane):
        vehicle_type = random.choice(self.vehicle_types)
        
        if lane == 'horizontal_bottom':
            direction = 'right'
            x = self.sim_area_x - 100
            y = self.lane_positions['horizontal_bottom']
        elif lane == 'horizontal_top':
            direction = 'left'
            x = self.sim_area_x + self.sim_area_width + 100
            y = self.lane_positions['horizontal_top']
        elif lane == 'vertical_left':
            direction = 'down'
            x = self.lane_positions['vertical_left']
            y = self.sim_area_y - 100
        else:
            direction = 'up'
            x = self.lane_positions['vertical_right']
            y = self.sim_area_y + self.sim_area_height + 100
        
        new_vehicle = SimulationVehicle(x, y, vehicle_type, direction)

        safe_spawn_margin = 15.0
        lane_vehicles = [v for v in self.vehicles if v.has_tag(lane)]

        for other in lane_vehicles:
            if direction in ['right', 'left']:
                dist = abs(new_vehicle.x - other.x)
                min_safe_dist = (new_vehicle.width + other.width) / 2 + safe_spawn_margin
                if dist < min_safe_dist:
                    new_vehicle.deactivate()
                    return None
            else:
                dist = abs(new_vehicle.y - other.y)
                min_safe_dist = (new_vehicle.height + other.height) / 2 + safe_spawn_margin
                if dist < min_safe_dist:
                    new_vehicle.deactivate()
                    return None
        
        new_vehicle.activate()
        new_vehicle.show()
        new_vehicle.add_tag(lane)
        new_vehicle.set_clip_bounds(self.clip_bounds)
        
        return new_vehicle
    
    def clear_all(self):
        for vehicle in self.vehicles[:]:
            vehicle.deactivate()
            vehicle.cleanup_canvas_items()
        self.vehicles.clear()
    
    def get_vehicles(self):
        return self.vehicles