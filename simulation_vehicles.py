import random
import math
from background_element import BackgroundElement

class SimulationVehicle(BackgroundElement):
    def __init__(self, vehicle_type, lane, direction):
        self.vehicle_type = vehicle_type
        self.lane = lane
        self.direction = direction
        
        width, height = self.get_vehicle_dimensions(vehicle_type, lane)
        super().__init__(0, 0, width, height)
        
        self.element_type = "simulation_vehicle"
        self.set_depth(-86)
        self.add_tag("simulation_vehicle")
        self.add_tag("simulator_ui")
        self.add_tag(lane)
        
        self.vehicle_colors = self.get_vehicle_colors(vehicle_type)
        self.set_color(self.vehicle_colors['body'])
        
        self.base_speed = self.get_random_speed()
        self.current_speed = self.base_speed
        self.target_speed = self.base_speed
        
        if 'horizontal' in lane:
            if direction > 0:
                self.set_velocity(self.base_speed, 0)
            else:
                self.set_velocity(-self.base_speed, 0)
        else:
            if direction > 0:
                self.set_velocity(0, self.base_speed)
            else:
                self.set_velocity(0, -self.base_speed)
        
        self.vehicle_color = self.get_random_vehicle_color()
        self.set_color(self.vehicle_color)
        
        self.canvas_items = []
        self.clip_bounds = None
        
        self.safe_distance = self.width * 2.0
        self.deceleration_distance = self.width * 5.0
        self.acceleration_distance = self.width * 7.0
    
    def get_vehicle_dimensions(self, vehicle_type, lane):
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
        
        if 'horizontal' in lane:
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
    
    def get_random_vehicle_color(self):
        colors = [
            '#E53935', '#1E88E5', '#43A047', '#FDD835', '#FB8C00',
            '#8E24AA', '#00ACC1', '#212121', '#FFFFFF', '#6D4C41',
            '#F06292', '#9575CD', '#4DD0E1', '#AED581', '#FF8A65'
        ]
        return random.choice(colors)
    
    def get_random_speed(self):
        speeds = [90, 110, 130, 150, 170]
        return random.choice(speeds)
    
    def custom_update(self, delta_time):
        if self.current_speed != self.target_speed:
            speed_diff = self.target_speed - self.current_speed
            acceleration_rate = 3.0 if speed_diff > 0 else 4.0
            adjustment = speed_diff * delta_time * acceleration_rate
            
            if abs(adjustment) > abs(speed_diff):
                self.current_speed = self.target_speed
            else:
                self.current_speed += adjustment
            
            if 'horizontal' in self.lane:
                if self.direction > 0:
                    self.set_velocity(self.current_speed, 0)
                else:
                    self.set_velocity(-self.current_speed, 0)
            else:
                if self.direction > 0:
                    self.set_velocity(0, self.current_speed)
                else:
                    self.set_velocity(0, -self.current_speed)
    
    def adjust_speed_for_traffic(self, distance, other_vehicle):
        if distance is None or other_vehicle is None:
            self.target_speed = self.base_speed
            return
        
        if distance < self.safe_distance:
            self.target_speed = max(other_vehicle.current_speed * 0.85, 40)
        elif distance < self.deceleration_distance:
            ratio = distance / self.deceleration_distance
            target = other_vehicle.current_speed + (self.base_speed - other_vehicle.current_speed) * ratio
            self.target_speed = min(self.base_speed, max(target, 50))
        elif distance < self.acceleration_distance:
            ratio = (distance - self.deceleration_distance) / (self.acceleration_distance - self.deceleration_distance)
            self.target_speed = other_vehicle.current_speed + (self.base_speed - other_vehicle.current_speed) * ratio
        else:
            self.target_speed = self.base_speed
    
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
        
        if 'horizontal' in self.lane:
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
        
        if self.direction > 0:
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
        
        if self.direction > 0:
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
    def __init__(self, sim_area_x, sim_area_y, sim_area_width, sim_area_height):
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
        
        self.lane_directions = {
            'horizontal_bottom': 1,
            'horizontal_top': -1,
            'vertical_left': 1,
            'vertical_right': -1
        }
    
    def update(self, delta_time):
        for lane in self.spawn_cooldowns:
            self.spawn_cooldowns[lane] -= delta_time
        
        for lane in ['horizontal_bottom', 'horizontal_top', 'vertical_left', 'vertical_right']:
            lane_vehicles = [v for v in self.vehicles if v.has_tag(lane)]
            
            if self.spawn_cooldowns[lane] <= 0 and len(lane_vehicles) < self.max_vehicles_per_lane:
                spawned = self.spawn_vehicle(lane)
                if spawned:
                    self.spawn_cooldowns[lane] = self.spawn_interval
        
        vehicles_by_lane = {
            'horizontal_bottom': [],
            'horizontal_top': [],
            'vertical_left': [],
            'vertical_right': []
        }
        
        for vehicle in self.vehicles[:]:
            if not vehicle.is_active():
                vehicle.cleanup_canvas_items()
                self.vehicles.remove(vehicle)
            else:
                if self.is_vehicle_completely_out_of_bounds(vehicle):
                    vehicle.deactivate()
                    vehicle.cleanup_canvas_items()
                    self.vehicles.remove(vehicle)
                else:
                    for lane in vehicles_by_lane.keys():
                        if vehicle.has_tag(lane):
                            vehicles_by_lane[lane].append(vehicle)
                            break
        
        for lane, lane_vehicles in vehicles_by_lane.items():
            lane_vehicles.sort(key=lambda v: v.x if 'horizontal' in lane else v.y)
            
            for i, vehicle in enumerate(lane_vehicles):
                vehicle_ahead = None
                min_distance = float('inf')
                
                for other in lane_vehicles:
                    if other == vehicle:
                        continue
                    
                    if 'horizontal_bottom' in lane:
                        if other.x > vehicle.x:
                            distance = other.x - (vehicle.x + vehicle.width)
                            if distance < min_distance:
                                min_distance = distance
                                vehicle_ahead = other
                    elif 'horizontal_top' in lane:
                        if other.x < vehicle.x:
                            distance = vehicle.x - (other.x + other.width)
                            if distance < min_distance:
                                min_distance = distance
                                vehicle_ahead = other
                    elif 'vertical_left' in lane:
                        if other.y > vehicle.y:
                            distance = other.y - (vehicle.y + vehicle.height)
                            if distance < min_distance:
                                min_distance = distance
                                vehicle_ahead = other
                    elif 'vertical_right' in lane:
                        if other.y < vehicle.y:
                            distance = vehicle.y - (other.y + other.height)
                            if distance < min_distance:
                                min_distance = distance
                                vehicle_ahead = other
                
                if vehicle_ahead:
                    vehicle.adjust_speed_for_traffic(min_distance, vehicle_ahead)
                else:
                    vehicle.adjust_speed_for_traffic(None, None)
    
    def is_vehicle_completely_out_of_bounds(self, vehicle):
        margin = 10
        
        if 'horizontal_bottom' in vehicle.lane:
            return vehicle.x > self.sim_area_x + self.sim_area_width + margin
        elif 'horizontal_top' in vehicle.lane:
            return vehicle.x + vehicle.width < self.sim_area_x - margin
        elif 'vertical_left' in vehicle.lane:
            return vehicle.y > self.sim_area_y + self.sim_area_height + margin
        elif 'vertical_right' in vehicle.lane:
            return vehicle.y + vehicle.height < self.sim_area_y - margin
        
        return False
    
    def spawn_vehicle(self, lane):
        vehicle_type = random.choice(self.vehicle_types)
        direction = self.lane_directions[lane]
        
        vehicle = SimulationVehicle(vehicle_type, lane, direction)
        
        if 'horizontal_bottom' in lane:
            x = self.sim_area_x - vehicle.width - 50
            y = self.lane_positions['horizontal_bottom'] - vehicle.height // 2
        elif 'horizontal_top' in lane:
            x = self.sim_area_x + self.sim_area_width + 50
            y = self.lane_positions['horizontal_top'] - vehicle.height // 2
        elif 'vertical_left' in lane:
            x = self.lane_positions['vertical_left'] - vehicle.width // 2
            y = self.sim_area_y - vehicle.height - 50
        else:
            x = self.lane_positions['vertical_right'] - vehicle.width // 2
            y = self.sim_area_y + self.sim_area_height + 50
        
        lane_vehicles = [v for v in self.vehicles if v.has_tag(lane)]
        
        if not self.check_spawn_collision(x, y, vehicle.width, vehicle.height, lane_vehicles, direction):
            return None
        
        vehicle.x = x
        vehicle.y = y
        vehicle.original_x = x
        vehicle.original_y = y
        vehicle.activate()
        vehicle.show()
        vehicle.set_clip_bounds(self.clip_bounds)
        
        self.vehicles.append(vehicle)
        
        return vehicle
    
    def check_spawn_collision(self, spawn_x, spawn_y, vehicle_width, vehicle_height, lane_vehicles, direction):
        min_gap = 250
    
        for vehicle in lane_vehicles:
            if not vehicle.is_active():
                continue
            
            if direction > 0:
                distance_ahead = vehicle.x - (spawn_x + vehicle_width)
                if distance_ahead < min_gap and distance_ahead > -vehicle_width:
                    return False
            else:
                distance_ahead = spawn_x - (vehicle.x + vehicle.width)
                if distance_ahead < min_gap and distance_ahead > -vehicle_width:
                    return False
    
        return True
    
    def clear_all(self):
        for vehicle in self.vehicles[:]:
            vehicle.deactivate()
            vehicle.cleanup_canvas_items()
        self.vehicles.clear()
    
    def get_vehicles(self):
        return self.vehicles
