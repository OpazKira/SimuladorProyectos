import tkinter as tk
from loading_screen import LoadingScreen
from main_menu import MainMenu
from simulator_screen import SimulatorScreen
from exit_screen import ExitScreen
from background_handler import BackgroundHandler
from cursor_handler import CursorHandler

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aplicacion de Simulacion")
        
        # Configurar icono ANTES de fullscreen
        try:
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, "logo.ico")
            
            # IMPORTANTE: Usar ruta sin join para evitar problemas
            self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        # AHORA activar fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # ... resto del código
        
        self.setup_bindings()
        
        # Canvas principal compartido entre todas las pantallas
        # CAMBIADO: bg inicial a azul oscuro en lugar de negro
        self.main_canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg='#0a0a1e',  # Azul oscuro inicial para loading
            highlightthickness=0
        )
        self.main_canvas.pack(fill='both', expand=True)
        
        # Handler de fondo compartido
        self.background_handler = BackgroundHandler(
            self.main_canvas, 
            self.screen_width, 
            self.screen_height
        )
        
        # Habilitar debug para ver que esta pasando
        self.background_handler.set_debug(True)
        
        # Handler de cursor compartido
        self.cursor_handler = CursorHandler(
            self.main_canvas,
            self.screen_width,
            self.screen_height
        )
        
        # Conectar cursor handler con background handler
        self.background_handler.set_cursor_handler(self.cursor_handler)
        
        self.current_screen = None
        self.screens = {}
        
        self.init_screens()
        self.show_screen('loading')
    
    def setup_bindings(self):
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.handle_escape)
    
    def toggle_fullscreen(self, event=None):
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
    
    def handle_escape(self, event=None):
        if self.current_screen == 'loading' or self.current_screen == 'menu':
            self.root.attributes('-fullscreen', False)
        else:
            self.show_screen('menu')
    
    def init_screens(self):
        self.screens = {
            'loading': LoadingScreen(self.main_canvas, self),
            'menu': MainMenu(self.main_canvas, self),
            'simulator': SimulatorScreen(self.main_canvas, self),
            'exit': ExitScreen(self.main_canvas, self)
        }
    
    def show_screen(self, screen_name, transition_type=None, transition_duration=1.0):
        print(f"DEBUG: Cambiando a pantalla: {screen_name}")
        
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].hide()
        
        if screen_name in self.screens:
            # Si hay transicion, configurarla
            if transition_type and self.current_screen:
                self.background_handler.start_transition(
                    transition_type, 
                    transition_duration,
                    lambda: self._complete_screen_change(screen_name)
                )
            else:
                self._complete_screen_change(screen_name)
    
    def _complete_screen_change(self, screen_name):
        """Completar el cambio de pantalla"""
        print(f"DEBUG: Completando cambio a: {screen_name}")
        self.current_screen = screen_name
        self.screens[screen_name].show()
    
    def get_background_handler(self):
        """Obtener referencia al handler de fondo"""
        return self.background_handler
    
    def get_cursor_handler(self):
        """Obtener referencia al handler de cursor"""
        return self.cursor_handler
    
    def quit_application(self):
        print("DEBUG: Cerrando aplicacion...")
        
        # Deshabilitar seguimiento del cursor
        if self.cursor_handler:
            self.cursor_handler.disable_tracking()
        
        # Limpieza completa del background handler
        if self.background_handler:
            self.background_handler.cleanup()
        
        # Dar tiempo para que se cancelen los after
        try:
            self.root.update()
        except:
            pass
        
        # Cerrar aplicacion
        try:
            self.root.destroy()
        except:
            pass
        
        print("DEBUG: Aplicacion cerrada")
    
    def run(self):
        # Iniciar animaciones de fondo
        self.background_handler.start_animation()
        
        # Habilitar seguimiento del cursor
        self.cursor_handler.enable_tracking()
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_application()

if __name__ == "__main__":
    app = App()
    app.run()
