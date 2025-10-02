import tkinter as tk
import math

class ScreenElement:
    """Clase base para elementos de interfaz de usuario en pantalla"""
    
    def __init__(self, canvas, x, y, width=0, height=0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Propiedades visuales
        self.visible = True
        self.active = True
        self.opacity = 1.0
        self.color = "#FFFFFF"
        self.border_color = "#CCCCCC"
        self.border_width = 0
        
        # Propiedades de transformacion
        self.rotation = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Estados de interaccion
        self.hover = False
        self.pressed = False
        self.focused = False
        
        # Eventos
        self.on_click = None
        self.on_hover = None
        self.on_focus = None
        
        # IDs de elementos del canvas
        self.element_ids = []
        
        # Tags para identificacion
        self.tags = set()
        self.element_type = "screen_element"
    
    def create_element(self):
        """Crear el elemento en el canvas - debe ser implementado por subclases"""
        pass
    
    def update_element(self):
        """Actualizar el elemento visual"""
        if not self.visible:
            self.hide_element()
            return
        
        self.draw_element()
    
    def draw_element(self):
        """Dibujar el elemento - debe ser implementado por subclases"""
        pass
    
    def hide_element(self):
        """Ocultar el elemento del canvas"""
        for element_id in self.element_ids:
            try:
                self.canvas.itemconfig(element_id, state='hidden')
            except tk.TclError:
                pass
    
    def show_element(self):
        """Mostrar el elemento en el canvas"""
        for element_id in self.element_ids:
            try:
                self.canvas.itemconfig(element_id, state='normal')
            except tk.TclError:
                pass
    
    def delete_element(self):
        """Eliminar el elemento del canvas"""
        for element_id in self.element_ids:
            try:
                self.canvas.tag_unbind(element_id, "<Button-1>")
                self.canvas.tag_unbind(element_id, "<Enter>")
                self.canvas.tag_unbind(element_id, "<Leave>")
                self.canvas.tag_unbind(element_id, "<ButtonPress-1>")
                self.canvas.tag_unbind(element_id, "<ButtonRelease-1>")
                self.canvas.tag_unbind(element_id, "<B1-Motion>")
            except:
                pass
    
        for element_id in self.element_ids:
            try:
                self.canvas.delete(element_id)
            except:
                pass
    
        self.element_ids.clear()
        self.on_click = None
        self.on_hover = None
        self.on_focus = None
    
    def set_position(self, x, y):
        """Establecer nueva posicion del elemento"""
        self.x = x
        self.y = y
        self.update_element()
    
    def set_size(self, width, height):
        """Establecer nuevo tamano del elemento"""
        self.width = width
        self.height = height
        self.update_element()
    
    def set_color(self, color):
        """Establecer color del elemento"""
        self.color = color
        self.update_element()
    
    def set_border(self, color, width):
        """Establecer borde del elemento"""
        self.border_color = color
        self.border_width = width
        self.update_element()
    
    def set_opacity(self, opacity):
        """Establecer opacidad del elemento"""
        self.opacity = max(0.0, min(1.0, opacity))
        self.update_element()
    
    def set_visible(self, visible):
        """Establecer visibilidad del elemento"""
        self.visible = visible
        if visible:
            self.show_element()
        else:
            self.hide_element()
    
    def set_active(self, active):
        """Establecer si el elemento esta activo"""
        self.active = active
    
    def contains_point(self, x, y):
        """Verificar si un punto esta dentro del elemento"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_bounds(self):
        """Obtener limites del elemento"""
        return {
            'left': self.x,
            'top': self.y,
            'right': self.x + self.width,
            'bottom': self.y + self.height,
            'center_x': self.x + self.width // 2,
            'center_y': self.y + self.height // 2
        }
    
    def bind_event(self, event_type, callback):
        """Vincular evento a los elementos del canvas"""
        for element_id in self.element_ids:
            try:
                self.canvas.tag_bind(element_id, event_type, callback)
            except tk.TclError:
                pass
    
    def set_hover_state(self, hover):
        """Establecer estado de hover"""
        if self.hover != hover:
            self.hover = hover
            if self.on_hover:
                self.on_hover(self, hover)
            self.update_element()
    
    def set_pressed_state(self, pressed):
        """Establecer estado de presionado"""
        if self.pressed != pressed:
            self.pressed = pressed
            self.update_element()
    
    def set_focus_state(self, focused):
        """Establecer estado de foco"""
        if self.focused != focused:
            self.focused = focused
            if self.on_focus:
                self.on_focus(self, focused)
            self.update_element()
    
    def handle_click(self, event=None):
        """Manejar evento de click"""
        if self.active and self.on_click:
            self.on_click(self, event)
    
    def add_tag(self, tag):
        """Agregar tag para identificacion"""
        self.tags.add(tag)
    
    def remove_tag(self, tag):
        """Remover tag"""
        self.tags.discard(tag)
    
    def has_tag(self, tag):
        """Verificar si tiene un tag especifico"""
        return tag in self.tags


class ButtonElement(ScreenElement):
    """Elemento de boton interactivo"""
    
    def __init__(self, canvas, x, y, width, height, text="Button"):
        super().__init__(canvas, x, y, width, height)
        
        self.text = text
        self.font_family = "Arial"
        self.font_size = 12
        self.font_weight = "normal"
        
        # Colores del boton
        self.bg_color = "#4a4a4a"
        self.text_color = "#ffffff"
        self.hover_bg_color = "#5a5a5a"
        self.hover_text_color = "#ffffff"
        self.pressed_bg_color = "#3a3a3a"
        self.pressed_text_color = "#ffffff"
        self.disabled_bg_color = "#2a2a2a"
        self.disabled_text_color = "#666666"
        
        # Estados especificos del boton
        self.enabled = True
        
        self.element_type = "button"
        
        # Crear el boton
        self.create_element()
    
    def create_element(self):
        """Crear elementos visuales del boton"""
        # Crear rectangulo de fondo
        self.bg_id = self.canvas.create_rectangle(
            self.x, self.y, 
            self.x + self.width, self.y + self.height,
            fill=self.bg_color,
            outline=self.border_color,
            width=self.border_width,
            tags="ui_element"  # CAMBIAR de "button_element" a "ui_element"
        )
    
        # Crear texto del boton
        self.text_id = self.canvas.create_text(
            self.x + self.width // 2,
            self.y + self.height // 2,
            text=self.text,
            fill=self.text_color,
            font=(self.font_family, self.font_size, self.font_weight),
            anchor="center",
            tags="ui_element"  # CAMBIAR de "button_element" a "ui_element"
        )
    
        self.element_ids = [self.bg_id, self.text_id]
    
        # Vincular eventos
        self.bind_event("<Button-1>", lambda e: self.handle_click(e))
        self.bind_event("<Enter>", lambda e: self.set_hover_state(True))
        self.bind_event("<Leave>", lambda e: self.set_hover_state(False))
        self.bind_event("<ButtonPress-1>", lambda e: self.set_pressed_state(True))
        self.bind_event("<ButtonRelease-1>", lambda e: self.set_pressed_state(False))
    
    def update_element(self):
        """Actualizar apariencia del boton"""
        if not self.visible:
            self.hide_element()
            return
        
        # Determinar colores segun estado
        if not self.enabled:
            bg_color = self.disabled_bg_color
            text_color = self.disabled_text_color
        elif self.pressed:
            bg_color = self.pressed_bg_color
            text_color = self.pressed_text_color
        elif self.hover:
            bg_color = self.hover_bg_color
            text_color = self.hover_text_color
        else:
            bg_color = self.bg_color
            text_color = self.text_color
        
        # Actualizar colores
        try:
            self.canvas.itemconfig(self.bg_id, fill=bg_color)
            self.canvas.itemconfig(self.text_id, fill=text_color)
        except tk.TclError:
            pass
    
    def set_text(self, text):
        """Establecer texto del boton"""
        self.text = text
        try:
            self.canvas.itemconfig(self.text_id, text=text)
        except tk.TclError:
            pass
    
    def set_font(self, family="Arial", size=12, weight="normal"):
        """Establecer fuente del boton"""
        self.font_family = family
        self.font_size = size
        self.font_weight = weight
        try:
            self.canvas.itemconfig(self.text_id, 
                                 font=(family, size, weight))
        except tk.TclError:
            pass
    
    def set_colors(self, bg_color=None, text_color=None, 
                   hover_bg=None, hover_text=None,
                   pressed_bg=None, pressed_text=None):
        """Establecer colores del boton"""
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
        if hover_bg:
            self.hover_bg_color = hover_bg
        if hover_text:
            self.hover_text_color = hover_text
        if pressed_bg:
            self.pressed_bg_color = pressed_bg
        if pressed_text:
            self.pressed_text_color = pressed_text
        
        self.update_element()
    
    def set_enabled(self, enabled):
        """Establecer si el boton esta habilitado"""
        self.enabled = enabled
        self.active = enabled
        self.update_element()
    
    def set_position(self, x, y):
        """Actualizar posicion del boton"""
        old_x, old_y = self.x, self.y
        self.x, self.y = x, y
        
        dx = x - old_x
        dy = y - old_y
        
        try:
            self.canvas.move(self.bg_id, dx, dy)
            self.canvas.move(self.text_id, dx, dy)
        except tk.TclError:
            pass
    
    def set_size(self, width, height):
        """Actualizar tamano del boton"""
        self.width = width
        self.height = height
        
        try:
            # Actualizar rectangulo de fondo
            self.canvas.coords(self.bg_id, 
                             self.x, self.y,
                             self.x + width, self.y + height)
            
            # Actualizar posicion del texto
            self.canvas.coords(self.text_id,
                             self.x + width // 2,
                             self.y + height // 2)
        except tk.TclError:
            pass
    def cleanup(self):
        """Limpiar el boton antes de eliminarlo"""
        # Limpiar callbacks
        self.on_click = None
        self.on_hover = None
        self.on_focus = None
        
        # Desvincular eventos y eliminar
        self.delete_element()
