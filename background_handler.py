import tkinter as tk
import time
import random
from background_element import BackgroundElement

try:
    from night_background_elements import NightBackgroundManager
    NIGHT_BG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: No se pudo importar night_background_elements: {e}")
    NIGHT_BG_AVAILABLE = False
try:
    from day_background_elements import DayBackgroundManager
    DAY_BG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: No se pudo importar day_background_elements: {e}")
    DAY_BG_AVAILABLE = False

try:
    from background_timer_system import BackgroundTimerSystem
    TIMER_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: No se pudo importar background_timer_system: {e}")
    TIMER_SYSTEM_AVAILABLE = False

class BackgroundHandler:
    def __init__(self, canvas, screen_width, screen_height):
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.background_elements = []
        self.animation_active = False
        self.last_update_time = time.time()
        self.animation_id = None
        
        self.transition_active = False
        self.transition_progress = 0.0
        self.transition_duration = 1.0
        self.transition_callback = None
        self.transition_type = None
        
        self.current_background_state = None
        self.background_states = ["loading", "transition", "toDay", "day"]
        
        self.current_background_type = None
        
        self.debug_enabled = False
        
        if NIGHT_BG_AVAILABLE:
            self.night_bg_manager = NightBackgroundManager(screen_width, screen_height)
        else:
            self.night_bg_manager = None
        
        if DAY_BG_AVAILABLE:
            self.day_bg_manager = DayBackgroundManager(screen_width, screen_height)
        else:
            self.day_bg_manager = None
        
        self.cached_day_background = None
        
        if TIMER_SYSTEM_AVAILABLE:
            self.timer_system = BackgroundTimerSystem()
            self.setup_star_twinkling_system()
        else:
            self.timer_system = None
        
        self.cursor_handler = None
        
        self.toDay_transition_completed = False
    
    def debug_print(self, message):
        if self.debug_enabled:
            print(message)
    
    def set_debug(self, enabled):
        self.debug_enabled = enabled
    
    def setup_star_twinkling_system(self):
        if not self.timer_system:
            return
        
        self.timer_system.add_random_timer(
            "star_twinkle_trigger",
            min_duration=0.5,
            max_duration=3.0,
            callback=self.trigger_random_star_twinkle,
            repeat=True
        )
    
    def trigger_random_star_twinkle(self):
        stars = self.get_elements_by_type("star")
        if stars:
            random_star = random.choice(stars)
            if hasattr(random_star, 'start_twinkling'):
                random_star.start_twinkling()
    
    def set_cursor_handler(self, cursor_handler):
        self.cursor_handler = cursor_handler
        
    def add_background_element(self, element):
        if isinstance(element, BackgroundElement):
            self.background_elements.append(element)
    
    def remove_background_element(self, element):
        if element in self.background_elements:
            self.background_elements.remove(element)
    
    def clear_background_elements(self):
        self.debug_print(f"DEBUG: Limpiando {len(self.background_elements)} elementos de fondo")
        
        # NO desactivar vehiculos ni nubes
        for element in self.background_elements[:]:
            if element.element_type not in ["vehicle", "cloud"]:
                element.deactivate()
        
        # Solo mantener vehiculos y nubes en la lista
        vehicles_and_clouds = [e for e in self.background_elements if e.element_type in ["vehicle", "cloud"]]
        self.background_elements = vehicles_and_clouds
        
        self.canvas.delete("background_layer")
        
        self.debug_print(f"DEBUG: {len(vehicles_and_clouds)} vehiculos y nubes preservados")
    
    def set_background_state(self, state):
        self.debug_print(f"DEBUG: set_background_state llamado con: {state}")
        if state in self.background_states:
            self.current_background_state = state
            self.debug_print(f"DEBUG: Estado establecido, llamando create_state_background")
            self.create_state_background(state)
        else:
            self.debug_print(f"DEBUG: Estado {state} no valido. Estados disponibles: {self.background_states}")
    
    def create_state_background(self, state):
        self.debug_print(f"DEBUG: create_state_background llamado con: {state}")
    
        if state == "day":
            active_day_elements = [e for e in self.background_elements if e.element_type in ["day_sky", "day_sun", "day_building", "day_road"] and e.is_active()]
            active_clouds = [e for e in self.background_elements if e.element_type == "cloud" and e.is_active()]
            active_vehicles = [e for e in self.background_elements if e.element_type == "vehicle" and e.is_active()]
            
            if len(active_day_elements) > 0:
                self.debug_print(f"DEBUG: Fondo diurno ya activo con {len(active_day_elements)} elementos + {len(active_clouds)} nubes + {len(active_vehicles)} vehiculos")
                self.set_canvas_background_color('#87CEEB')
                
                if self.day_bg_manager and self.toDay_transition_completed:
                    if not self.day_bg_manager.cloud_spawn_enabled:
                        self.day_bg_manager.enable_cloud_spawning()
                        self.debug_print("DEBUG: Sistema de nubes reactivado en fondo existente")
                
                return
            
            if self.cached_day_background and len(self.cached_day_background) > 0:
                self.debug_print(f"DEBUG: Reutilizando cache existente de {len(self.cached_day_background)} elementos")
            
                clouds_in_background = [e for e in self.background_elements if e.element_type == "cloud"]
                vehicles_in_background = [e for e in self.background_elements if e.element_type == "vehicle"]
                self.debug_print(f"DEBUG: Hay {len(clouds_in_background)} nubes y {len(vehicles_in_background)} vehiculos activos")
                
                non_shared_elements = [e for e in self.background_elements if e.element_type not in ["cloud", "vehicle"]]
                cached_count = len([e for e in non_shared_elements if e.is_active()])
                
                if cached_count >= len(self.cached_day_background) - 5:
                    self.debug_print(f"DEBUG: Cache ya esta activo ({cached_count} elementos), preservando estado")
                    self.set_canvas_background_color('#87CEEB')
                    
                    if self.day_bg_manager and self.toDay_transition_completed:
                        if not self.day_bg_manager.cloud_spawn_enabled:
                            self.day_bg_manager.enable_cloud_spawning()
                            self.debug_print("DEBUG: Sistema de nubes reactivado")
                    
                    return
            
                self.debug_print(f"DEBUG: Recreando fondo desde cache")
                
                # PRESERVAR nubes y vehiculos
                elements_to_preserve = [e for e in self.background_elements if e.element_type in ["cloud", "vehicle"] and e.is_active()]
                self.debug_print(f"DEBUG: Preservando {len(elements_to_preserve)} elementos compartidos (nubes y vehiculos)")
                
                # Desactivar solo elementos que NO son nubes ni vehiculos
                for element in self.background_elements[:]:
                    if element.element_type not in ["cloud", "vehicle"]:
                        element.deactivate()
                
                self.background_elements = elements_to_preserve.copy()
                self.canvas.delete("background_layer")
            
                for element in self.cached_day_background:
                    if element.element_type not in ["cloud", "vehicle"]:
                        element.activate()
                        element.show()
                        self.add_background_element(element)
            
                self.set_canvas_background_color('#87CEEB')
                
                if self.day_bg_manager and self.toDay_transition_completed:
                    if not self.day_bg_manager.cloud_spawn_enabled:
                        self.day_bg_manager.enable_cloud_spawning()
                        self.debug_print("DEBUG: Sistema de nubes reactivado tras recreacion")
                
                self.draw_background()
                return
    
        if state == "day" and self.night_bg_manager and hasattr(self.night_bg_manager, 'final_transition_state') and self.night_bg_manager.final_transition_state:
            self.debug_print(f"DEBUG: Estado final disponible para fondo diurno, creando por primera vez")
            
            # PRESERVAR vehiculos existentes antes de limpiar
            vehicles_to_preserve = [e for e in self.background_elements if e.element_type == "vehicle" and e.is_active()]
            self.debug_print(f"DEBUG: Preservando {len(vehicles_to_preserve)} vehiculos antes de crear fondo diurno")
            
            if len(self.background_elements) > 0:
                self.debug_print(f"DEBUG: Limpiando {len(self.background_elements)} elementos existentes para aplicar estado final")
                # Limpiar solo elementos que NO son vehiculos
                for element in self.background_elements[:]:
                    if element.element_type != "vehicle":
                        element.deactivate()
                self.background_elements = vehicles_to_preserve.copy()
                self.canvas.delete("background_layer")
            
            self.debug_print("DEBUG: Llamando create_day_state_background con estado final")
            self.create_day_state_background()
            return
    
        if self.current_background_state == state and len(self.background_elements) > 0:
            self.debug_print(f"DEBUG: Ya tenemos el fondo {state} con {len(self.background_elements)} elementos")
            active_count = len([e for e in self.background_elements if e.is_active()])
            if active_count > 0:
                self.debug_print(f"DEBUG: {active_count} elementos activos, no recreando")
                return
            else:
                self.debug_print(f"DEBUG: No hay elementos activos, recreando fondo")
    
        # PRESERVAR vehiculos antes de limpiar
        vehicles_to_preserve = [e for e in self.background_elements if e.element_type == "vehicle" and e.is_active()]
        
        if len(self.background_elements) > 0:
            self.debug_print(f"DEBUG: Limpiando {len(self.background_elements)} elementos existentes (preservando {len(vehicles_to_preserve)} vehiculos)")
            for element in self.background_elements[:]:
                if element.element_type != "vehicle":
                    element.deactivate()
            self.background_elements = vehicles_to_preserve.copy()
    
        if state == "loading":
            self.debug_print("DEBUG: Llamando create_loading_state_background")
            self.create_loading_state_background()
        elif state == "transition":
            self.debug_print("DEBUG: Llamando create_transition_state_background")
            self.create_transition_state_background()
        elif state == "toDay":
            self.debug_print("DEBUG: Llamando create_toDay_state_background")
            self.create_toDay_state_background()
        elif state == "day":
            self.debug_print("DEBUG: Llamando create_day_state_background")
            self.create_day_state_background()
        else:
            self.debug_print(f"DEBUG: Estado {state} no reconocido")
    
    def set_canvas_background_color(self, color):
        try:
            self.canvas.configure(bg=color)
            self.debug_print(f"DEBUG: Color de fondo del canvas cambiado a {color}")
        except Exception as e:
            self.debug_print(f"ERROR: No se pudo cambiar color de fondo del canvas: {e}")
    
    def create_loading_state_background(self):
        self.debug_print("DEBUG: Creando fondo de loading...")
        
        self.set_canvas_background_color('#0a0a1e')
        
        if self.night_bg_manager is None:
            self.debug_print("DEBUG: night_bg_manager no disponible, usando fondo por defecto")
            self.create_solid_background("#1a1a1a")
            return
        
        try:
            elements = self.night_bg_manager.create_loading_background_elements()
            self.debug_print(f"DEBUG: Se crearon {len(elements)} elementos de fondo")
            
            for i, element in enumerate(elements):
                self.add_background_element(element)
                self.debug_print(f"DEBUG: Agregado elemento {i}: {element.element_type}")
                
        except Exception as e:
            self.debug_print(f"ERROR: No se pudo crear el fondo nocturno: {e}")
            self.create_solid_background("#1a1a1a")
    
    def create_toDay_state_background(self):
        self.debug_print("DEBUG: Creando fondo toDay...")
        
        if self.night_bg_manager is None:
            self.debug_print("DEBUG: night_bg_manager no disponible, usando fondo por defecto")
            self.create_solid_background("#2a2a6a")
            return
        
        try:
            elements = self.night_bg_manager.create_toDay_background_elements()
            self.debug_print(f"DEBUG: Se crearon {len(elements)} elementos de fondo toDay")
            
            for i, element in enumerate(elements):
                self.add_background_element(element)
                self.debug_print(f"DEBUG: Agregado elemento toDay {i}: {element.element_type}")
            
            self.start_toDay_transition()
                
        except Exception as e:
            self.debug_print(f"ERROR: No se pudo crear el fondo toDay: {e}")
            self.create_solid_background("#2a2a6a")
    
    def start_toDay_transition(self):
        self.debug_print("DEBUG: Iniciando transicion toDay")
        
        sky_elements = self.get_elements_by_type("night_sky") + self.get_elements_by_type("toDay_sky")
        sun_elements = self.get_elements_by_type("sun")
        building_elements = self.get_elements_by_type("building_silhouette") + self.get_elements_by_type("toDay_building")
        road_elements = self.get_elements_by_type("road") + self.get_elements_by_type("toDay_road")
        
        for sky in sky_elements:
            if hasattr(sky, 'start_dawn_transition'):
                sky.start_dawn_transition()
        
        for sun in sun_elements:
            if hasattr(sun, 'start_sunrise'):
                sun.start_sunrise()
        
        for building in building_elements:
            if hasattr(building, 'start_day_illumination'):
                building.start_day_illumination()
        
        for road in road_elements:
            if hasattr(road, 'start_day_illumination'):
                road.start_day_illumination()
        
        def complete_toDay_transition():
            self.debug_print("DEBUG: Completando transicion toDay")
            self.toDay_transition_completed = True
            if self.night_bg_manager:
                self.night_bg_manager.capture_final_transition_state()
            
            if self.day_bg_manager:
                self.day_bg_manager.enable_cloud_spawning()
                self.debug_print("DEBUG: Sistema de nubes activado")
        
        if self.timer_system:
            self.timer_system.add_timer("toDay_transition_complete", 12.0, complete_toDay_transition, False)
    
    def create_transition_state_background(self):
        self.debug_print("DEBUG: Transicion sin crear fondo adicional")
    
    def create_day_state_background(self):
        self.debug_print("DEBUG: Creando fondo diurno...")
    
        self.set_canvas_background_color('#87CEEB')
    
        if self.cached_day_background and len(self.cached_day_background) > 0:
            self.debug_print(f"DEBUG: Reutilizando fondo diurno cacheado con {len(self.cached_day_background)} elementos")
            for element in self.cached_day_background:
                element.activate()
                element.show()
                self.add_background_element(element)
            
            if self.day_bg_manager and self.toDay_transition_completed:
                if not self.day_bg_manager.cloud_spawn_enabled:
                    self.day_bg_manager.enable_cloud_spawning()
                    self.debug_print("DEBUG: Sistema de nubes activado en cache reutilizado")
            
            self.draw_background()
            return
    
        if not self.day_bg_manager:
            self.debug_print("DEBUG: day_bg_manager no disponible")
            self.create_gradient_background("#87CEEB", "#B0E0E6", "vertical")
            return
    
        try:
            if self.night_bg_manager and hasattr(self.night_bg_manager, 'final_transition_state') and self.night_bg_manager.final_transition_state:
                self.debug_print("DEBUG: Usando estado de transicion para crear fondo diurno")
                elements = self.day_bg_manager.create_from_transition_state(self.night_bg_manager.final_transition_state)
            else:
                self.debug_print("DEBUG: Creando fondo diurno estandar (sin estado de transicion)")
                elements = self.day_bg_manager.create_day_background()
        
            for element in elements:
                self.add_background_element(element)
        
            self.cached_day_background = elements.copy()
            
            if self.toDay_transition_completed:
                self.day_bg_manager.enable_cloud_spawning()
                self.debug_print("DEBUG: Sistema de nubes activado en primera creacion de fondo diurno")
        
            self.draw_background()
        
        except Exception as e:
            self.debug_print(f"ERROR: No se pudo crear el fondo diurno: {e}")
            import traceback
            self.debug_print(traceback.format_exc())
    
    def set_background_type(self, background_type):
        self.debug_print(f"DEBUG: set_background_type llamado con: {background_type}")
        self.current_background_type = background_type
        
        if background_type == "loading":
            self.debug_print(f"DEBUG: Usando fondo nocturno para {background_type}")
            self.set_background_state("loading")
        elif background_type in ["menu", "simulator", "exit"]:
            self.debug_print(f"DEBUG: Verificando fondo diurno para {background_type}")
            
            if self.current_background_state == "day":
                active_day_elements = [e for e in self.background_elements 
                                      if e.element_type in ["day_sky", "day_sun", "day_building", "day_road"] 
                                      and e.is_active()]
                
                if len(active_day_elements) > 10:
                    self.debug_print(f"DEBUG: Fondo diurno YA ACTIVO ({len(active_day_elements)} elementos), NO RECREAR")
                    self.set_canvas_background_color('#87CEEB')
                    
                    # Asegurar que el sistema de vehiculos siga activo
                    if self.day_bg_manager and self.toDay_transition_completed:
                        if not self.day_bg_manager.cloud_spawn_enabled:
                            self.day_bg_manager.enable_cloud_spawning()
                            self.debug_print("DEBUG: Sistema de nubes reactivado")
                        
                        active_vehicles = len([e for e in self.background_elements if e.element_type == "vehicle" and e.is_active()])
                        self.debug_print(f"DEBUG: Hay {active_vehicles} vehiculos activos")
                    return
            
            self.debug_print(f"DEBUG: Creando fondo diurno para {background_type}")
            self.set_background_state("day")
        else:
            self.debug_print(f"DEBUG: Tipo de fondo {background_type} no encontrado en mapeo")
    
    def start_animation(self):
        self.animation_active = True
        self.last_update_time = time.time()
        self._schedule_next_frame()
    
    def _schedule_next_frame(self):
        """Programa el siguiente frame de animacion de forma segura"""
        if self.animation_active:
            try:
                self.animation_id = self.canvas.after(16, lambda: self._animate_frame())
            except (tk.TclError, AttributeError):
                self.animation_active = False
                self.animation_id = None
    
    def _animate_frame(self):
        """Frame individual de animacion"""
        if not self.animation_active:
            self.animation_id = None
            return

        try:
            if not self.canvas.winfo_exists():
                self.animation_active = False
                self.animation_id = None
                return
                
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time

            for element in self.background_elements[:]:
                if element.is_active():
                    element.update(delta_time)
        
                if not element.is_active():
                    self.background_elements.remove(element)

            if self.transition_active:
                self.update_transition(delta_time)

            if self.timer_system:
                self.timer_system.update(delta_time)

            if self.day_bg_manager and self.current_background_state == "day":
                self.day_bg_manager.update_clouds(delta_time)
                
                for cloud in self.day_bg_manager.active_clouds:
                    if cloud not in self.background_elements and cloud.is_active():
                        self.add_background_element(cloud)
                
                new_vehicles = self.day_bg_manager.update_vehicles(delta_time, self.background_elements)
                for vehicle in new_vehicles:
                    if vehicle not in self.background_elements:
                        self.add_background_element(vehicle)

            self.draw_background()

            self._schedule_next_frame()
            
        except tk.TclError:
            self.animation_active = False
            self.animation_id = None
        except Exception as e:
            self.debug_print(f"ERROR en animate: {e}")
            self.animation_active = False
            self.animation_id = None
    
    def stop_animation(self):
        """Detener animaciones de forma segura"""
        self.animation_active = False
        if self.animation_id:
            try:
                self.canvas.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
    
    def draw_background(self):
        if not self.animation_active:
            return
        
        if len(self.background_elements) == 0:
            return

        active_elements = [element for element in self.background_elements if element.is_active()]

        if len(active_elements) == 0:
            return

        if random.random() < 0.001:
            self.debug_print(f"DEBUG: Dibujando {len(active_elements)} elementos activos")

        sorted_elements = sorted(active_elements, key=lambda x: x.get_depth())

        for element in sorted_elements:
            if element.is_visible():
                try:
                    element.draw(self.canvas)
                except tk.TclError:
                    self.animation_active = False
                    return
                except Exception as e:
                    self.debug_print(f"ERROR: No se pudo dibujar elemento {element.element_type}: {e}")

        # CORREGIDO: Solo bajar elementos estaticos del fondo, NO vehiculos ni nubes
        try:
            # Bajar solo cielo, edificios y carretera
            self.canvas.tag_lower("background_layer")
            # Subir vehiculos y nubes para que siempre esten visibles
            for element in active_elements:
                if element.element_type in ["vehicle", "cloud"]:
                    for item_id in getattr(element, 'canvas_items', []):
                        try:
                            self.canvas.tag_raise(item_id)
                        except:
                            pass
            # AGREGAR ESTA LINEA:
            self.canvas.tag_raise("ui_element")
        except tk.TclError:
            self.animation_active = False
        except:
            pass
    
    def start_transition(self, transition_type, duration=1.0, callback=None):
        self.transition_active = True
        self.transition_progress = 0.0
        self.transition_duration = duration
        self.transition_callback = callback
        self.transition_type = transition_type
    
    def update_transition(self, delta_time):
        self.transition_progress += delta_time / self.transition_duration
        
        if self.transition_progress >= 1.0:
            self.transition_progress = 1.0
            self.transition_active = False
            
            if self.transition_callback:
                self.transition_callback()
                self.transition_callback = None
        
        self.apply_transition_effect()
    
    def apply_transition_effect(self):
        if self.transition_type == "fade":
            self.apply_fade_effect()
        elif self.transition_type == "slide_up":
            self.apply_slide_up_effect()
        elif self.transition_type == "slide_down":
            self.apply_slide_down_effect()
    
    def apply_fade_effect(self):
        alpha = 1.0 - self.transition_progress
        for element in self.background_elements:
            if element.element_type not in ["cloud", "vehicle"]:
                element.set_opacity(alpha)
    
    def apply_slide_up_effect(self):
        offset_y = -self.screen_height * self.transition_progress
        for element in self.background_elements:
            if element.element_type not in ["cloud", "vehicle"]:
                element.set_offset(0, offset_y)
    
    def apply_slide_down_effect(self):
        offset_y = self.screen_height * self.transition_progress
        for element in self.background_elements:
            if element.element_type not in ["cloud", "vehicle"]:
                element.set_offset(0, offset_y)
    
    def create_gradient_background(self, color1, color2, direction="vertical"):
        if direction == "vertical":
            for i in range(0, self.screen_height, 10):
                progress = i / self.screen_height
                color = self.interpolate_color(color1, color2, progress)
                self.canvas.create_rectangle(
                    0, i, self.screen_width, i + 10,
                    fill=color, outline="", tags="background_layer"
                )
        elif direction == "horizontal":
            for i in range(0, self.screen_width, 10):
                progress = i / self.screen_width
                color = self.interpolate_color(color1, color2, progress)
                self.canvas.create_rectangle(
                    i, 0, i + 10, self.screen_height,
                    fill=color, outline="", tags="background_layer"
                )
    
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
    
    def create_solid_background(self, color):
        self.canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill=color, outline="", tags="background_layer"
        )
    
    def cleanup(self):
        """Limpieza completa del handler"""
        self.debug_print("DEBUG: Iniciando limpieza completa del background_handler")
        
        self.stop_animation()
        
        try:
            self.canvas.after_cancel('all')
        except:
            pass
        
        if self.day_bg_manager:
            self.day_bg_manager.cloud_spawn_enabled = False
            self.day_bg_manager.active_clouds.clear()
        
        for element in self.background_elements:
            element.deactivate()
        
        self.background_elements.clear()
        self.cached_day_background = None
        
        try:
            self.canvas.delete("background_layer")
        except:
            pass
        
        self.debug_print("DEBUG: Limpieza completa finalizada")
    
    def get_animation_status(self):
        return self.animation_active
    
    def get_transition_progress(self):
        return self.transition_progress if self.transition_active else 1.0
    
    def get_background_state(self):
        return self.current_background_state
    
    def get_elements_by_group(self, group):
        group_tag = f"group_{group.lower()}"
        return [element for element in self.background_elements 
                if element.has_tag(group_tag)]
    
    def get_elements_by_type(self, element_type):
        return [element for element in self.background_elements 
                if element.element_type == element_type]