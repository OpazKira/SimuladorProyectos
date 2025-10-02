import tkinter as tk
from abc import ABC, abstractmethod
from background_handler import BackgroundHandler
from background_element import BackgroundElement

class ScreenHandler(ABC):
    """
    Clase base abstracta que maneja funcionalidades comunes de todas las pantallas.
    Proporciona una interfaz estándar y funcionalidades compartidas para reducir duplicación de código.
    """
    
    def __init__(self, canvas, app, screen_type):
        """
        Inicializar el manejador de pantalla base.
        
        Args:
            canvas: Canvas de tkinter donde se dibuja la pantalla
            app: Referencia a la aplicación principal
            screen_type: Tipo de pantalla (string identificador)
        """
        self.canvas = canvas
        self.app = app
        self.screen_type = screen_type
        self.screen_width = app.screen_width
        self.screen_height = app.screen_height
        
        self.background_handler = app.get_background_handler()
        
        self.is_visible = False
        self.is_initialized = False
        
        self.background_elements = []
        self.ui_elements = []
        self.animation_elements = []
        
        self.setup_screen()
    
    def setup_screen(self):
        """
        Configuración inicial de la pantalla.
        Puede ser sobrescrito por las subclases para configuraciones específicas.
        """
        self.is_initialized = True
    
    @abstractmethod
    def create_specific_background(self):
        """
        Método abstracto para crear elementos específicos del fondo.
        Debe ser implementado por cada pantalla específica.
        """
        pass
    
    @abstractmethod
    def create_specific_ui(self):
        """
        Método abstracto para crear elementos específicos de UI.
        Debe ser implementado por cada pantalla específica.
        """
        pass
    
    def create_default_background(self):
        """
        No crear fondo por defecto - delegar al background_handler
        """
        pass
    
    def clear_background_elements(self):
        """
        Limpiar solo los elementos de fondo especificos de esta pantalla.
        NO limpiar el fondo principal del background_handler ni los vehiculos.
        """
        for element in self.background_elements[:]:  # Usar copia para iterar
            # NO eliminar vehiculos, nubes, ni elementos del sistema de fondo compartido
            if element.element_type not in ["vehicle", "cloud", "day_sky", "day_sun", "day_building", "day_road"]:
                if element in self.background_handler.background_elements:
                    self.background_handler.remove_background_element(element)
                self.background_elements.remove(element)
    
        # Solo limpiar la lista local, no los elementos compartidos
        self.background_elements = [e for e in self.background_elements 
                                if e.element_type in ["vehicle", "cloud", "day_sky", "day_sun", "day_building", "day_road"]]
    
    def clear_ui_elements(self):
        """
        Limpiar todos los elementos de UI de esta pantalla.
        """
        for element_id in self.ui_elements:
            try:
                self.canvas.delete(element_id)
            except tk.TclError:
                pass
        self.ui_elements.clear()
    
    def clear_animation_elements(self):
        """
        Limpiar elementos de animacion especificos de esta pantalla.
        NO tocar vehiculos ni elementos del sistema compartido.
        """
        for element in self.animation_elements[:]:  # Usar copia para iterar
            # NO eliminar vehiculos ni elementos del sistema compartido
            if element.element_type not in ["vehicle", "cloud"]:
                if element in self.background_handler.background_elements:
                    self.background_handler.remove_background_element(element)
            self.animation_elements.remove(element)
    
        # Solo limpiar la lista local
        self.animation_elements = [e for e in self.animation_elements 
                               if e.element_type in ["vehicle", "cloud"]]
    
    def clear_all_elements(self):
        """
        Limpiar solo los elementos especificos de la pantalla.
        NUNCA tocar background_elements que pertenecen al sistema compartido.
        """
        self.clear_ui_elements()
        # NO limpiar background ni animation elements para preservar vehiculos y fondo
        
    def add_background_element(self, element):
        """
        Agregar un elemento de fondo y registrarlo.
        
        Args:
            element: BackgroundElement a agregar
        """
        if isinstance(element, BackgroundElement):
            self.background_elements.append(element)
            self.background_handler.add_background_element(element)
    
    def add_ui_element(self, element_id):
        """
        Registrar un elemento de UI.
        
        Args:
            element_id: ID del elemento de canvas creado
        """
        self.ui_elements.append(element_id)
    
    def add_animation_element(self, element):
        """
        Agregar un elemento de animación específico.
        
        Args:
            element: BackgroundElement de animación a agregar
        """
        if isinstance(element, BackgroundElement):
            self.animation_elements.append(element)
            self.background_handler.add_background_element(element)
    
    def ensure_animations_active(self):
        """
        Asegurar que las animaciones de fondo estén activas.
        """
        if not self.background_handler.get_animation_status():
            self.background_handler.start_animation()
    
    def set_background_type(self):
        """
        Establecer el tipo de fondo en el background handler.
        """
        print(f"DEBUG: ScreenHandler.set_background_type() - tipo: {self.screen_type}")
        self.background_handler.set_background_type(self.screen_type)
    
    def show(self):
        """
        Mostrar la pantalla. Método estándar que puede ser extendido por las subclases.
        """
        if not self.is_visible:
            self.is_visible = True
            
            self.set_background_type()
            
            try:
                self.create_specific_background()
                self.create_specific_ui()
            except NotImplementedError:
                try:
                    self.create_specific_ui()
                except NotImplementedError:
                    pass
            
            self.ensure_animations_active()
            
            self.on_show()
    
    def hide(self):
        """
        Ocultar la pantalla. Método estándar que puede ser extendido por las subclases.
        """
        if self.is_visible:
            self.is_visible = False
            
            self.on_hide()
            
            self.clear_all_elements()
    
    def on_show(self):
        """
        Método llamado cuando la pantalla se muestra.
        Puede ser sobrescrito por las subclases para lógica específica.
        """
        pass
    
    def on_hide(self):
        """
        Método llamado cuando la pantalla se oculta.
        Puede ser sobrescrito por las subclases para lógica específica.
        """
        pass
    
    def update(self):
        """
        Actualizar la pantalla. Método base que puede ser extendido.
        """
        if self.is_visible:
            self.on_update()
    
    def on_update(self):
        """
        Método llamado en cada actualización de la pantalla.
        Puede ser sobrescrito por las subclases para lógica específica.
        """
        pass
    
    def create_centered_text(self, text, y_offset=0, font_size=24, color="white", tag_suffix=""):
        """
        Crear texto centrado en la pantalla.
        
        Args:
            text: Texto a mostrar
            y_offset: Desplazamiento vertical desde el centro
            font_size: Tamaño de fuente
            color: Color del texto
            tag_suffix: Sufijo para el tag del elemento
        
        Returns:
            ID del elemento de texto creado
        """
        x = self.screen_width // 2
        y = self.screen_height // 2 + y_offset
        
        element_id = self.canvas.create_text(
            x, y,
            text=text,
            fill=color,
            font=("Arial", font_size, "bold"),
            anchor="center",
            tags=f"{self.screen_type}_ui{tag_suffix}"
        )
        
        self.add_ui_element(element_id)
        return element_id
    
    def create_button(self, text, x, y, width, height, command=None, 
                     bg_color="#4a4a4a", text_color="white", font_size=14):
        """
        Crear un botón simple.
        
        Args:
            text: Texto del botón
            x, y: Posición del botón
            width, height: Dimensiones del botón
            command: Función a ejecutar al hacer click
            bg_color: Color de fondo del botón
            text_color: Color del texto
            font_size: Tamaño de fuente
        
        Returns:
            Tupla con (button_bg_id, button_text_id)
        """
        bg_id = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=bg_color,
            outline="#666666",
            tags=f"{self.screen_type}_button_bg"
        )
        
        text_id = self.canvas.create_text(
            x + width//2, y + height//2,
            text=text,
            fill=text_color,
            font=("Arial", font_size, "bold"),
            anchor="center",
            tags=f"{self.screen_type}_button_text"
        )
        
        self.add_ui_element(bg_id)
        self.add_ui_element(text_id)
        
        if command:
            self.canvas.tag_bind(bg_id, "<Button-1>", lambda e: command())
            self.canvas.tag_bind(text_id, "<Button-1>", lambda e: command())
        
        return bg_id, text_id
    
    def create_loading_indicator(self, x, y, size=50, color="#ffffff"):
        """
        Crear un indicador de carga simple.
        
        Args:
            x, y: Posición del indicador
            size: Tamaño del indicador
            color: Color del indicador
        
        Returns:
            ID del elemento creado
        """
        element_id = self.canvas.create_oval(
            x - size//2, y - size//2,
            x + size//2, y + size//2,
            outline=color,
            width=3,
            tags=f"{self.screen_type}_loading"
        )
        
        self.add_ui_element(element_id)
        return element_id
    
    def get_screen_info(self):
        """
        Obtener información sobre el estado de la pantalla.
        
        Returns:
            Dict con información de la pantalla
        """
        return {
            'type': self.screen_type,
            'visible': self.is_visible,
            'initialized': self.is_initialized,
            'background_elements_count': len(self.background_elements),
            'ui_elements_count': len(self.ui_elements),
            'animation_elements_count': len(self.animation_elements)
        }
    
    def transition_to(self, target_screen, transition_type="fade", duration=1.0):
        """
        Realizar transición a otra pantalla.
        
        Args:
            target_screen: Nombre de la pantalla destino
            transition_type: Tipo de transición
            duration: Duración de la transición
        """
        self.app.show_screen(target_screen, transition_type, duration)
    
    def __str__(self):
        """
        Representación en string de la pantalla.
        """
        return f"ScreenHandler({self.screen_type}, visible={self.is_visible})"
    
    def __repr__(self):
        return self.__str__()