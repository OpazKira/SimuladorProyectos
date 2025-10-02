import random
import math
from background_element import BackgroundElement
from vehicle_elements import VehicleSpawnManager
class DaySkyElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        super().__init__(0, 0, screen_width, screen_height)
        self.element_type = "day_sky"
        self.set_depth(-100)
        self.add_tag("group_day")
        
        self.gradient_colors = ["#87CEEB", "#B0E0E6", "#E0F6FF"]
    
    def custom_update(self, delta_time):
        pass
    
    def draw_simple(self, canvas, x, y):
        steps = 50
        step_height = self.height / steps
        
        for i in range(steps):
            progress = i / steps
            color = self.interpolate_gradient_color(progress)
            
            canvas.create_rectangle(
                x, y + i * step_height,
                x + self.width, y + (i + 1) * step_height,
                fill=color, outline="", tags="background_layer"
            )
    
    def interpolate_gradient_color(self, progress):
        if progress <= 0.5:
            t = progress * 2
            return self.interpolate_color(self.gradient_colors[0], self.gradient_colors[1], t)
        else:
            t = (progress - 0.5) * 2
            return self.interpolate_color(self.gradient_colors[1], self.gradient_colors[2], t)
    
    def interpolate_color(self, color1, color2, t):
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"

class DaySunElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        sun_size = 120
        x = screen_width // 2 - sun_size // 2
        y = screen_height * 0.15
        
        super().__init__(x, y, sun_size, sun_size)
        self.element_type = "day_sun"
        self.set_depth(-99)
        self.add_tag("group_day")
        
        self.sun_color = "#ffaa00"
        self.glow_color = "#ffdd44"
        self.set_color(self.sun_color)
        
        self.glow_radius = 80
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def custom_update(self, delta_time):
        pass
    
    def draw_simple(self, canvas, x, y):
        self.draw_sun_glow(canvas, x, y)
        
        canvas.create_oval(
            int(x), int(y), int(x + self.width), int(y + self.height),
            fill=self.sun_color, outline="", tags="background_layer"
        )
        
        glow_size = self.width + 20
        canvas.create_oval(
            int(x - 10), int(y - 10), int(x + glow_size - 10), int(y + glow_size - 10),
            fill="", outline=self.glow_color, width=2, tags="background_layer"
        )
    
    def draw_sun_glow(self, canvas, sun_x, sun_y):
        sun_center_x = sun_x + self.width // 2
        sun_center_y = sun_y + self.height // 2
        
        canvas.create_oval(
            sun_center_x - self.glow_radius, sun_center_y - self.glow_radius,
            sun_center_x + self.glow_radius, sun_center_y + self.glow_radius,
            fill="#ffee88", stipple="gray12", outline="", tags="background_layer"
        )
        
        medium_radius = self.glow_radius * 0.6
        canvas.create_oval(
            sun_center_x - medium_radius, sun_center_y - medium_radius,
            sun_center_x + medium_radius, sun_center_y + medium_radius,
            fill="#ffdd66", stipple="gray25", outline="", tags="background_layer"
        )

class CloudElement(BackgroundElement):
    def __init__(self, screen_width, screen_height, start_x=None, y_position=None, depth_layer=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.cloud_style = random.choice(["fluffy", "stretched", "small", "medium", "large"])
        
        if self.cloud_style == "small":
            cloud_width = random.randint(80, 120)
            cloud_height = random.randint(40, 60)
        elif self.cloud_style == "medium":
            cloud_width = random.randint(120, 180)
            cloud_height = random.randint(60, 90)
        elif self.cloud_style == "large":
            cloud_width = random.randint(180, 250)
            cloud_height = random.randint(90, 120)
        elif self.cloud_style == "stretched":
            cloud_width = random.randint(200, 300)
            cloud_height = random.randint(50, 70)
        else:
            cloud_width = random.randint(140, 200)
            cloud_height = random.randint(70, 100)
        
        start_x_pos = start_x if start_x is not None else -cloud_width
        y_pos = y_position if y_position is not None else random.randint(int(screen_height * 0.05), int(screen_height * 0.35))
        
        super().__init__(start_x_pos, y_pos, cloud_width, cloud_height)
        self.element_type = "cloud"
        
        if depth_layer is not None:
            self.set_depth(depth_layer)
        else:
            cloud_depth = random.choice([-98, -96, -94, -93, -91])
            self.set_depth(cloud_depth)
        
        self.add_tag("group_day")
        self.add_tag("cloud")
        
        self.cloud_colors = ["#ffffff", "#f5f5f5", "#fafafa", "#f0f0f0"]
        self.base_color = random.choice(self.cloud_colors)
        self.set_color(self.base_color)
        
        self.speed = random.uniform(25, 45)
        self.set_velocity(self.speed, 0)
        
        self.is_entering = True
        self.entry_progress = 0.0
        self.entry_duration = random.uniform(2.0, 4.0)
        
        depth_opacity_map = {
            -98: (0.4, 0.6),
            -96: (0.5, 0.7),
            -94: (0.6, 0.8),
            -93: (0.7, 0.85),
            -91: (0.75, 0.9)
        }
        opacity_range = depth_opacity_map.get(self.depth, (0.6, 0.85))
        self.opacity_variation = random.uniform(opacity_range[0], opacity_range[1])
        self.set_opacity(0.0)
        
        self.puff_positions = self.generate_puff_positions()
        
        self.cloud_tag = f"cloud_{id(self)}"
        self.canvas_items = []
    
    def generate_puff_positions(self):
        puffs = []
        base_radius = min(self.width, self.height) // 2.5
        
        num_puffs = random.randint(4, 7)
        
        for i in range(num_puffs):
            if i == 0:
                offset_x = self.width * 0.25
                offset_y = self.height * 0.5
                radius = base_radius * random.uniform(0.9, 1.1)
            elif i == num_puffs - 1:
                offset_x = self.width * 0.75
                offset_y = self.height * 0.5
                radius = base_radius * random.uniform(0.9, 1.1)
            else:
                progress = i / (num_puffs - 1)
                offset_x = self.width * (0.15 + progress * 0.7)
                offset_y = self.height * random.uniform(0.35, 0.65)
                radius = base_radius * random.uniform(0.85, 1.15)
            
            puffs.append({
                'x': offset_x,
                'y': offset_y,
                'radius': radius
            })
        
        return puffs
    
    def custom_update(self, delta_time):
        if self.is_entering:
            self.entry_progress += delta_time / self.entry_duration
            if self.entry_progress >= 1.0:
                self.entry_progress = 1.0
                self.is_entering = False
                self.set_opacity(self.opacity_variation)
            else:
                fade_in_opacity = self.entry_progress * self.opacity_variation
                self.set_opacity(fade_in_opacity)
        
        if self.x > self.screen_width + 50:
            self.deactivate()
    
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
        
        if not hasattr(self, 'canvas_items') or not self.canvas_items:
            self.canvas_items = []
            fill_color = self.base_color
            
            for puff in self.puff_positions:
                puff_x = final_x + puff['x']
                puff_y = final_y + puff['y']
                radius = puff['radius']
                
                item_id = canvas.create_oval(
                    int(puff_x - radius), int(puff_y - radius),
                    int(puff_x + radius), int(puff_y + radius),
                    fill=fill_color, outline="", tags=("background_layer",)
                )
                self.canvas_items.append(item_id)
        else:
            for i, puff in enumerate(self.puff_positions):
                if i < len(self.canvas_items):
                    puff_x = final_x + puff['x']
                    puff_y = final_y + puff['y']
                    radius = puff['radius']
                    
                    try:
                        canvas.coords(
                            self.canvas_items[i],
                            int(puff_x - radius), int(puff_y - radius),
                            int(puff_x + radius), int(puff_y + radius)
                        )
                        canvas.itemconfig(self.canvas_items[i], state='normal')
                    except:
                        pass
    
    def get_bounds(self):
        return {
            'left': self.x,
            'top': self.y,
            'right': self.x + self.width,
            'bottom': self.y + self.height
        }
    
    def deactivate(self):
        super().deactivate()
        if hasattr(self, 'cloud_tag'):
            try:
                import tkinter as tk
            except:
                pass

class DayBuildingElement(BackgroundElement):
    def __init__(self, x, y, width, height, layer="front", color=None):
        super().__init__(x, y, width, height)
        self.element_type = "day_building"
        self.layer = layer
        self.add_tag("group_day")
        
        self.building_style = random.choice(["standard", "stepped", "antenna", "dome"])
        
        if layer == "front":
            self.set_depth(-90)
        elif layer == "distant":
            self.set_depth(-92)
        else:
            self.set_depth(-97)
        
        if color:
            self.base_color = color
        else:
            day_colors = ["#8a8a9a", "#9a8a8a", "#8a9a8a", "#9a8a9a", "#8a9a9a"]
            self.base_color = random.choice(day_colors)
        
        self.set_color(self.base_color)
    
    def custom_update(self, delta_time):
        pass
    
    def draw_simple(self, canvas, x, y):
        self.draw_building_structure(canvas, x, y)
    
    def draw_building_structure(self, canvas, x, y):
        if self.building_style == "standard":
            canvas.create_rectangle(
                int(x), int(y), int(x + self.width), int(y + self.height),
                fill=self.base_color, outline="", tags="background_layer"
            )
        
        elif self.building_style == "stepped":
            step_height = self.height // 3
            step_width = self.width // 4
            
            canvas.create_rectangle(
                int(x), int(y + step_height), int(x + self.width), int(y + self.height),
                fill=self.base_color, outline="", tags="background_layer"
            )
            canvas.create_rectangle(
                int(x + step_width), int(y), int(x + self.width - step_width), int(y + step_height * 2),
                fill=self.base_color, outline="", tags="background_layer"
            )
        
        elif self.building_style == "antenna":
            canvas.create_rectangle(
                int(x), int(y + 10), int(x + self.width), int(y + self.height),
                fill=self.base_color, outline="", tags="background_layer"
            )
            antenna_x = x + self.width // 2
            canvas.create_line(
                int(antenna_x), int(y), int(antenna_x), int(y + 15),
                fill="#666666", width=2, tags="background_layer"
            )
        
        elif self.building_style == "dome":
            dome_height = min(20, self.width // 3)
            canvas.create_rectangle(
                int(x), int(y + dome_height), int(x + self.width), int(y + self.height),
                fill=self.base_color, outline="", tags="background_layer"
            )
            canvas.create_arc(
                int(x), int(y), int(x + self.width), int(y + dome_height * 2),
                start=0, extent=180, fill=self.base_color, outline="", tags="background_layer"
            )

class DayRoadElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        road_height = 120
        super().__init__(0, screen_height - road_height, screen_width, road_height)
        self.element_type = "day_road"
        self.set_depth(-80)
        self.add_tag("group_day")
        
        self.road_color = "#4a4a4a"
        self.line_color = "#8a8a8a"
    
    def custom_update(self, delta_time):
        pass
    
    def draw_simple(self, canvas, x, y):
        x = int(x)
        y = int(y)
        width = int(self.width)
        height = int(self.height)
        
        canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=self.road_color, outline="", tags="background_layer"
        )
        
        line_y = y + height // 2
        dash_width = 30
        gap_width = 20
        
        for dash_x in range(x, x + width, dash_width + gap_width):
            canvas.create_rectangle(
                dash_x, line_y - 2,
                min(dash_x + dash_width, x + width), line_y + 2,
                fill=self.line_color, outline="", tags="background_layer"
            )

class DayBackgroundManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.elements = []
        
        self.building_positions_cache = None
        
        self.active_clouds = []
        self.cloud_spawn_enabled = False
        self.last_cloud_spawn_time = 0
        self.min_cloud_horizontal_spacing = 400
        self.min_cloud_vertical_spacing = 80
        self.max_clouds = 6
        
        try:
            from vehicle_elements import VehicleSpawnManager
            self.vehicle_manager = VehicleSpawnManager(screen_width, screen_height)
        except ImportError as e:
            print(f"Warning: No se pudo importar vehicle_elements: {e}")
            self.vehicle_manager = None
    
    def enable_cloud_spawning(self):
        self.cloud_spawn_enabled = True
        self.last_cloud_spawn_time = 0
    
    def disable_cloud_spawning(self):
        self.cloud_spawn_enabled = False
    
    def should_spawn_cloud(self):
        if not self.cloud_spawn_enabled:
            return False
        
        if len(self.active_clouds) >= self.max_clouds:
            return False
        
        import time
        current_time = time.time()
        
        min_delay = 5.0
        max_delay = 10.0
        
        time_since_last = current_time - self.last_cloud_spawn_time
        spawn_delay = random.uniform(min_delay, max_delay)
        
        if time_since_last < spawn_delay:
            return False
        
        for cloud in self.active_clouds:
            if cloud.x < self.min_cloud_horizontal_spacing:
                return False
        
        return True
    
    def find_valid_cloud_position(self, max_attempts=15):
        min_y = int(self.screen_height * 0.05)
        max_y = int(self.screen_height * 0.35)
        
        for attempt in range(max_attempts):
            y_position = random.randint(min_y, max_y)
            position_valid = True
            
            for cloud in self.active_clouds:
                if cloud.x > 200:
                    continue
                
                vertical_distance = abs(y_position - cloud.y)
                
                if vertical_distance < self.min_cloud_vertical_spacing:
                    position_valid = False
                    break
            
            if position_valid:
                return y_position
        
        return None
    
    def spawn_cloud(self):
        import time
        
        y_position = self.find_valid_cloud_position()
        
        if y_position is None:
            return None
        
        depth_options = [-98, -96, -94, -93, -91]
        chosen_depth = random.choice(depth_options)
        
        cloud = CloudElement(
            self.screen_width, 
            self.screen_height, 
            start_x=-250, 
            y_position=y_position,
            depth_layer=chosen_depth
        )
        cloud.activate()
        cloud.show()
        
        self.active_clouds.append(cloud)
        self.last_cloud_spawn_time = time.time()
        
        return cloud
    
    def update_clouds(self, delta_time):
        self.active_clouds = [cloud for cloud in self.active_clouds if cloud.is_active()]
        
        if self.should_spawn_cloud():
            spawned = self.spawn_cloud()
    
    def update_vehicles(self, delta_time, background_elements):
        if not self.vehicle_manager:
            return []
    
        new_vehicles = list(self.vehicle_manager.update(delta_time, background_elements))
    
        return new_vehicles
    
    def generate_building_positions(self, road_top, layer_type="front"):
        positions = []
        current_x = 0
        
        if layer_type == "front":
            min_height = 80
            max_height = 300
            min_gap = 8
            max_gap = 25
            min_width = 25 
            max_width = 120
        elif layer_type == "distant":
            min_height = 60
            max_height = 200
            min_gap = 5
            max_gap = 20
            min_width = 30
            max_width = 110
        else:
            min_height = 40
            max_height = 120
            min_gap = 0
            max_gap = 15
            min_width = 35
            max_width = 100
        
        while current_x < self.screen_width + 50:
            if random.random() < 0.3:
                width = random.randint(min_width, min_width + 20)
            elif random.random() < 0.6:
                width = random.randint(min_width + 20, min_width + 50)
            else:
                width = random.randint(min_width + 50, max_width)
                
            height = random.randint(min_height, max_height)
            y = road_top - height
            
            positions.append({
                'x': current_x,
                'y': y,
                'width': width,
                'height': height
            })
            
            gap = random.randint(min_gap, max_gap)
            current_x += width + gap
        
        return positions
    
    def create_from_transition_state(self, transition_state):
        elements_to_keep = [e for e in self.elements if e.element_type == "vehicle"]
        self.elements = elements_to_keep
    
        sky_created = False
        road_created = False
        sun_created = False
    
        sorted_keys = sorted(transition_state.keys())
    
        for key in sorted_keys:
            data = transition_state[key]
            element_ref = data.get('element_ref')
            final_state = data['final_state']
            pos = data['position']
        
            if 'sky' in key and not sky_created:
                sky = DaySkyElement(self.screen_width, self.screen_height)
                sky.activate()
                sky.show()
                self.elements.append(sky)
                sky_created = True
            
            elif 'road' in key and not road_created:
                road = DayRoadElement(self.screen_width, self.screen_height)
                road.activate()
                road.show()
                self.elements.append(road)
                road_created = True
            
            elif 'building' in key:
                layer = data.get('layer', 'front')
                if not layer and element_ref and hasattr(element_ref, 'layer'):
                    layer = element_ref.layer
            
                building = DayBuildingElement(
                    pos['x'], pos['y'], pos['width'], pos['height'],
                    layer=layer,
                    color=final_state['color']
                )
            
                if 'building_style' in data:
                    building.building_style = data['building_style']
                elif element_ref and hasattr(element_ref, 'building_style'):
                    building.building_style = element_ref.building_style
            
                building.activate()
                building.show()
                self.elements.append(building)
            
            elif 'sun' in key and not sun_created:
                sun = DaySunElement(self.screen_width, self.screen_height)
                sun.activate()
                sun.show()
                self.elements.append(sun)
                sun_created = True
    
        if not sky_created:
            sky = DaySkyElement(self.screen_width, self.screen_height)
            sky.activate()
            sky.show()
            self.elements.insert(0, sky)
        
        if not road_created:
            road = DayRoadElement(self.screen_width, self.screen_height)
            road.activate()
            road.show()
            self.elements.append(road)
        
        if not sun_created:
            sun = DaySunElement(self.screen_width, self.screen_height)
            sun.activate()
            sun.show()
            self.elements.append(sun)
    
        return self.elements
    
    def create_day_background(self):
        self.elements.clear()
        
        sky = DaySkyElement(self.screen_width, self.screen_height)
        sky.activate()
        sky.show()
        self.elements.append(sky)
        
        road = DayRoadElement(self.screen_width, self.screen_height)
        road.activate()
        road.show()
        road_top = road.y
        self.elements.append(road)
        
        if not self.building_positions_cache:
            self.building_positions_cache = {
                'far': self.generate_building_positions(road_top, "far"),
                'distant': self.generate_building_positions(road_top, "distant"),
                'front': self.generate_building_positions(road_top, "front")
            }
        
        for layer in ['far', 'distant', 'front']:
            for pos in self.building_positions_cache[layer]:
                building = DayBuildingElement(pos['x'], pos['y'], pos['width'], pos['height'], layer)
                building.activate()
                building.show()
                self.elements.append(building)
        
        sun = DaySunElement(self.screen_width, self.screen_height)
        sun.activate()
        sun.show()
        self.elements.append(sun)
        
        return self.elements
    
    def get_elements(self):
        return self.elements
