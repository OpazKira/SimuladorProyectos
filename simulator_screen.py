import tkinter as tk
from screen_handler import ScreenHandler
from screen_element import ScreenElement, ButtonElement
from background_element import BackgroundElement
from simulation_handler import SimulationHandler

class SimulatorScreen(ScreenHandler):
    def __init__(self, canvas, app):
        super().__init__(canvas, app, "simulator")
    
        self.control_buttons = []
        self.info_panel = None
        self.simulation_running = False
    
        self.cursor_handler = app.get_cursor_handler()
    
        self.callbacks_registered = False
    
        self.sim_size = 600
        self.sim_area_x = (self.screen_width - self.sim_size) // 2
        self.sim_area_y = (self.screen_height - self.sim_size) // 2 + 60
        self.sim_area_width = self.sim_size
        self.sim_area_height = self.sim_size
    
        self.timer_text = None
        self.left_light = None
        self.right_light = None
        self.left_arrow = None
        self.right_arrow = None
    
        self.traffic_light_state = "off"
    
        self.simulation_handler = SimulationHandler(
            self.canvas,
            self.screen_width,
            self.screen_height,
            self.sim_area_x,
            self.sim_area_y,
            self.sim_area_width,
            self.sim_area_height
        )
        self.simulation_handler.set_simulator_screen(self)
    
    def setup_cursor_callbacks(self):
        if not self.callbacks_registered:
            self.cursor_handler.add_move_callback(self.on_cursor_move)
            self.cursor_handler.add_click_callback(self.on_cursor_click)
            self.cursor_handler.add_drag_callback(self.on_cursor_drag)
            self.callbacks_registered = True
            print("DEBUG: Simulator callbacks registrados")
    
    def cleanup_cursor_callbacks(self):
        if self.callbacks_registered:
            try:
                self.cursor_handler.remove_move_callback(self.on_cursor_move)
                self.cursor_handler.remove_click_callback(self.on_cursor_click)
                self.cursor_handler.remove_drag_callback(self.on_cursor_drag)
                self.callbacks_registered = False
                print("DEBUG: Simulator callbacks limpiados")
            except Exception as e:
                print(f"DEBUG: Error limpiando callbacks en simulator: {e}")
    
    def create_specific_background(self):
        pass
    
    def create_specific_ui(self):
        self.create_control_panel()
        self.create_simulation_container()
        self.create_simulation_area()
        self.create_timer_and_traffic_lights()
        self.create_back_button()
    
        self.simulation_handler.create_control_buttons()
    
    def create_control_panel(self):
        panel_height = 60
    
        panel_bg = self.canvas.create_rectangle(
            0, 0, self.screen_width, panel_height,
            fill="#1a1a2e",
            outline="",
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(panel_bg)
    
        title = self.canvas.create_text(
            self.screen_width // 2, 20,
            text="Simulador de Trafico",
            fill="#ffffff",
            font=("Arial", 20, "bold"),
            anchor="center",
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(title)
    
    def create_simulation_container(self):
        padding = 20
        
        outer_border = self.canvas.create_rectangle(
            self.sim_area_x - padding, 
            self.sim_area_y - padding,
            self.sim_area_x + self.sim_area_width + padding,
            self.sim_area_y + self.sim_area_height + padding,
            fill="",
            outline="#4a4a6e",
            width=3,
            tags=("simulator_ui", "ui_element", "container_border")
        )
        self.add_ui_element(outer_border)
        
        inner_border = self.canvas.create_rectangle(
            self.sim_area_x - 5, 
            self.sim_area_y - 5,
            self.sim_area_x + self.sim_area_width + 5,
            self.sim_area_y + self.sim_area_height + 5,
            fill="",
            outline="#5a5a7a",
            width=2,
            tags=("simulator_ui", "ui_element", "container_border")
        )
        self.add_ui_element(inner_border)
    
    def create_timer_and_traffic_lights(self):
        center_x = self.screen_width // 2
        timer_y = self.sim_area_y - 50
        
        timer_bg = self.canvas.create_rectangle(
            center_x - 40, timer_y - 15,
            center_x + 40, timer_y + 15,
            fill="#2a2a3e",
            outline="#4a4a6e",
            width=2,
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(timer_bg)
        
        self.timer_text = self.canvas.create_text(
            center_x, timer_y,
            text="N/A",
            fill="#ffffff",
            font=("Arial", 16, "bold"),
            anchor="center",
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(self.timer_text)
        
        left_light_x = center_x - 120
        self.create_traffic_light(left_light_x, timer_y, "left")
        
        arrow_left_x = left_light_x - 40
        self.left_arrow = self.create_arrow(arrow_left_x, timer_y, "right", "#444444")
        
        right_light_x = center_x + 120
        self.create_traffic_light(right_light_x, timer_y, "right")
        
        arrow_right_x = right_light_x + 40
        self.right_arrow = self.create_arrow(arrow_right_x, timer_y, "up", "#444444")
    
    def create_traffic_light(self, x, y, side):
        light_bg = self.canvas.create_rectangle(
            x - 18, y - 22,
            x + 18, y + 22,
            fill="#2a2a2a",
            outline="#1a1a1a",
            width=2,
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(light_bg)
        
        light = self.canvas.create_oval(
            x - 12, y - 12,
            x + 12, y + 12,
            fill="#333333",
            outline="#1a1a1a",
            width=2,
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(light)
        
        if side == "left":
            self.left_light = light
        else:
            self.right_light = light
    
    def create_arrow(self, x, y, direction, color):
        arrow_size = 15
        
        if direction == "right":
            points = [
                x - arrow_size, y - arrow_size//2,
                x, y - arrow_size//2,
                x, y - arrow_size,
                x + arrow_size, y,
                x, y + arrow_size,
                x, y + arrow_size//2,
                x - arrow_size, y + arrow_size//2
            ]
        else:
            points = [
                x - arrow_size//2, y + arrow_size,
                x - arrow_size//2, y,
                x - arrow_size, y,
                x, y - arrow_size,
                x + arrow_size, y,
                x + arrow_size//2, y,
                x + arrow_size//2, y + arrow_size
            ]
        
        arrow = self.canvas.create_polygon(
            points,
            fill=color,
            outline="#1a1a1a",
            width=2,
            tags=("simulator_ui", "ui_element")
        )
        self.add_ui_element(arrow)
        
        return arrow
    
    def set_traffic_light_state(self, state):
        self.traffic_light_state = state
        
        if state == "off":
            self.canvas.itemconfig(self.left_light, fill="#333333")
            self.canvas.itemconfig(self.right_light, fill="#333333")
            self.canvas.itemconfig(self.left_arrow, fill="#444444")
            self.canvas.itemconfig(self.right_arrow, fill="#444444")
            
        elif state == "left_go":
            self.canvas.itemconfig(self.left_light, fill="#00ff00")
            self.canvas.itemconfig(self.right_light, fill="#ff0000")
            self.canvas.itemconfig(self.left_arrow, fill="#00ff00")
            self.canvas.itemconfig(self.right_arrow, fill="#ff0000")
            
        elif state == "right_go":
            self.canvas.itemconfig(self.left_light, fill="#ff0000")
            self.canvas.itemconfig(self.right_light, fill="#00ff00")
            self.canvas.itemconfig(self.left_arrow, fill="#ff0000")
            self.canvas.itemconfig(self.right_arrow, fill="#00ff00")
            
        elif state == "caution":
            self.canvas.itemconfig(self.left_light, fill="#ffff00")
            self.canvas.itemconfig(self.right_light, fill="#ffff00")
            self.canvas.itemconfig(self.left_arrow, fill="#ffff00")
            self.canvas.itemconfig(self.right_arrow, fill="#ffff00")
    
    def update_timer(self, seconds):
        if seconds < 0 or seconds > 60:
            text = "N/A"
        else:
            text = f"{seconds:02d}s"
        
        self.canvas.itemconfig(self.timer_text, text=text)
    
    def update_timer_text(self, text):
        if self.timer_text:
            self.canvas.itemconfig(self.timer_text, text=text)
    
    def create_simulation_area(self):
        # Crear fondo del area de simulacion (SOLO con su propia tag)
        sim_bg = self.canvas.create_rectangle(
            self.sim_area_x, self.sim_area_y,
            self.sim_area_x + self.sim_area_width,
            self.sim_area_y + self.sim_area_height,
            fill="#f0f0f5",
            outline="",
            tags=("sim_background_layer",)
        )
        self.add_ui_element(sim_bg)
    
        self.draw_simulation_roads()
        self.draw_simulation_grid()
        self.create_clipping_borders()
    
    def create_simulation_background(self):
        bg_color = "#f0f0f5"
        
        sim_bg = self.canvas.create_rectangle(
            self.sim_area_x,
            self.sim_area_y,
            self.sim_area_x + self.sim_area_width,
            self.sim_area_y + self.sim_area_height,
            fill=bg_color,
            outline="",
            tags=("simulator_ui", "sim_background_layer")
        )
        self.add_ui_element(sim_bg)
    
    def draw_simulation_roads(self):
        road_color = "#5a5a5a"
        line_color = "#ffcc00"
        border_color = "#3a3a3a"
        
        center_x = self.sim_area_x + self.sim_area_width // 2
        center_y = self.sim_area_y + self.sim_area_height // 2
        road_width = 100
        
        box_id = self.canvas.create_rectangle(
            self.sim_area_x, center_y + road_width//2 - 4,
            self.sim_area_x + self.sim_area_width, center_y + road_width//2,
            fill=border_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(box_id)
        
        box_id = self.canvas.create_rectangle(
            self.sim_area_x, center_y - road_width//2,
            self.sim_area_x + self.sim_area_width, center_y - road_width//2 + 4,
            fill=border_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(box_id)
        
        box_id = self.canvas.create_rectangle(
            center_x + road_width//2 - 4, self.sim_area_y,
            center_x + road_width//2, self.sim_area_y + self.sim_area_height,
            fill=border_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(box_id)
        
        box_id = self.canvas.create_rectangle(
            center_x - road_width//2, self.sim_area_y,
            center_x - road_width//2 + 4, self.sim_area_y + self.sim_area_height,
            fill=border_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(box_id)
        
        h_road_id = self.canvas.create_rectangle(
            self.sim_area_x, center_y - road_width//2 + 4,
            self.sim_area_x + self.sim_area_width, center_y + road_width//2 - 4,
            fill=road_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(h_road_id)
        
        v_road_id = self.canvas.create_rectangle(
            center_x - road_width//2 + 4, self.sim_area_y,
            center_x + road_width//2 - 4, self.sim_area_y + self.sim_area_height,
            fill=road_color, outline="", tags=("simulator_ui", "road_layer")
        )
        self.add_ui_element(v_road_id)
        
        dash_width = 25
        gap_width = 15
        intersection_margin = road_width // 2
        
        for dash_x in range(self.sim_area_x, self.sim_area_x + self.sim_area_width, dash_width + gap_width):
            if dash_x + dash_width < center_x - intersection_margin or dash_x > center_x + intersection_margin:
                line_id = self.canvas.create_rectangle(
                    dash_x, center_y - 4,
                    min(dash_x + dash_width, self.sim_area_x + self.sim_area_width), center_y - 2,
                    fill=line_color, outline="", tags=("simulator_ui", "road_layer")
                )
                self.add_ui_element(line_id)
                
                line_id = self.canvas.create_rectangle(
                    dash_x, center_y + 2,
                    min(dash_x + dash_width, self.sim_area_x + self.sim_area_width), center_y + 4,
                    fill=line_color, outline="", tags=("simulator_ui", "road_layer")
                )
                self.add_ui_element(line_id)
        
        for dash_y in range(self.sim_area_y, self.sim_area_y + self.sim_area_height, dash_width + gap_width):
            if dash_y + dash_width < center_y - intersection_margin or dash_y > center_y + intersection_margin:
                line_id = self.canvas.create_rectangle(
                    center_x - 4, dash_y,
                    center_x - 2, min(dash_y + dash_width, self.sim_area_y + self.sim_area_height),
                    fill=line_color, outline="", tags=("simulator_ui", "road_layer")
                )
                self.add_ui_element(line_id)
                
                line_id = self.canvas.create_rectangle(
                    center_x + 2, dash_y,
                    center_x + 4, min(dash_y + dash_width, self.sim_area_y + self.sim_area_height),
                    fill=line_color, outline="", tags=("simulator_ui", "road_layer")
                )
                self.add_ui_element(line_id)
    
    def draw_simulation_grid(self):
        grid_color = "#333333"
        grid_size = 50
        
        for x in range(self.sim_area_x, self.sim_area_x + self.sim_area_width + 1, grid_size):
            line = self.canvas.create_line(
                x, self.sim_area_y,
                x, self.sim_area_y + self.sim_area_height,
                fill=grid_color,
                width=1,
                dash=(2, 4),
                tags=("simulator_ui", "grid_layer")
            )
            self.add_ui_element(line)
        
        for y in range(self.sim_area_y, self.sim_area_y + self.sim_area_height + 1, grid_size):
            line = self.canvas.create_line(
                self.sim_area_x, y,
                self.sim_area_x + self.sim_area_width, y,
                fill=grid_color,
                width=1,
                dash=(2, 4),
                tags=("simulator_ui", "grid_layer")
            )
            self.add_ui_element(line)
    
    def create_clipping_borders(self):
        self.sim_area_bounds = {
            'left': self.sim_area_x,
            'right': self.sim_area_x + self.sim_area_width,
            'top': self.sim_area_y,
            'bottom': self.sim_area_y + self.sim_area_height
        }
    
    def create_back_button(self):
        back_button = ButtonElement(
            self.canvas,
            20, 20,
            100, 35,
            "< Menu"
        )
        back_button.set_colors(
            bg_color="#4a4a6e",
            hover_bg="#5a5a7e",
            pressed_bg="#3a3a5e"
        )
        back_button.on_click = self.go_back_to_menu
        self.control_buttons.append(back_button)
    
    def on_cursor_move(self, x, y, vel_x, vel_y):
        sim_buttons = self.simulation_handler.get_buttons() if self.simulation_handler else []
        for button in sim_buttons:
            if button and button.contains_point(x, y):
                button.set_hover_state(True)
            elif button:
                button.set_hover_state(False)
    
        for button in self.control_buttons:
            if button and button.contains_point(x, y):
                button.set_hover_state(True)
            elif button:
                button.set_hover_state(False)
    
    def on_cursor_click(self, x, y, action, event):
        sim_buttons = self.simulation_handler.get_buttons() if self.simulation_handler else []
    
        if action == "press":
            for button in sim_buttons:
                if button and button.contains_point(x, y):
                    button.set_pressed_state(True)
            for button in self.control_buttons:
                if button and button.contains_point(x, y):
                    button.set_pressed_state(True)
                
        elif action == "release":
            for button in sim_buttons:
                if button:
                    button.set_pressed_state(False)
                    if button.contains_point(x, y):
                        button.handle_click(event)
                        return
        
            for button in self.control_buttons:
                if button:
                    button.set_pressed_state(False)
                    if button.contains_point(x, y):
                        button.handle_click(event)
    
    def on_cursor_drag(self, x, y, action, event):
        if (self.sim_area_x <= x <= self.sim_area_x + self.sim_area_width and 
            self.sim_area_y <= y <= self.sim_area_y + self.sim_area_height):
            
            if action == "start":
                print(f"Inicio de arrastre en simulacion: {x}, {y}")
            elif action == "drag":
                print(f"Arrastrando en simulacion: {x}, {y}")
            elif action == "end":
                print(f"Fin de arrastre en simulacion: {x}, {y}")
    
    def go_back_to_menu(self, button, event=None):
        print("DEBUG: Regresando al menu desde simulator")
        self.transition_to('menu', 'slide_down', 1.0)
    
    def on_show(self):
        print("DEBUG: Simulator on_show llamado")
        
        self.cleanup_cursor_callbacks()
        
        self.setup_cursor_callbacks()
        
        self.cursor_handler.enable_smooth_movement(0.9)
    
    def on_hide(self):
        print("DEBUG: Simulator on_hide llamado")
    
        self.cursor_handler.disable_smooth_movement()
    
        if self.simulation_handler:
            self.simulation_handler.cleanup()
    
        self.cleanup_cursor_callbacks()
    
        for button in self.control_buttons:
            try:
                button.cleanup()
            except:
                pass
        self.control_buttons.clear()
    
        try:
            self.canvas.after_cancel('all')
        except:
            pass
    
        try:
            self.canvas.delete("simulator_ui")
            self.canvas.delete("simulation_vehicle")
            self.canvas.delete("sim_background_layer")
            self.canvas.delete("road_layer")
            self.canvas.delete("vehicle_layer")
            self.canvas.delete("grid_layer")
            self.canvas.delete("border_layer")
        except:
            pass
    
        self.clear_ui_elements()
    
    def on_update(self):
        if self.simulation_running:
            pass
