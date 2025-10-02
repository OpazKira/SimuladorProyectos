import tkinter as tk
from screen_handler import ScreenHandler
from screen_element import ScreenElement, ButtonElement
from background_element import BackgroundElement

class ExitScreen(ScreenHandler):
    def __init__(self, canvas, app):
        super().__init__(canvas, app, "exit")
        
        self.confirmation_buttons = []
        self.exit_message = None
        
        self.cursor_handler = app.get_cursor_handler()
        
        self.callbacks_registered = False
    
    def setup_cursor_callbacks(self):
        """Configurar callbacks del cursor para interacciones"""
        if not self.callbacks_registered:
            self.cursor_handler.add_move_callback(self.on_cursor_move)
            self.cursor_handler.add_click_callback(self.on_cursor_click)
            self.callbacks_registered = True
            print("DEBUG: Exit callbacks registrados")
    
    def cleanup_cursor_callbacks(self):
        """Limpiar callbacks del cursor"""
        if self.callbacks_registered:
            try:
                self.cursor_handler.remove_move_callback(self.on_cursor_move)
                self.cursor_handler.remove_click_callback(self.on_cursor_click)
                self.callbacks_registered = False
                print("DEBUG: Exit callbacks limpiados")
            except Exception as e:
                print(f"DEBUG: Error limpiando callbacks en exit: {e}")
    
    def create_specific_background(self):
        """Crear fondo especifico de la pantalla de salida"""
        pass
    
    def create_fade_effects(self):
        """Crear efectos de desvanecimiento sutiles"""
        import random
        
        for i in range(8):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            
            fade_particle = BackgroundElement(x, y, 2, 2)
            fade_particle.set_color("#ffffff")
            fade_particle.set_opacity(random.uniform(0.05, 0.15))
            fade_particle.set_velocity(0, random.uniform(5, 15))
            fade_particle.add_tag("fade_particle")
            fade_particle.set_depth(10)
            
            self.add_background_element(fade_particle)
    
    def create_specific_ui(self):
        """Crear elementos de UI especificos de salida"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        panel_width = 400
        panel_height = 200
        panel_x = center_x - panel_width // 2
        panel_y = center_y - panel_height // 2
        
        panel_bg = self.canvas.create_rectangle(
            panel_x, panel_y,
            panel_x + panel_width, panel_y + panel_height,
            fill="#2d1b69",
            outline="#666666",
            width=2,
            stipple="gray25",
            tags="exit_panel"
        )
        self.add_ui_element(panel_bg)
        
        self.exit_message = self.canvas.create_text(
            center_x, center_y - 50,
            text="Estas seguro de que deseas salir?",
            fill="#ffffff",
            font=("Arial", 18, "bold"),
            anchor="center",
            tags="exit_confirmation"
        )
        self.add_ui_element(self.exit_message)
        
        warning_text = self.canvas.create_text(
            center_x, center_y - 20,
            text="Se perdera cualquier progreso no guardado",
            fill="#ffcccc",
            font=("Arial", 12),
            anchor="center",
            tags="exit_warning"
        )
        self.add_ui_element(warning_text)
        
        self.create_confirmation_buttons(center_x, center_y)
    
    def create_confirmation_buttons(self, center_x, center_y):
        """Crear botones de confirmacion de salida"""
        button_width = 120
        button_height = 40
        button_spacing = 40
        
        yes_button = ButtonElement(
            self.canvas,
            center_x - button_width - button_spacing // 2,
            center_y + 30,
            button_width,
            button_height,
            "Si, Salir"
        )
        yes_button.set_colors(
            bg_color="#F44336",
            hover_bg="#EF5350",
            pressed_bg="#D32F2F"
        )
        yes_button.on_click = self.confirm_exit
        self.confirmation_buttons.append(yes_button)
        
        no_button = ButtonElement(
            self.canvas,
            center_x + button_spacing // 2,
            center_y + 30,
            button_width,
            button_height,
            "Cancelar"
        )
        no_button.set_colors(
            bg_color="#4CAF50",
            hover_bg="#5CBF60",
            pressed_bg="#45A049"
        )
        no_button.on_click = self.cancel_exit
        self.confirmation_buttons.append(no_button)
    
    def on_cursor_move(self, x, y, vel_x, vel_y):
        """Manejar movimiento del cursor"""
        for button in self.confirmation_buttons:
            if button.contains_point(x, y):
                button.set_hover_state(True)
            else:
                button.set_hover_state(False)
    
    def on_cursor_click(self, x, y, action, event):
        """Manejar clicks del cursor"""
        if action == "press":
            for button in self.confirmation_buttons:
                if button.contains_point(x, y):
                    button.set_pressed_state(True)
        elif action == "release":
            for button in self.confirmation_buttons:
                button.set_pressed_state(False)
                if button.contains_point(x, y):
                    button.handle_click(event)
    
    def confirm_exit(self, button, event=None):
        """Confirmar salida de la aplicacion"""
        self.create_exit_animation()
    
    def cancel_exit(self, button, event=None):
        """Cancelar salida y regresar al menu"""
        print("DEBUG: Cancelando salida, regresando al menu")
        
        self.cleanup_cursor_callbacks()
        
        for button in self.confirmation_buttons:
            try:
                button.delete_element()
            except:
                pass
        
        self.clear_ui_elements()
        
        self.canvas.after(50, lambda: self.app.show_screen('menu'))

    
    def create_exit_animation(self):
        """Crear animacion de salida"""
        if self.exit_message:
            try:
                self.canvas.itemconfig(self.exit_message, text="Cerrando aplicacion...")
            except:
                pass
        
        self.canvas.after(500, self.app.quit_application)
    
    def on_show(self):
        """Acciones al mostrar la pantalla de salida"""
        print("DEBUG: Exit on_show llamado")
        
        self.cleanup_cursor_callbacks()
        
        self.setup_cursor_callbacks()
        
        self.animate_entrance()
    
    def animate_entrance(self):
        """Animar entrada de elementos"""
        pass
    
    def on_hide(self):
        """Acciones al ocultar la pantalla de salida"""
        print("DEBUG: Exit on_hide llamado")
    
        self.cleanup_cursor_callbacks()
    
        for button in self.confirmation_buttons:
            try:
                button.cleanup()
            except:
                pass
        self.confirmation_buttons.clear()
    
        try:
            self.canvas.after_cancel('all')
        except:
            pass
    
        self.clear_ui_elements()
    
    def on_update(self):
        """Actualizacion continua de la pantalla de salida"""
        pass
