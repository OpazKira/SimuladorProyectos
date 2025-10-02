import random
import math
from background_element import BackgroundElement

class NightSkyElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        super().__init__(0, 0, screen_width, screen_height)
        self.element_type = "night_sky"
        self.set_depth(-100)
        self.add_tag("group_a")
        self.add_tag("night_sky")
        
        self.base_gradient_colors = ["#0a0a1e", "#1a1a3a", "#2a2a4a"]
        self.target_gradient_colors = ["#0a0a2a", "#1a1a4a", "#2a2a6a"]
        self.gradient_colors = self.base_gradient_colors.copy()
        
        self.transition_progress = 0.0
        self.is_transitioning = False
        
        self.final_day_colors = ["#87CEEB", "#B0E0E6", "#E0F6FF"]
        self.transition_complete = False
    
    def start_sky_transition(self):
        self.is_transitioning = True
        self.transition_progress = 0.0
    
    def start_dawn_transition(self):
        self.is_transitioning = True
        self.transition_progress = 0.0
        self.target_gradient_colors = self.final_day_colors.copy()
    
    def update_dawn_transition(self, sun_y, target_sun_y):
        if not self.is_transitioning:
            return
            
        initial_sun_y = self.height + 120
        travel_distance = initial_sun_y - target_sun_y
        
        if travel_distance > 0:
            current_progress = (initial_sun_y - sun_y) / travel_distance
            self.transition_progress = max(0.0, min(1.0, current_progress))
            
            self.gradient_colors = []
            for i in range(len(self.base_gradient_colors)):
                interpolated_color = self.interpolate_color(
                    self.base_gradient_colors[i],
                    self.target_gradient_colors[i],
                    self.transition_progress
                )
                self.gradient_colors.append(interpolated_color)
            
            if self.transition_progress >= 1.0:
                self.transition_complete = True
                self.gradient_colors = self.final_day_colors.copy()
    
    def get_final_state(self):
        return {
            'gradient_colors': self.final_day_colors.copy(),
            'element_type': 'day_sky'
        }
    
    def apply_final_state(self, state):
        self.gradient_colors = state['gradient_colors'].copy()
        self.element_type = state['element_type']
        self.transition_complete = True
    
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

class StarElement(BackgroundElement):
    def __init__(self, x, y):
        size = random.randint(2, 4)
        super().__init__(x, y, size, size)
        self.element_type = "star"
        self.set_depth(-98)
        self.add_tag("group_a")
        self.add_tag("star")
        
        self.base_opacity = random.uniform(0.6, 1.0)
        self.twinkle_speed = random.uniform(1.0, 3.0)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
        self.is_twinkling = True
        
        star_colors = ["#ffffff", "#ffffcc", "#ccccff", "#ffcccc"]
        self.star_color = random.choice(star_colors)
        self.set_color(self.star_color)
        
        self.set_opacity(self.base_opacity)
    
    def custom_update(self, delta_time):
        if not self.active:
            return
            
        if hasattr(self, 'is_fading') and self.is_fading:
            self.update_fade(delta_time)
            return
            
        if self.is_twinkling:
            self.twinkle_phase += self.twinkle_speed * delta_time
            opacity_variation = math.sin(self.twinkle_phase) * 0.4
            new_opacity = self.base_opacity + opacity_variation
            self.set_opacity(max(0.2, min(1.0, new_opacity)))
    
    def update_fade(self, delta_time):
        if not hasattr(self, 'is_fading') or not self.is_fading:
            return
            
        if not hasattr(self, 'fade_start_time') or self.fade_start_time is None:
            self.fade_start_time = 0
            
        self.fade_start_time += delta_time
        progress = min(self.fade_start_time / self.fade_duration, 1.0)
        
        new_opacity = self.initial_opacity * (1.0 - progress)
        self.set_opacity(new_opacity)
        
        if progress >= 1.0:
            self.is_fading = False
            self.deactivate()
    
    def start_gradual_fade(self, fade_duration=2.0):
        self.is_twinkling = False
        self.fade_start_time = 0.0
        self.fade_duration = fade_duration
        self.initial_opacity = self.opacity
        self.is_fading = True
    
    def stop_twinkling(self):
        self.is_twinkling = False
        
    def check_collision_with_moon(self, moon_bounds):
        star_center_x = self.x + self.width / 2
        star_center_y = self.y + self.height / 2
        
        return (moon_bounds['left'] <= star_center_x <= moon_bounds['right'] and
                moon_bounds['top'] <= star_center_y <= moon_bounds['bottom'])
    
    def draw_simple(self, canvas, x, y):
        if self.opacity > 0.1:
            canvas.create_oval(
                int(x), int(y), int(x + self.width), int(y + self.height),
                fill=self.color, outline="", tags="background_layer"
            )
    
    def start_finale_twinkle(self):
        self.twinkle_speed = random.uniform(8.0, 15.0)
        self.is_twinkling = True

class MoonElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        moon_size = 120
        x = screen_width // 2 - moon_size // 2
        y = screen_height * 0.15
        
        super().__init__(x, y, moon_size, moon_size)
        self.element_type = "moon"
        self.set_depth(-99)
        self.add_tag("group_a")
        self.add_tag("moon")
        
        self.moon_color = "#f5f5dc"
        self.glow_color = "#ffffcc"
        self.set_color(self.moon_color)
        
        self.glow_radius = 80
        self.glow_intensity = 0.15
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def custom_update(self, delta_time):
        pass
    
    def draw_simple(self, canvas, x, y):
        self.draw_translucent_glow(canvas, x, y)
        
        canvas.create_oval(
            x, y, x + self.width, y + self.height,
            fill=self.color, outline="", tags="background_layer"
        )
        
        glow_size = self.width + 20
        canvas.create_oval(
            x - 10, y - 10, x + glow_size - 10, y + glow_size - 10,
            fill="", outline=self.glow_color, width=2, tags="background_layer"
        )
    
    def draw_translucent_glow(self, canvas, moon_x, moon_y):
        moon_center_x = moon_x + self.width // 2
        moon_center_y = moon_y + self.height // 2
        
        canvas.create_oval(
            moon_center_x - self.glow_radius, moon_center_y - self.glow_radius,
            moon_center_x + self.glow_radius, moon_center_y + self.glow_radius,
            fill="#ffffaa", stipple="gray12", outline="", tags="background_layer"
        )
        
        medium_radius = self.glow_radius * 0.6
        canvas.create_oval(
            moon_center_x - medium_radius, moon_center_y - medium_radius,
            moon_center_x + medium_radius, moon_center_y + medium_radius,
            fill="#ffffcc", stipple="gray25", outline="", tags="background_layer"
        )
    
    def start_fade_descent(self):
        self.set_velocity(0, 100)  # Cambia de 50 a 100 (doble velocidad)
        
    def get_collision_bounds(self):
        margin = 20
        return {
            'left': self.x - margin,
            'right': self.x + self.width + margin,
            'top': self.y - margin,
            'bottom': self.y + self.height + margin
        }
    
    def is_behind_buildings(self, road_top):
        return self.y > road_top

class SunElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        sun_size = 120
        x = screen_width // 2 - sun_size // 2
        y = screen_height + sun_size
        
        super().__init__(x, y, sun_size, sun_size)
        self.element_type = "sun"
        self.set_depth(-99)
        self.add_tag("group_a")
        self.add_tag("sun")
        
        self.sun_color = "#ffaa00"
        self.glow_color = "#ffdd44"
        self.set_color(self.sun_color)
        
        self.glow_radius = 80
        self.glow_intensity = 0.2
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.target_y = screen_height * 0.15
        self.is_rising = False
        self.rise_speed = 0
    
    def start_sunrise(self):
        self.is_rising = True
        distance = self.y - self.target_y
        self.rise_speed = distance / 5.0  # Cambia de 10.0 a 5.0 (doble velocidad)
        self.set_velocity(0, -self.rise_speed)
        print(f"DEBUG: Sol iniciando ascenso - Distancia: {distance:.1f}px, Velocidad: {self.rise_speed:.2f}px/s")
        print(f"DEBUG: Sol desde Y:{self.y:.1f} hacia Y:{self.target_y:.1f}")
    
    def get_final_state(self):
        return {
            'x': self.screen_width // 2 - 60,
            'y': self.target_y,
            'sun_color': self.sun_color,
            'glow_color': self.glow_color,
            'element_type': 'day_sun'
        }
    
    def custom_update(self, delta_time):
        if self.is_rising and self.y > self.target_y:
            if hasattr(self, '_debug_counter'):
                self._debug_counter += 1
            else:
                self._debug_counter = 0
            
            if self._debug_counter % 30 == 0:  
                remaining = self.y - self.target_y
                print(f"DEBUG: Sol subiendo - Y: {self.y:.1f}, Restante: {remaining:.1f}px")
                
        elif self.is_rising and self.y <= self.target_y:
            self.set_velocity(0, 0)
            self.y = self.target_y
            self.is_rising = False
            print(f"DEBUG: Sol termino ascenso en Y:{self.y:.1f}")
        elif not self.is_rising:
            if not hasattr(self, '_stopped_debug'):
                print(f"DEBUG: Sol detenido permanentemente en Y:{self.y:.1f}")
                self._stopped_debug = True
    
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

class BuildingSilhouetteElement(BackgroundElement):
    def __init__(self, x, y, width, height, layer="front"):
        super().__init__(x, y, width, height)
        self.element_type = "building_silhouette"
        self.layer = layer
        self.add_tag("group_a")
        self.add_tag("building_silhouette")
        
        self.building_style = random.choice(["standard", "stepped", "antenna", "dome"])
        
        if layer == "front":
            self.set_depth(-90)
            building_colors = [
                "#3a3a4a", "#4a3a3a", "#3a4a3a", "#4a3a4a",
                "#3a4a4a", "#4a4a3a", "#454545", "#3d3d50"
            ]
        elif layer == "distant":
            self.set_depth(-92)
            building_colors = [
                "#353540", "#403535", "#354035", "#403540",
                "#354040", "#404035", "#3a3a3a", "#353545"
            ]
        else:
            self.set_depth(-97)
            building_colors = [
                "#1a1a25", "#251a1a", "#1a251a", "#251a25",
                "#1a2525", "#25251a", "#202020", "#1a1a2a"
            ]
        
        self.base_color = random.choice(building_colors)
        self.original_color = self.base_color
        self.set_color(self.base_color)
        
        day_colors_map = {
            "#3a3a4a": "#8a8a9a", "#4a3a3a": "#9a8a8a", "#3a4a3a": "#8a9a8a", "#4a3a4a": "#9a8a9a",
            "#3a4a4a": "#8a9a9a", "#4a4a3a": "#9a9a8a", "#454545": "#959595", "#3d3d50": "#8d8da0",
            "#353540": "#757580", "#403535": "#807575", "#354035": "#758075", "#403540": "#807580",
            "#354040": "#758080", "#404035": "#808075", "#3a3a3a": "#7a7a7a", "#353545": "#757585",
            "#1a1a25": "#6a6a75", "#251a1a": "#756a6a", "#1a251a": "#6a756a", "#251a25": "#756a75",
            "#1a2525": "#6a7575", "#25251a": "#75756a", "#202020": "#707070", "#1a1a2a": "#6a6a7a"
        }
        self.final_day_color = day_colors_map.get(self.base_color, "#808080")
        
        self.is_transitioning_color = False
        self.start_color = self.base_color
        self.target_color = self.base_color
        self.transition_progress = 0.0
    
    def get_final_state(self):
        return {
            'color': self.final_day_color,
            'element_type': 'day_building'
        }
    
    def apply_final_state(self, state):
        self.set_color(state['color'])
        self.base_color = state['color']
        self.element_type = state['element_type']
    
    def custom_update(self, delta_time):
        if self.is_transitioning_color:
            self.update_color_transition()
    
    def update_color_transition(self):
        if self.is_transitioning_color and hasattr(self, 'transition_progress'):
            new_color = self.interpolate_color(self.start_color, self.target_color, self.transition_progress)
            self.set_color(new_color)
            self.base_color = new_color
    
    def interpolate_color(self, color1, color2, progress):
        try:
            r1 = int(color1[1:3], 16)
            g1 = int(color1[3:5], 16)
            b1 = int(color1[5:7], 16)
            
            r2 = int(color2[1:3], 16)
            g2 = int(color2[3:5], 16)
            b2 = int(color2[5:7], 16)
            
            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1
    
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

class RoadElement(BackgroundElement):
    def __init__(self, screen_width, screen_height):
        road_height = 120
        super().__init__(0, screen_height - road_height, screen_width, road_height)
        self.element_type = "road"
        self.set_depth(-80)
        self.add_tag("group_a")
        self.add_tag("road")
        
        self.road_color = "#1a1a1a"
        self.line_color = "#3a3a3a"
        self.original_road_color = "#1a1a1a"
        self.original_line_color = "#3a3a3a"
        
        self.final_road_color = "#4a4a4a"
        self.final_line_color = "#8a8a8a"
        
        self.is_transitioning_color = False
        self.start_road_color = self.road_color
        self.start_line_color = self.line_color
        self.target_road_color = self.road_color
        self.target_line_color = self.line_color
        self.transition_progress = 0.0
    
    def get_final_state(self):
        return {
            'road_color': self.final_road_color,
            'line_color': self.final_line_color,
            'element_type': 'day_road'
        }
    
    def apply_final_state(self, state):
        self.road_color = state['road_color']
        self.line_color = state['line_color']
        self.element_type = state['element_type']
    
    def custom_update(self, delta_time):
        if self.is_transitioning_color:
            self.update_color_transition()
    
    def update_color_transition(self):
        if self.is_transitioning_color and hasattr(self, 'transition_progress'):
            self.road_color = self.interpolate_color(self.start_road_color, self.target_road_color, self.transition_progress)
            self.line_color = self.interpolate_color(self.start_line_color, self.target_line_color, self.transition_progress)
    
    def interpolate_color(self, color1, color2, progress):
        try:
            r1 = int(color1[1:3], 16)
            g1 = int(color1[3:5], 16)
            b1 = int(color1[5:7], 16)
            
            r2 = int(color2[1:3], 16)
            g2 = int(color2[3:5], 16)
            b2 = int(color2[5:7], 16)
            
            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1
    
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

class NightBackgroundManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.elements = []
        
        self.final_transition_state = None
    
    def create_loading_background_elements(self):
        self.elements.clear()
        
        sky = NightSkyElement(self.screen_width, self.screen_height)
        self.elements.append(sky)
        
        road = RoadElement(self.screen_width, self.screen_height)
        road_top = road.y
        self.elements.append(road)
        
        far_buildings = self.generate_building_positions(road_top, "far")
        for pos in far_buildings:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "far")
            self.elements.append(building)
        
        distant_buildings = self.generate_building_positions(road_top, "distant")
        for pos in distant_buildings:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "distant")
            self.elements.append(building)
        
        front_buildings = self.generate_building_positions(road_top, "front")
        for pos in front_buildings:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "front")
            self.elements.append(building)
        
        moon = MoonElement(self.screen_width, self.screen_height)
        self.elements.append(moon)
        
        moon_x = moon.x + moon.width // 2
        moon_y = moon.y + moon.height // 2
        moon_radius = 100
        
        star_count = 120
        for _ in range(star_count):
            while True:
                x = random.randint(0, int(self.screen_width * 0.95))
                y = random.randint(0, int(self.screen_height * 0.7))
                
                distance_to_moon = math.sqrt((x - moon_x)**2 + (y - moon_y)**2)
                if distance_to_moon > moon_radius:
                    break
            
            star = StarElement(x, y)
            self.elements.append(star)
        
        return self.elements
    
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
    
    def capture_final_transition_state(self):
        if not self.elements:
            print("DEBUG: No hay elementos para capturar estado")
            return
            
        self.final_transition_state = {}
        
        for element in self.elements:
            if hasattr(element, 'get_final_state'):
                element_key = f"{element.element_type}_{element.x}_{element.y}"
                
                final_state_data = {
                    'element_ref': element,
                    'final_state': element.get_final_state(),
                    'position': {'x': element.x, 'y': element.y, 'width': element.width, 'height': element.height}
}
                
                if hasattr(element, 'building_style'):
                    final_state_data['building_style'] = element.building_style
                
                if hasattr(element, 'layer'):
                    final_state_data['layer'] = element.layer
                
                self.final_transition_state[element_key] = final_state_data
        
        print(f"DEBUG: Capturado estado final con {len(self.final_transition_state)} elementos")
        for key, data in list(self.final_transition_state.items())[:5]:
            print(f"DEBUG: - {key}: {data['final_state']}")
    
    def create_toDay_background_elements(self):
        self.elements.clear()
        
        sky = NightSkyElement(self.screen_width, self.screen_height)
        sky.gradient_colors = ["#0a0a2a", "#1a1a4a", "#2a2a6a"]
        sky.element_type = "toDay_sky"
        self.elements.append(sky)
        
        road = RoadElement(self.screen_width, self.screen_height)
        road.element_type = "toDay_road"
        road_top = road.y
        self.elements.append(road)
        
        building_positions = self.generate_building_positions(road_top, "front")
        for pos in building_positions:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "front")
            building.element_type = "toDay_building"
            self.elements.append(building)
        
        sun = SunElement(self.screen_width, self.screen_height)
        self.elements.append(sun)
        
        return self.elements
    
    def create_day_background_elements(self):
        print("DEBUG: create_day_background_elements llamado")
        self.elements.clear()
        
        if hasattr(self, 'final_transition_state') and self.final_transition_state:
            print("DEBUG: Usando estado final capturado para fondo diurno")
            return self.create_day_from_final_state()
        
        print("DEBUG: Creando fondo diurno normal (sin estado final)")
        return self.create_standard_day_background()
    
    def create_day_from_final_state(self):
        print("DEBUG: create_day_from_final_state iniciado")
        
        sky = NightSkyElement(self.screen_width, self.screen_height)
        sky_final_state = {
            'gradient_colors': ["#87CEEB", "#B0E0E6", "#E0F6FF"],
            'element_type': 'day_sky'
        }
        sky.apply_final_state(sky_final_state)
        sky.set_depth(-100)
        sky.activate()
        sky.show()
        self.elements.append(sky)
        
        road = RoadElement(self.screen_width, self.screen_height)
        road_final_state = {
            'road_color': "#4a4a4a",
            'line_color': "#8a8a8a",
            'element_type': 'day_road'
        }
        road.apply_final_state(road_final_state)
        road.set_depth(-80)
        road.activate()
        road.show()
        road_top = road.y
        self.elements.append(road)
        
        far_positions = self.generate_building_positions(road_top, "far")
        for pos in far_positions:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "far")
            building_final_state = building.get_final_state()
            building.apply_final_state(building_final_state)
            building.set_depth(-97)
            building.activate()
            building.show()
            self.elements.append(building)
        
        distant_positions = self.generate_building_positions(road_top, "distant")
        for pos in distant_positions:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "distant")
            building_final_state = building.get_final_state()
            building.apply_final_state(building_final_state)
            building.set_depth(-92)
            building.activate()
            building.show()
            self.elements.append(building)
        
        front_positions = self.generate_building_positions(road_top, "front")
        for pos in front_positions:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'], "front")
            building_final_state = building.get_final_state()
            building.apply_final_state(building_final_state)
            building.set_depth(-90)
            building.activate()
            building.show()
            self.elements.append(building)
        
        sun = SunElement(self.screen_width, self.screen_height)
        sun.y = sun.target_y
        sun.x = self.screen_width // 2 - 60
        sun.element_type = "day_sun"
        sun.set_depth(-99)
        sun.activate()
        sun.show()
        self.elements.append(sun)
        
        print(f"DEBUG: Fondo diurno completado con {len(self.elements)} elementos")
        return self.elements
    
    def create_standard_day_background(self):
        print("DEBUG: create_standard_day_background iniciado")
        
        sky = NightSkyElement(self.screen_width, self.screen_height)
        sky.gradient_colors = ["#87CEEB", "#B0E0E6", "#E0F6FF"]
        sky.element_type = "day_sky"
        sky.set_depth(-100)
        sky.activate()
        sky.show()
        self.elements.append(sky)
        
        road = RoadElement(self.screen_width, self.screen_height)
        road.road_color = "#4a4a4a"
        road.line_color = "#8a8a8a"
        road.element_type = "day_road"
        road.set_depth(-80)
        road.activate()
        road.show()
        road_top = road.y
        self.elements.append(road)
        
        building_positions = self.generate_building_positions(road_top, "front")
        building_count = 0
        for pos in building_positions:
            building = BuildingSilhouetteElement(pos['x'], pos['y'], pos['width'], pos['height'])
            day_colors = ["#8a8a9a", "#9a8a8a", "#8a9a8a", "#9a8a9a", "#8a9a9a"]
            building.set_color(random.choice(day_colors))
            building.element_type = "day_building"
            building.set_depth(-90)
            building.activate()
            building.show()
            self.elements.append(building)
            building_count += 1
        
        sun = SunElement(self.screen_width, self.screen_height)
        sun.y = sun.target_y
        sun.x = self.screen_width // 2 - 60
        sun.element_type = "day_sun"
        sun.set_depth(-99)
        sun.activate()
        sun.show()
        self.elements.append(sun)
        
        print(f"DEBUG: Fondo diurno estandar completado con {len(self.elements)} elementos ACTIVOS")
        for elem in self.elements:
            print(f"DEBUG:   - {elem.element_type} activo={elem.is_active()} visible={elem.is_visible()} depth={elem.depth}")
        
        return self.elements
    
    def get_elements_by_group(self, group):
        return [elem for elem in self.elements if elem.has_tag(f"group_{group}")]