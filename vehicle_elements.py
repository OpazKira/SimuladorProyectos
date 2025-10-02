import random
import math
from background_element import BackgroundElement

class VehicleElement(BackgroundElement):
    def __init__(self, vehicle_type, lane, direction):
        self.vehicle_type = vehicle_type
        self.lane = lane
        self.direction = direction
    
        width, height = self.get_vehicle_dimensions(vehicle_type)
        super().__init__(0, 0, width, height)
    
        self.element_type = "vehicle"
    
        if direction > 0:
            self.set_depth(-78)
        else:
            self.set_depth(-79)
    
        self.add_tag("vehicle")
        self.add_tag(f"lane_{lane}")
    
        self.base_speed = self.get_random_speed()
        self.current_speed = self.base_speed
        self.target_speed = self.base_speed
    
        self.set_velocity(self.base_speed * direction, 0)
    
        self.vehicle_color = self.get_random_vehicle_color()
        self.set_color(self.vehicle_color)
    
        self.canvas_items = []
        self.clip_bounds = None
    
        self.safe_distance = self.width * 2.5
        self.deceleration_distance = self.width * 4.5
        
    def get_vehicle_dimensions(self, vehicle_type):
        dimensions = {
            'compact': (40, 18),
            'sedan': (55, 20),
            'suv': (65, 24),
            'van': (70, 26),
            'pickup': (70, 24),
            'truck': (85, 28),
            'semi': (110, 30),
            'bus': (95, 28),
            'delivery': (60, 26),
            'box_truck': (80, 30),
            'flatbed': (90, 26)
        }
        return dimensions.get(vehicle_type, (55, 20))
    
    def get_random_speed(self):
        speeds = [80, 100, 120, 140, 160]
        return random.choice(speeds)
    
    def get_random_vehicle_color(self):
        colors = [
            '#FF4444', '#4444FF', '#44FF44', '#FFFF44', '#FF44FF',
            '#44FFFF', '#FF8844', '#8844FF', '#FFFFFF', '#222222',
            '#888888', '#CC0000', '#0000CC', '#00CC00', '#666666',
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
        ]
        return random.choice(colors)
    
    def custom_update(self, delta_time):
        if self.current_speed != self.target_speed:
            speed_diff = self.target_speed - self.current_speed
            adjustment = speed_diff * delta_time * 2.0
            self.current_speed += adjustment
            
            if abs(self.current_speed - self.target_speed) < 1:
                self.current_speed = self.target_speed
            
            self.set_velocity(self.current_speed * self.direction, 0)
        
        screen_width = 1920
        if self.direction > 0:
            if self.x > screen_width + 100:
                self.deactivate()
        else:
            if self.x < -self.width - 100:
                self.deactivate()
    
    def check_collision_ahead(self, vehicles_in_lane):
        closest_distance = None
        closest_vehicle = None
    
        for other in vehicles_in_lane:
            if other == self or not other.is_active():
                continue
        
            if self.direction > 0:
                if other.x > self.x:
                    distance = other.x - (self.x + self.width)
                    if distance < self.deceleration_distance:
                        if closest_distance is None or distance < closest_distance:
                            closest_distance = distance
                            closest_vehicle = other
            else:
                if other.x < self.x:
                    distance = self.x - (other.x + other.width)
                    if distance < self.deceleration_distance:
                        if closest_distance is None or distance < closest_distance:
                            closest_distance = distance
                            closest_vehicle = other
    
        return closest_distance, closest_vehicle
    
    def adjust_speed_for_traffic(self, distance, other_vehicle):
        if distance is None or other_vehicle is None:
            self.target_speed = self.base_speed
            return
    
        if distance < self.safe_distance:
            self.target_speed = max(other_vehicle.current_speed * 0.90, 50)
        elif distance < self.deceleration_distance:
            ratio = distance / self.deceleration_distance
            max_safe_speed = min(self.base_speed, other_vehicle.current_speed + 10)
            self.target_speed = min(
                max_safe_speed,
                other_vehicle.current_speed + (max_safe_speed - other_vehicle.current_speed) * ratio
            )
        else:
            self.target_speed = self.base_speed
    
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
        
        # CLIPPING: Los vehiculos del fondo NO necesitan clipping
        # Solo los vehiculos de simulacion (SimulationVehicle) necesitan clipping
        # Los vehiculos del fondo deben ser visibles en toda la pantalla
        
        # Crear o actualizar vehiculo
        if not hasattr(self, 'canvas_items') or not self.canvas_items:
            self.canvas_items = self.create_vehicle_visual(canvas, final_x, final_y)
        else:
            self.update_vehicle_position(canvas, final_x, final_y)
        
        # Asegurar que todos los items esten visibles
        if hasattr(self, 'canvas_items') and self.canvas_items:
            for item_id in self.canvas_items:
                try:
                    canvas.itemconfig(item_id, state='normal')
                except:
                    pass
    
    def create_vehicle_visual(self, canvas, x, y):
        items = []
        
        if self.vehicle_type == 'bus':
            items.extend(self.draw_bus(canvas, x, y))
        elif self.vehicle_type == 'delivery':
            items.extend(self.draw_delivery_van(canvas, x, y))
        elif self.vehicle_type == 'box_truck':
            items.extend(self.draw_box_truck(canvas, x, y))
        elif self.vehicle_type == 'flatbed':
            items.extend(self.draw_flatbed_truck(canvas, x, y))
        elif self.vehicle_type == 'semi':
            items.extend(self.draw_semi_truck(canvas, x, y))
        elif self.vehicle_type == 'truck':
            items.extend(self.draw_pickup_truck(canvas, x, y))
        elif self.vehicle_type == 'pickup':
            items.extend(self.draw_pickup_truck(canvas, x, y))
        else:
            items.extend(self.draw_standard_vehicle(canvas, x, y))
        
        return items
    
    def draw_standard_vehicle(self, canvas, x, y):
        items = []
        
        body_id = canvas.create_rectangle(
            int(x), int(y),
            int(x + self.width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(body_id)
        
        if self.vehicle_type in ['sedan', 'suv', 'van', 'compact']:
            cabin_height = self.height * 0.4
            cabin_width = self.width * 0.5
            cabin_x = x + self.width * 0.25
            
            cabin_id = canvas.create_rectangle(
                int(cabin_x), int(y - cabin_height),
                int(cabin_x + cabin_width), int(y),
                fill=self.vehicle_color,
                outline='#000000',
                width=1,
                tags=('background_layer', 'vehicle')
            )
            items.append(cabin_id)
            
            window_color = '#87CEEB'
            window_margin = 2
            window_id = canvas.create_rectangle(
                int(cabin_x + window_margin), int(y - cabin_height + window_margin),
                int(cabin_x + cabin_width - window_margin), int(y - window_margin),
                fill=window_color,
                outline='',
                tags=('background_layer', 'vehicle')
            )
            items.append(window_id)
        
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
        
        return items
    
    def draw_bus(self, canvas, x, y):
        items = []
        
        body_id = canvas.create_rectangle(
            int(x), int(y),
            int(x + self.width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(body_id)
        
        window_height = self.height * 0.5
        window_y = y + self.height * 0.15
        window_width = self.width / 5
        window_spacing = self.width / 5
        
        for i in range(4):
            window_x = x + window_spacing * i + 10
            window_id = canvas.create_rectangle(
                int(window_x), int(window_y),
                int(window_x + window_width - 8), int(window_y + window_height),
                fill='#87CEEB',
                outline='#000000',
                width=1,
                tags=('background_layer', 'vehicle')
            )
            items.append(window_id)
        
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
        
        return items
    
    def draw_delivery_van(self, canvas, x, y):
        items = []
    
        cabin_width = self.width * 0.35
        box_width = self.width * 0.65
    
        if self.direction > 0:
            box_x = x
            cabin_x = x + box_width
        else:
            cabin_x = x
            box_x = x + cabin_width
    
        box_id = canvas.create_rectangle(
            int(box_x), int(y - self.height * 0.3),
            int(box_x + box_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(box_id)
    
        cabin_id = canvas.create_rectangle(
            int(cabin_x), int(y),
            int(cabin_x + cabin_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(cabin_id)
    
        window_margin = 3
        window_id = canvas.create_rectangle(
            int(cabin_x + window_margin), int(y + window_margin),
            int(cabin_x + cabin_width - window_margin), int(y + self.height * 0.5),
            fill='#87CEEB',
            outline='',
            tags=('background_layer', 'vehicle')
        )
        items.append(window_id)
    
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
    
        return items
    
    def draw_box_truck(self, canvas, x, y):
        items = []
    
        cabin_width = self.width * 0.3
        box_width = self.width * 0.7
    
        if self.direction > 0:
            box_x = x
            cabin_x = x + box_width
        else:
            cabin_x = x
            box_x = x + cabin_width
    
        box_height = self.height * 1.2
        box_id = canvas.create_rectangle(
            int(box_x), int(y - box_height),
            int(box_x + box_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(box_id)
    
        cabin_id = canvas.create_rectangle(
            int(cabin_x), int(y),
            int(cabin_x + cabin_width), int(y + self.height),
            fill='#444444',
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(cabin_id)
    
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
    
        return items
    
    def draw_flatbed_truck(self, canvas, x, y):
        items = []
        
        cabin_width = self.width * 0.25
        bed_width = self.width * 0.75
        
        if self.direction > 0:
            cabin_x = x
            bed_x = x + cabin_width
        else:
            bed_x = x
            cabin_x = x + bed_width
        
        bed_id = canvas.create_rectangle(
            int(bed_x), int(y + self.height * 0.3),
            int(bed_x + bed_width), int(y + self.height),
            fill='#8B4513',
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(bed_id)
        
        cabin_id = canvas.create_rectangle(
            int(cabin_x), int(y),
            int(cabin_x + cabin_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(cabin_id)
        
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
        
        return items
    
    def draw_semi_truck(self, canvas, x, y):
        items = []
    
        cabin_width = self.width * 0.3
        trailer_width = self.width * 0.7
    
        if self.direction > 0:
            trailer_x = x
            cabin_x = x + trailer_width
        else:
            cabin_x = x
            trailer_x = x + cabin_width
    
        trailer_height = self.height * 1.3
        trailer_id = canvas.create_rectangle(
            int(trailer_x), int(y - trailer_height),
            int(trailer_x + trailer_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(trailer_id)
    
        cabin_id = canvas.create_rectangle(
            int(cabin_x), int(y),
            int(cabin_x + cabin_width), int(y + self.height),
            fill='#444444',
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(cabin_id)
    
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
    
        return items
    
    def draw_pickup_truck(self, canvas, x, y):
        items = []
        
        cabin_width = self.width * 0.5
        bed_width = self.width * 0.5
        
        if self.direction > 0:
            cabin_x = x
            bed_x = x + cabin_width
        else:
            bed_x = x
            cabin_x = x + bed_width
        
        bed_id = canvas.create_rectangle(
            int(bed_x), int(y + self.height * 0.2),
            int(bed_x + bed_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(bed_id)
        
        cabin_height = self.height * 0.5
        cabin_id = canvas.create_rectangle(
            int(cabin_x), int(y - cabin_height),
            int(cabin_x + cabin_width), int(y + self.height),
            fill=self.vehicle_color,
            outline='#000000',
            width=1,
            tags=('background_layer', 'vehicle')
        )
        items.append(cabin_id)
        
        window_margin = 2
        window_id = canvas.create_rectangle(
            int(cabin_x + window_margin), int(y - cabin_height + window_margin),
            int(cabin_x + cabin_width - window_margin), int(y - window_margin),
            fill='#87CEEB',
            outline='',
            tags=('background_layer', 'vehicle')
        )
        items.append(window_id)
        
        items.extend(self.draw_wheels(canvas, x, y))
        items.extend(self.draw_lights(canvas, x, y))
        
        return items
    
    def draw_wheels(self, canvas, x, y):
        items = []
        wheel_radius = 3
        wheel_y = y + self.height - 2
        
        if self.direction > 0:
            wheel1_x = x + self.width * 0.2
            wheel2_x = x + self.width * 0.8
        else:
            wheel1_x = x + self.width * 0.2
            wheel2_x = x + self.width * 0.8
        
        wheel1_id = canvas.create_oval(
            int(wheel1_x - wheel_radius), int(wheel_y - wheel_radius),
            int(wheel1_x + wheel_radius), int(wheel_y + wheel_radius),
            fill='#222222',
            outline='#000000',
            tags=('background_layer', 'vehicle')
        )
        items.append(wheel1_id)
        
        wheel2_id = canvas.create_oval(
            int(wheel2_x - wheel_radius), int(wheel_y - wheel_radius),
            int(wheel2_x + wheel_radius), int(wheel_y + wheel_radius),
            fill='#222222',
            outline='#000000',
            tags=('background_layer', 'vehicle')
        )
        items.append(wheel2_id)
        
        return items
    
    def draw_lights(self, canvas, x, y):
        items = []
        
        if self.direction > 0:
            light_x = x + self.width - 5
        else:
            light_x = x + 2
        
        light_y = y + self.height * 0.5
        light_id = canvas.create_oval(
            int(light_x), int(light_y - 3),
            int(light_x + 6), int(light_y + 3),
            fill='#FFFF88',
            outline='',
            tags=('background_layer', 'vehicle')
        )
        items.append(light_id)
        
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


class VehicleSpawnManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        road_bottom = screen_height - 120
        road_height = 120
        road_top = road_bottom
        
        lane_lower_center = road_top + (road_height * 0.75)
        lane_upper_center = road_top + (road_height * 0.25)
        
        vehicle_avg_height = 22
        
        self.lane_positions = {
            'upper': lane_upper_center - vehicle_avg_height,
            'lower': lane_lower_center - vehicle_avg_height
        }
        
        self.lane_directions = {
            'upper': -1,
            'lower': 1
        }
        
        self.vehicle_types = ['compact', 'sedan', 'suv', 'van', 'pickup', 'truck', 'semi', 'bus', 'delivery', 'box_truck', 'flatbed']
        self.vehicle_weights = [0.15, 0.20, 0.15, 0.10, 0.10, 0.08, 0.05, 0.07, 0.05, 0.03, 0.02]
        
        self.max_vehicles_per_lane = 12
        self.max_total_vehicles = 20
        
        self.spawn_cooldown = {}
        self.min_spawn_interval = 2.0
        self.max_spawn_interval = 5.0
        
        self.active_vehicles = []
        
        import time
        current_time = time.time()
        for lane in ['upper', 'lower']:
            self.spawn_cooldown[lane] = current_time
    
    def update(self, delta_time, background_elements):
        import time
        current_time = time.time()
    
        self.active_vehicles = [v for v in background_elements if v.element_type == 'vehicle' and v.is_active()]
    
        for lane in ['upper', 'lower']:
            if current_time - self.spawn_cooldown[lane] < random.uniform(self.min_spawn_interval, self.max_spawn_interval):
                continue
        
            if self.can_spawn_vehicle(lane):
                vehicle = self.spawn_vehicle(lane)
                if vehicle:
                    self.spawn_cooldown[lane] = current_time
                    yield vehicle
    
        vehicles_by_lane = {'upper': [], 'lower': []}
        for vehicle in self.active_vehicles:
            if vehicle.has_tag('lane_upper'):
                vehicles_by_lane['upper'].append(vehicle)
            elif vehicle.has_tag('lane_lower'):
                vehicles_by_lane['lower'].append(vehicle)
    
        for vehicle in self.active_vehicles:
            vehicle_lane = 'upper' if vehicle.has_tag('lane_upper') else 'lower'
            distance, other = vehicle.check_collision_ahead(vehicles_by_lane[vehicle_lane])
            vehicle.adjust_speed_for_traffic(distance, other)
    
    def can_spawn_vehicle(self, lane):
        lane_vehicles = [v for v in self.active_vehicles if v.has_tag(f'lane_{lane}')]
        
        if len(lane_vehicles) >= self.max_vehicles_per_lane:
            return False
        
        if len(self.active_vehicles) >= self.max_total_vehicles:
            return False
        
        return True
    
    def spawn_vehicle(self, lane):
        vehicle_type = random.choices(self.vehicle_types, weights=self.vehicle_weights)[0]
    
        direction = self.lane_directions[lane]
        y_position = self.lane_positions[lane]
    
        vehicle = VehicleElement(vehicle_type, lane, direction)
    
        if direction > 0:
            spawn_x = -vehicle.width - 50
        else:
            spawn_x = self.screen_width + 50
    
        if not self.check_spawn_collision(spawn_x, y_position, vehicle.width, vehicle.height, lane):
            return None
    
        vehicle.x = spawn_x
        vehicle.y = y_position
        vehicle.original_x = spawn_x
        vehicle.original_y = y_position
        vehicle.activate()
        vehicle.show()
    
        return vehicle
    
    def check_spawn_collision(self, spawn_x, spawn_y, vehicle_width, vehicle_height, lane):
        min_gap = 200
    
        for vehicle in self.active_vehicles:
            if not vehicle.has_tag(f'lane_{lane}'):
                continue
        
            horizontal_distance = abs(spawn_x - vehicle.x)
        
            if horizontal_distance < (vehicle_width + vehicle.width + min_gap):
                return False
    
        return True
