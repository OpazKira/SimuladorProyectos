import tkinter as tk
import time
import random
from screen_handler import ScreenHandler
from screen_element import ScreenElement, ButtonElement
from background_element import BackgroundElement

class LoadingScreen(ScreenHandler):
    def __init__(self, canvas, app):
        super().__init__(canvas, app, "loading")
        
        self.loading_progress = 0.0
        self.loading_complete = False
        self.loading_start_time = None
        self.loading_duration = 5.0
        
        self.progress_bar = None
        self.loading_text = None
        self.countdown_text = None
        self.instruction_text = None
        self.instruction_blink_timer = None
        
        self.skip_enabled = False
        self.transition_started = False
        self.toDay_transition_started = False
        
        self.cursor_handler = app.get_cursor_handler()
    
    def create_specific_background(self):
        pass
    
    def create_specific_ui(self):
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        progress_y = center_y + 150
        self.create_progress_bar(center_x - 400, progress_y, 800, 25)
        
        self.countdown_text = self.create_centered_text("", 200, 18, "#ffff88", "_countdown")
        
        self.instruction_text = self.create_centered_text(
            "[Presiona ENTER o haz CLICK para comenzar]", 
            250, 16, "#ffff88", "_instruction"
        )
        self.canvas.itemconfig(self.instruction_text, state='hidden')
    
    def create_progress_bar(self, x, y, width, height):
        bg_id = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill="#333333",
            outline="#666666",
            width=2,
            tags="loading_progress_bg"
        )
        
        progress_id = self.canvas.create_rectangle(
            x, y, x, y + height,
            fill="#4CAF50",
            outline="",
            tags="loading_progress_bar"
        )
        
        self.add_ui_element(bg_id)
        self.add_ui_element(progress_id)
        
        self.progress_bar = {
            'bg_id': bg_id,
            'bar_id': progress_id,
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
    
    def update_progress_bar(self, progress):
        if self.progress_bar:
            bar_width = self.progress_bar['width'] * progress
            self.canvas.coords(
                self.progress_bar['bar_id'],
                self.progress_bar['x'],
                self.progress_bar['y'],
                self.progress_bar['x'] + bar_width,
                self.progress_bar['y'] + self.progress_bar['height']
            )
    
    def on_show(self):
        self.loading_start_time = time.time()
        self.loading_progress = 0.0
        self.loading_complete = False
        self.skip_enabled = False
        self.transition_started = False
        self.toDay_transition_started = False
        
        self.canvas.bind('<KeyPress>', self.on_key_press)
        self.canvas.bind('<Button-1>', self.on_mouse_click)
        self.canvas.focus_set()
        
        self.start_loading_animation()
    
    def start_loading_animation(self):
        if not self.is_visible or self.transition_started:
            return
        
        current_time = time.time()
        if self.loading_start_time:
            elapsed = current_time - self.loading_start_time
            self.loading_progress = min(elapsed / self.loading_duration, 1.0)
            
            self.update_progress_bar(self.loading_progress)
            
            remaining_time = max(0, self.loading_duration - elapsed)
            
            if remaining_time > 0:
                self.canvas.itemconfig(self.countdown_text, 
                    text=f"Tiempo restante: {int(remaining_time) + 1}s")
            else:
                self.canvas.itemconfig(self.countdown_text, text="")
            
            if elapsed >= 5.0 and not self.skip_enabled:
                self.enable_skip()
            
            if self.loading_progress >= 1.0 and not self.loading_complete:
                self.loading_complete = True
            else:
                self.canvas.after(50, self.start_loading_animation)
    
    def enable_skip(self):
        self.skip_enabled = True
        
        if self.countdown_text:
            self.canvas.itemconfig(self.countdown_text, state='hidden')
        
        if self.progress_bar:
            self.canvas.itemconfig(self.progress_bar['bg_id'], state='hidden')
            self.canvas.itemconfig(self.progress_bar['bar_id'], state='hidden')
        
        if self.instruction_text:
            self.canvas.itemconfig(self.instruction_text, state='normal')
            self.start_instruction_blink()
    
    def start_instruction_blink(self):
        if not self.skip_enabled or self.transition_started:
            return
        
        current_state = self.canvas.itemcget(self.instruction_text, 'state')
        new_state = 'hidden' if current_state == 'normal' else 'normal'
        self.canvas.itemconfig(self.instruction_text, state=new_state)
        
        self.canvas.after(500, self.start_instruction_blink)
    
    def on_key_press(self, event):
        if event.keysym == 'Return' and self.skip_enabled and not self.transition_started:
            self.start_transition_sequence()
    
    def on_mouse_click(self, event):
        if self.skip_enabled and not self.transition_started:
            self.start_transition_sequence()
    
    def start_transition_sequence(self):
        if self.transition_started:
            return
        
        self.transition_started = True
        
        if self.instruction_text:
            self.canvas.itemconfig(self.instruction_text, state='hidden')
        
        self.start_star_finale()
        self.canvas.after(500, self.start_moon_fade)
    
    def start_star_finale(self):
        star_elements = self.background_handler.get_elements_by_type("star")
        print(f"DEBUG: Iniciando finale de {len(star_elements)} estrellas")
        
        moon_elements = self.background_handler.get_elements_by_type("moon")
        moon = moon_elements[0] if moon_elements else None
        
        collision_count = 0
        fade_count = 0
        
        for star in star_elements:
            if hasattr(star, 'stop_twinkling'):
                star.stop_twinkling()
            
            if moon and hasattr(star, 'check_collision_with_moon'):
                moon_bounds = moon.get_collision_bounds()
                if star.check_collision_with_moon(moon_bounds):
                    if hasattr(star, 'start_gradual_fade'):
                        star.start_gradual_fade(0.5)
                        collision_count += 1
                else:
                    if hasattr(star, 'start_gradual_fade'):
                        star.start_gradual_fade(2.0)
                        fade_count += 1
            else:
                if hasattr(star, 'start_gradual_fade'):
                    star.start_gradual_fade(2.0)
                    fade_count += 1
        
        print(f"DEBUG: {collision_count} estrellas en colision, {fade_count} estrellas normales")
    
    def start_moon_fade(self):
        moon_elements = self.background_handler.get_elements_by_type("moon")
    
        sky_elements = self.background_handler.get_elements_by_type("night_sky")
        if sky_elements and hasattr(sky_elements[0], 'start_sky_transition'):
            sky_elements[0].start_sky_transition()
    
        for moon in moon_elements:
            if hasattr(moon, 'start_fade_descent'):
                moon.start_fade_descent()
        self.monitor_moon_descent(moon_elements)
    
    def monitor_moon_descent(self, moon_elements):
        if not moon_elements or not self.transition_started:
            return
        
        moon = moon_elements[0]
    
        sky_elements = self.background_handler.get_elements_by_type("night_sky")
        if sky_elements:
            sky = sky_elements[0]
            road_elements = self.background_handler.get_elements_by_type("road")
            if road_elements and hasattr(sky, 'update_sky_transition'):
                road_top = road_elements[0].y
                sky.update_sky_transition(moon.y, road_top)
    
        road_elements = self.background_handler.get_elements_by_type("road")
        if road_elements:
            road_top = road_elements[0].y
        
            if hasattr(moon, 'is_behind_buildings') and moon.is_behind_buildings(road_top):
                self.start_toDay_transition()
            else:
                self.canvas.after(16, lambda: self.monitor_moon_descent(moon_elements))
        else:
            self.canvas.after(3000, self.start_toDay_transition)
    
    def start_toDay_transition(self):
        if self.toDay_transition_started:
            return
            
        self.toDay_transition_started = True
        print("DEBUG: Iniciando transicion toDay desde loading_screen")
        
        self.hide_loading_ui()
        self.add_sun_to_current_background()
    
    def hide_loading_ui(self):
        if self.progress_bar:
            self.canvas.itemconfig(self.progress_bar['bg_id'], state='hidden')
            self.canvas.itemconfig(self.progress_bar['bar_id'], state='hidden')
        
        if self.countdown_text:
            self.canvas.itemconfig(self.countdown_text, state='hidden')
        
        for element_id in self.ui_elements:
            try:
                self.canvas.itemconfig(element_id, state='hidden')
            except tk.TclError:
                pass
    
    def add_sun_to_current_background(self):
        try:
            from night_background_elements import SunElement
            
            sun = SunElement(self.screen_width, self.screen_height)
            self.background_handler.add_background_element(sun)
            
            if hasattr(sun, 'start_sunrise'):
                sun.start_sunrise()
                print("DEBUG: Sol agregado e iniciando ascenso")
            
            sky_elements = self.background_handler.get_elements_by_type("night_sky")
            for sky in sky_elements:
                if hasattr(sky, 'start_dawn_transition'):
                    sky.start_dawn_transition()
                    print("DEBUG: Cielo iniciando transicion de amanecer")
            
            building_elements = self.background_handler.get_elements_by_type("building_silhouette")
            print(f"DEBUG: Configurando transicion para {len(building_elements)} edificios")
            for building in building_elements:
                self.start_building_day_transition(building)
            
            road_elements = self.background_handler.get_elements_by_type("road")
            print(f"DEBUG: Configurando transicion para {len(road_elements)} carreteras")
            for road in road_elements:
                self.start_road_day_transition(road)
            
            print("DEBUG: Programando inicio de monitor_sun_ascent en 100ms")
            self.canvas.after(100, self.monitor_sun_ascent)
            
        except Exception as e:
            print(f"ERROR: No se pudo agregar el sol: {e}")
            self.canvas.after(1000, self.complete_transition_to_menu)
    
    def start_building_day_transition(self, building):
        current_color = building.base_color
        
        day_colors_map = {
            "#3a3a4a": "#8a8a9a", "#4a3a3a": "#9a8a8a", "#3a4a3a": "#8a9a8a", "#4a3a4a": "#9a8a9a",
            "#3a4a4a": "#8a9a9a", "#4a4a3a": "#9a9a8a", "#454545": "#959595", "#3d3d50": "#8d8da0",
            "#353540": "#757580", "#403535": "#807575", "#354035": "#758075", "#403540": "#807580",
            "#354040": "#758080", "#404035": "#808075", "#3a3a3a": "#7a7a7a", "#353545": "#757585",
            "#1a1a25": "#6a6a75", "#251a1a": "#756a6a", "#1a251a": "#6a756a", "#251a25": "#756a75",
            "#1a2525": "#6a7575", "#25251a": "#75756a", "#202020": "#707070", "#1a1a2a": "#6a6a7a"
        }
        
        target_color = day_colors_map.get(current_color, "#808080")
        
        building.is_transitioning_color = True
        building.start_color = current_color
        building.target_color = target_color
        building.transition_progress = 0.0
        
        print(f"DEBUG: Edificio {building.layer} iniciando transicion de {current_color} a {target_color}")
    
    def start_road_day_transition(self, road):
        road.target_road_color = "#4a4a4a"
        road.target_line_color = "#8a8a8a"
        
        road.is_transitioning_color = True
        road.start_road_color = road.road_color
        road.start_line_color = road.line_color
        road.transition_progress = 0.0
        
        print(f"DEBUG: Carretera iniciando transicion de {road.start_road_color} a {road.target_road_color}")
        print(f"DEBUG: Lineas de {road.start_line_color} a {road.target_line_color}")
    
    def monitor_sun_ascent(self):
        print("DEBUG: monitor_sun_ascent ejecutandose")
    
        if not self.toDay_transition_started:
            print("DEBUG: toDay_transition_started es False, terminando monitor")
            return
    
        sun_elements = self.background_handler.get_elements_by_type("sun")
        if not sun_elements:
            print("DEBUG: No se encontro sol, terminando transicion")
            self.complete_transition_to_menu()
            return
    
        sun = sun_elements[0]
    
        if hasattr(sun, 'target_y') and hasattr(sun, 'y'):
            initial_y = self.screen_height + 120
            current_y = sun.y
            target_y = sun.target_y
        
            if initial_y != target_y:
                progress = max(0.0, min(1.0, (initial_y - current_y) / (initial_y - target_y)))
                self.update_color_transitions(progress)
    
        if hasattr(sun, 'target_y'):
            distance_to_target = abs(sun.y - sun.target_y)
            if distance_to_target < 5:
                if self.background_handler.night_bg_manager:
                    self.background_handler.night_bg_manager.capture_final_transition_state()
            
                self.complete_transition_to_menu()
                return
    
        self.canvas.after(16, self.monitor_sun_ascent)
    
    def update_color_transitions(self, progress):
        if progress <= 0.3:
            phase_progress = progress / 0.3
            self.apply_dawn_tint(phase_progress * 0.2)
        elif progress <= 0.7:
            phase_progress = (progress - 0.3) / 0.4
            self.update_building_illumination(phase_progress * 0.5)
            self.update_road_illumination(phase_progress * 0.5)
        else:
            phase_progress = (progress - 0.7) / 0.3
            self.update_building_illumination(0.5 + phase_progress * 0.5)
            self.update_road_illumination(0.5 + phase_progress * 0.5)
        
        self.update_sky_transition(progress)
        
        if int(progress * 20) != getattr(self, '_last_debug_step', -1):
            self._last_debug_step = int(progress * 20)
            phase = "Aparicion" if progress <= 0.3 else "Iluminacion" if progress <= 0.7 else "Finalizacion"
            print(f"DEBUG: Fase {phase} - Progreso: {progress:.3f}")
    
    def apply_dawn_tint(self, intensity):
        if intensity > 0.1:
            print(f"DEBUG: Aplicando tinte de amanecer: {intensity:.2f}")
    
    def update_building_illumination(self, illumination_progress):
        building_elements = self.background_handler.get_elements_by_type("building_silhouette")
        for building in building_elements:
            if hasattr(building, 'is_transitioning_color') and building.is_transitioning_color:
                building.transition_progress = illumination_progress
                building.update_color_transition()
    
    def update_road_illumination(self, illumination_progress):
        road_elements = self.background_handler.get_elements_by_type("road")
        for road in road_elements:
            if hasattr(road, 'is_transitioning_color') and road.is_transitioning_color:
                road.transition_progress = illumination_progress
                road.update_color_transition()
    
    def update_sky_transition(self, progress):
        sky_elements = self.background_handler.get_elements_by_type("night_sky")
        for sky in sky_elements:
            if hasattr(sky, 'update_dawn_transition'):
                sun_elements = self.background_handler.get_elements_by_type("sun")
                if sun_elements:
                    sun = sun_elements[0]
                    sky.update_dawn_transition(sun.y, sun.target_y)
    
    def complete_transition_to_menu(self):
        print("DEBUG: Transicion toDay completada, pasando al menu")
        print("DEBUG: Estado final deberia estar capturado para uso en fondo diurno")
        
        self.background_handler.toDay_transition_completed = True
        
        if self.background_handler.day_bg_manager:
            self.background_handler.day_bg_manager.enable_cloud_spawning()
            print("DEBUG: Sistema de nubes activado antes de cambiar al menu")
        
        if self.is_visible:
            self.transition_to('menu', 'fade', 1.0)
    
    def on_hide(self):
        self.canvas.unbind('<KeyPress>')
        self.canvas.unbind('<Button-1>')
        
        self.clear_ui_elements()
    
    def on_update(self):
        pass
