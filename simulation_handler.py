import tkinter as tk
import time
from screen_element import ButtonElement
from simulation_vehicles import SimulationVehicleManager

class SimulationHandler:
    def __init__(self, canvas, screen_width, screen_height, sim_area_x, sim_area_y, sim_area_width, sim_area_height):
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.sim_area_x = sim_area_x
        self.sim_area_y = sim_area_y
        self.sim_area_width = sim_area_width
        self.sim_area_height = sim_area_height
        
        self.simulation_active = False
        self.simulation_paused = False
        
        self.start_button = None
        self.pause_button = None
        
        self.control_buttons = []
        
        self.animation_id = None
        self.last_update_time = time.time()
        
        self.simulation_vehicles = []
        
        self.vehicle_manager = SimulationVehicleManager(
            sim_area_x, sim_area_y, sim_area_width, sim_area_height
        )
        
        self.button_y = 35
        self.button_width = 90
        self.button_height = 22
        self.button_spacing = 15
        
        self.traffic_light_state = "left_go"
        self.traffic_light_timer = 0
        self.traffic_light_duration = 10.0
        self.transition_duration = 3.0
        self.is_transitioning = False
        self.transition_timer = 0
        
        self.simulator_screen = None
        
    def set_simulator_screen(self, simulator_screen):
        self.simulator_screen = simulator_screen
        
    def create_control_buttons(self):
        center_x = self.screen_width // 2
        
        self.start_button = ButtonElement(
            self.canvas,
            center_x - self.button_width - self.button_spacing // 2,
            self.button_y,
            self.button_width,
            self.button_height,
            "INICIAR"
        )
        self.start_button.set_colors(
            bg_color="#4CAF50",
            hover_bg="#5CBF60",
            pressed_bg="#45A049"
        )
        self.start_button.on_click = self.toggle_simulation
        self.control_buttons.append(self.start_button)
        
        return self.control_buttons
    
    def toggle_simulation(self, button, event=None):
        if not self.simulation_active:
            self.start_simulation()
        else:
            self.clear_simulation()
    
    def start_simulation(self):
        print("DEBUG: Iniciando simulacion")
        self.simulation_active = True
        self.simulation_paused = False
        
        self.start_button.set_text("BORRAR")
        self.start_button.set_colors(
            bg_color="#F44336",
            hover_bg="#EF5350",
            pressed_bg="#D32F2F"
        )
        
        center_x = self.screen_width // 2
        left_button_x = center_x - self.button_width - self.button_spacing // 2
        
        self.start_button.set_position(left_button_x, self.button_y)
        
        self.pause_button = ButtonElement(
            self.canvas,
            center_x + self.button_spacing // 2,
            self.button_y,
            self.button_width,
            self.button_height,
            "PAUSAR"
        )
        self.pause_button.set_colors(
            bg_color="#FF9800",
            hover_bg="#FFB74D",
            pressed_bg="#F57C00"
        )
        self.pause_button.on_click = self.toggle_pause
        
        for item_id in self.pause_button.element_ids:
            try:
                self.canvas.itemconfig(item_id, tags=("simulator_ui", "ui_element"))
            except:
                pass
        
        self.control_buttons.append(self.pause_button)
        
        try:
            self.canvas.update_idletasks()
        except:
            pass
        
        print(f"DEBUG: Boton de pausa creado con {len(self.pause_button.element_ids)} elementos")
        
        self.initialize_traffic_lights()
        
        self.setup_static_layering()
        
        self.last_update_time = time.time()
        self.start_simulation_loop()
    
    def initialize_traffic_lights(self):
        self.traffic_light_state = "left_go"
        self.traffic_light_timer = 0
        self.is_transitioning = False
        self.transition_timer = 0
        
        if self.simulator_screen:
            self.simulator_screen.set_traffic_light_state("left_go")
            self.simulator_screen.update_timer(int(self.get_traffic_light_duration()))
    
    def toggle_pause(self, button, event=None):
        if self.simulation_paused:
            self.resume_simulation()
        else:
            self.pause_simulation()
    
    def pause_simulation(self):
        print("DEBUG: Pausando simulacion")
        self.simulation_paused = True
        
        if self.pause_button:
            self.pause_button.set_text("REANUDAR")
            self.pause_button.set_colors(
                bg_color="#FFEB3B",
                hover_bg="#FFF176",
                pressed_bg="#FDD835"
            )
        
        if self.simulator_screen:
            current_remaining = max(0, self.get_traffic_light_duration() - self.traffic_light_timer)
            self.simulator_screen.update_timer(int(current_remaining))
    
    def resume_simulation(self):
        print("DEBUG: Reanudando simulacion")
        self.simulation_paused = False
        self.last_update_time = time.time()
        
        if self.pause_button:
            self.pause_button.set_text("PAUSAR")
            self.pause_button.set_colors(
                bg_color="#FF9800",
                hover_bg="#FFB74D",
                pressed_bg="#F57C00"
            )
        
        if self.simulator_screen:
            if self.is_transitioning:
                remaining_transition = max(0, self.transition_duration - self.transition_timer)
                transition_seconds = int(remaining_transition) + 1
                if transition_seconds == 3:
                    self.simulator_screen.update_timer_text("...")
                elif transition_seconds == 2:
                    self.simulator_screen.update_timer_text("..")
                elif transition_seconds == 1:
                    self.simulator_screen.update_timer_text(".")
            else:
                current_remaining = max(0, self.get_traffic_light_duration() - self.traffic_light_timer)
                self.simulator_screen.update_timer(int(current_remaining))
    
    def clear_simulation(self):
        print("DEBUG: Limpiando simulacion")
        
        if self.animation_id:
            try:
                self.canvas.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
        
        self.simulation_active = False
        self.simulation_paused = False
        
        if self.vehicle_manager:
            self.vehicle_manager.clear_all()
        
        try:
            self.canvas.delete("simulation_vehicle")
        except:
            pass
        
        if self.pause_button:
            try:
                self.pause_button.delete_element()
            except:
                pass
            if self.pause_button in self.control_buttons:
                self.control_buttons.remove(self.pause_button)
            self.pause_button = None
        
        if self.start_button:
            center_x = self.screen_width // 2
            self.start_button.set_position(
                center_x - self.button_width - self.button_spacing // 2,
                self.button_y
            )
            self.start_button.set_text("INICIAR")
            self.start_button.set_colors(
                bg_color="#4CAF50",
                hover_bg="#5CBF60",
                pressed_bg="#45A049"
            )
        
        if self.simulator_screen:
            self.simulator_screen.set_traffic_light_state("off")
            self.simulator_screen.update_timer(-1)
        
        self.traffic_light_state = "left_go"
        self.traffic_light_timer = 0
        self.is_transitioning = False
        self.transition_timer = 0
        
        self.simulation_vehicles.clear()
        
        try:
            self.canvas.update_idletasks()
        except:
            pass
        
        print("DEBUG: Simulacion limpiada completamente")
    
    def start_simulation_loop(self):
        if self.simulation_active:
            self.animation_id = self.canvas.after(16, self.update_simulation)
    
    def update_simulation(self):
        if not self.simulation_active:
            return
        
        if not self.simulation_paused:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
            
            self.update_traffic_lights(delta_time)
            self.update_simulation_logic(delta_time)
        else:
            self.last_update_time = time.time()
        
        self.start_simulation_loop()
    
    def update_traffic_lights(self, delta_time):
        if not self.simulator_screen:
            return
        
        if self.is_transitioning:
            self.transition_timer += delta_time
            
            remaining_transition = max(0, self.transition_duration - self.transition_timer)
            transition_seconds = int(remaining_transition) + 1
            
            if transition_seconds == 3:
                self.simulator_screen.update_timer_text("...")
            elif transition_seconds == 2:
                self.simulator_screen.update_timer_text("..")
            elif transition_seconds == 1:
                self.simulator_screen.update_timer_text(".")
            
            if self.transition_timer >= self.transition_duration:
                self.complete_transition()
        else:
            self.traffic_light_timer += delta_time
            
            remaining_time = max(0, self.get_traffic_light_duration() - self.traffic_light_timer)
            remaining_seconds = int(remaining_time)
            
            self.simulator_screen.update_timer(remaining_seconds)
            
            if self.traffic_light_timer >= self.get_traffic_light_duration():
                self.start_transition()
    
    def start_transition(self):
        print("DEBUG: Iniciando transicion de semaforo (solo visual)")
        self.is_transitioning = True
        self.transition_timer = 0
        
        if self.simulator_screen:
            self.simulator_screen.set_traffic_light_state("caution")
            self.simulator_screen.update_timer_text("...")
    
    def complete_transition(self):
        print("DEBUG: Completando transicion de semaforo (solo visual)")
        self.is_transitioning = False
        self.transition_timer = 0
        self.traffic_light_timer = 0
        
        if self.traffic_light_state == "left_go":
            self.traffic_light_state = "right_go"
        else:
            self.traffic_light_state = "left_go"
        
        if self.simulator_screen:
            self.simulator_screen.set_traffic_light_state(self.traffic_light_state)
            self.simulator_screen.update_timer(int(self.get_traffic_light_duration()))
    
    def get_traffic_light_duration(self):
        return self.traffic_light_duration
    
    def update_simulation_logic(self, delta_time):
        if self.vehicle_manager:
            self.vehicle_manager.update(delta_time)
            
            for vehicle in self.vehicle_manager.get_vehicles():
                vehicle.update(delta_time)
                vehicle.draw(self.canvas)
    
    def setup_static_layering(self):
        """Establece el orden de capas UNA sola vez al iniciar la simulacion"""
        try:
            self.canvas.tag_lower('container_border')
            self.canvas.tag_raise('background_layer', 'container_border')
            self.canvas.tag_raise('road_layer', 'background_layer')
            self.canvas.tag_raise('vehicle_layer', 'road_layer')
            self.canvas.tag_raise('grid_layer', 'vehicle_layer')
            self.canvas.tag_raise('border_layer', 'grid_layer')
            self.canvas.tag_raise('ui_element', 'border_layer')
            
            print("DEBUG: Orden de capas estatico establecido")
            print("DEBUG: Orden final (abajo -> arriba):")
            print("  1. container_border")
            print("  2. background_layer (fondo diurno)")
            print("  3. road_layer (carretera simulador)")
            print("  4. vehicle_layer (vehiculos)")
            print("  5. grid_layer (cuadricula)")
            print("  6. border_layer (bordes)")
            print("  7. ui_element (botones)")
        except Exception as e:
            print(f"ERROR al establecer layering estatico: {e}")
    
    def cleanup(self):
        print("DEBUG: Limpiando simulation_handler")
        
        if self.animation_id:
            try:
                self.canvas.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
        
        if self.vehicle_manager:
            self.vehicle_manager.clear_all()
        
        try:
            self.canvas.delete("simulation_vehicle")
        except:
            pass
        
        for button in self.control_buttons[:]:
            try:
                button.cleanup()
            except:
                pass
        
        self.control_buttons.clear()
        self.start_button = None
        self.pause_button = None
        
        self.simulation_vehicles.clear()
        
        self.simulation_active = False
        self.simulation_paused = False
        
        print("DEBUG: simulation_handler limpiado completamente")
    
    def get_buttons(self):
        return self.control_buttons
    
    def is_active(self):
        return self.simulation_active
    
    def is_paused(self):
        return self.simulation_paused
