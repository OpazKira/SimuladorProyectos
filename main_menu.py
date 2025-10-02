import tkinter as tk
from screen_handler import ScreenHandler
from screen_element import ScreenElement, ButtonElement
from background_element import BackgroundElement

class MainMenu(ScreenHandler):
    def __init__(self, canvas, app):
        super().__init__(canvas, app, "menu")
        
        self.menu_buttons = []
        self.title_element = None
        
        self.cursor_handler = app.get_cursor_handler()
        
        self.callbacks_registered = False
    
    def setup_cursor_callbacks(self):
        """Configurar callbacks del cursor para interacciones"""
        if not self.callbacks_registered:
            self.cursor_handler.add_move_callback(self.on_cursor_move)
            self.cursor_handler.add_click_callback(self.on_cursor_click)
            self.callbacks_registered = True
            print("DEBUG: Menu callbacks registrados")
    
    def cleanup_cursor_callbacks(self):
        """Limpiar callbacks del cursor"""
        if self.callbacks_registered:
            try:
                self.cursor_handler.remove_move_callback(self.on_cursor_move)
                self.cursor_handler.remove_click_callback(self.on_cursor_click)
                self.callbacks_registered = False
                print("DEBUG: Menu callbacks limpiados")
            except Exception as e:
                print(f"DEBUG: Error limpiando callbacks en menu: {e}")
    
    def create_specific_background(self):
        """Crear fondo especifico del menu principal"""
        pass
    
    def create_specific_ui(self):
        """Crear elementos de UI especificos del menu"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
    
        self.title_element = self.create_centered_text(
            "RoadShifter", 
            -150, 
            36, 
            "#ffffff", 
            "_title"
        )
    
        self.create_menu_buttons(center_x, center_y)
    
        self.canvas.tag_lower("background_layer")
        self.canvas.update()
    
    def create_menu_buttons(self, center_x, center_y):
        """Crear botones del menu principal"""
        button_width = 250
        button_height = 50
        button_spacing = 70
    
        # CAMBIADO: Solo 2 botones ahora, ajustar posicion vertical
        start_button = ButtonElement(
            self.canvas,
            center_x - button_width // 2,
            center_y - button_spacing // 2,  # Ajustado para centrar con 2 botones
            button_width,
            button_height,
            "Iniciar Simulacion"
        )
        start_button.set_colors(
            bg_color="#4CAF50",
            hover_bg="#5CBF60",
            pressed_bg="#45A049"
        )
        start_button.on_click = self.on_start_simulation
        self.menu_buttons.append(start_button)
    
        # ELIMINADO: config_button
    
        exit_button = ButtonElement(
            self.canvas,
            center_x - button_width // 2,
            center_y + button_spacing // 2,  # Ajustado para centrar con 2 botones
            button_width,
            button_height,
            "Salir"
        )
        exit_button.set_colors(
            bg_color="#F44336",
            hover_bg="#EF5350",
            pressed_bg="#D32F2F"
        )
        exit_button.on_click = self.on_exit
        self.menu_buttons.append(exit_button)
    
    def on_cursor_move(self, x, y, vel_x, vel_y):
        """Manejar movimiento del cursor"""
        for button in self.menu_buttons:
            if button.contains_point(x, y):
                button.set_hover_state(True)
            else:
                button.set_hover_state(False)
    
    def on_cursor_click(self, x, y, action, event):
        """Manejar clicks del cursor"""
        if action == "press":
            for button in self.menu_buttons:
                if button.contains_point(x, y):
                    button.set_pressed_state(True)
        elif action == "release":
            for button in self.menu_buttons:
                button.set_pressed_state(False)
                if button.contains_point(x, y):
                    button.handle_click(event)
    
    def on_start_simulation(self, button, event=None):
        """Iniciar simulacion"""
        self.transition_to('simulator', 'slide_up', 1.0)
    
    def on_exit(self, button, event=None):
        """Salir de la aplicacion"""
        self.transition_to('exit', 'fade', 0.5)
    
    def on_show(self):
        """Acciones al mostrar el menu"""
        print("DEBUG: Menu on_show llamado")
        
        self.cleanup_cursor_callbacks()
        
        self.setup_cursor_callbacks()
        
        self.animate_title_entrance()
    
    def animate_title_entrance(self):
        """Animar entrada del titulo"""
        pass
    
    def on_hide(self):
        """Acciones al ocultar el menu"""
        print("DEBUG: Menu on_hide llamado")
    
        self.cleanup_cursor_callbacks()
    
        for button in self.menu_buttons:
            try:
                button.cleanup()
            except:
                pass
        self.menu_buttons.clear()
    
        try:
            self.canvas.after_cancel('all')
        except:
            pass
    
        self.clear_ui_elements()
    
    def on_update(self):
        """Actualizacion continua del menu"""
        pass
