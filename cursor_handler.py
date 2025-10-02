import tkinter as tk
import math
import time

class CursorHandler:
    """Manejador del cursor para seguimiento y control de posicion"""
    
    def __init__(self, canvas, screen_width, screen_height):
        self.canvas = canvas
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Posicion actual del cursor
        self.current_x = 0
        self.current_y = 0
        self.last_x = 0
        self.last_y = 0
        
        # Posicion objetivo (para movimiento suave)
        self.target_x = 0
        self.target_y = 0
        
        # Velocidad del cursor
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Configuraciones
        self.tracking_enabled = False
        self.smooth_movement = False
        self.movement_speed = 0.8
        self.update_interval = 16  # ~60 FPS
        
        # Estados del cursor
        self.is_pressed = False
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Historial de movimiento
        self.position_history = []
        self.max_history_length = 10
        
        # Callbacks para eventos
        self.on_move_callbacks = []
        self.on_click_callbacks = []
        self.on_drag_callbacks = []
        self.on_hover_callbacks = []
        
        # Elementos bajo el cursor
        self.hovered_elements = []
        
        # Tiempo de actualizacion
        self.last_update_time = time.time()
        
        # Configurar eventos del canvas
        self.setup_events()
    
    def setup_events(self):
        """Configurar eventos del canvas para seguimiento del cursor"""
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_mouse_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<Enter>', self.on_mouse_enter)
        self.canvas.bind('<Leave>', self.on_mouse_leave)
        
        # Hacer el canvas focusable para recibir eventos
        self.canvas.focus_set()
    
    def enable_tracking(self):
        """Habilitar seguimiento del cursor"""
        self.tracking_enabled = True
        if self.smooth_movement:
            self.start_smooth_update()
    
    def disable_tracking(self):
        """Deshabilitar seguimiento del cursor"""
        self.tracking_enabled = False
    
    def enable_smooth_movement(self, speed=0.8):
        """Habilitar movimiento suave del cursor"""
        self.smooth_movement = True
        self.movement_speed = speed
        if self.tracking_enabled:
            self.start_smooth_update()
    
    def disable_smooth_movement(self):
        """Deshabilitar movimiento suave del cursor"""
        self.smooth_movement = False
    
    def start_smooth_update(self):
        """Iniciar actualizacion suave del cursor"""
        if self.smooth_movement and self.tracking_enabled:
            self.update_smooth_position()
    
    def update_smooth_position(self):
        """Actualizar posicion suave del cursor"""
        if not self.smooth_movement or not self.tracking_enabled:
            return
    
        try:
            if not self.canvas.winfo_exists():
                return
        except:
            return
    
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
    
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
    
        if abs(dx) > 1 or abs(dy) > 1:
            self.current_x += dx * self.movement_speed * delta_time * 60
            self.current_y += dy * self.movement_speed * delta_time * 60
        
            self.velocity_x = dx * self.movement_speed
            self.velocity_y = dy * self.movement_speed
        
            self.notify_move_callbacks()
    
        try:
            self.canvas.after(self.update_interval, self.update_smooth_position)
        except:
            pass
    
    def on_mouse_move(self, event):
        """Manejar movimiento del mouse"""
        self.last_x = self.current_x
        self.last_y = self.current_y
        
        if self.smooth_movement:
            self.target_x = event.x
            self.target_y = event.y
        else:
            self.current_x = event.x
            self.current_y = event.y
            self.notify_move_callbacks()
        
        # Agregar al historial
        self.add_to_history(event.x, event.y)
        
        # Verificar elementos bajo el cursor
        self.update_hovered_elements(event.x, event.y)
    
    def on_mouse_press(self, event):
        """Manejar presion del mouse"""
        self.is_pressed = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.notify_click_callbacks(event, 'press')
    
    def on_mouse_release(self, event):
        """Manejar liberacion del mouse"""
        self.is_pressed = False
        
        if self.is_dragging:
            self.is_dragging = False
            self.notify_drag_callbacks(event, 'end')
        
        self.notify_click_callbacks(event, 'release')
    
    def on_mouse_drag(self, event):
        """Manejar arrastre del mouse"""
        if not self.is_dragging:
            self.is_dragging = True
            self.notify_drag_callbacks(event, 'start')
        
        self.notify_drag_callbacks(event, 'drag')
        
        # Actualizar posicion durante arrastre
        self.on_mouse_move(event)
    
    def on_mouse_enter(self, event):
        """Manejar entrada del mouse al canvas"""
        pass
    
    def on_mouse_leave(self, event):
        """Manejar salida del mouse del canvas"""
        # Limpiar elementos en hover
        for element in self.hovered_elements:
            if hasattr(element, 'set_hover_state'):
                element.set_hover_state(False)
        self.hovered_elements.clear()
    
    def add_to_history(self, x, y):
        """Agregar posicion al historial"""
        self.position_history.append((x, y, time.time()))
        
        # Mantener historial limitado
        if len(self.position_history) > self.max_history_length:
            self.position_history.pop(0)
    
    def update_hovered_elements(self, x, y):
        """Actualizar elementos bajo el cursor"""
        # Esta funcion seria implementada con una lista de elementos registrados
        # Por ahora es un placeholder
        pass
    
    def register_element(self, element):
        """Registrar un elemento para deteccion de hover"""
        # Agregar elemento a lista de elementos registrados
        pass
    
    def unregister_element(self, element):
        """Desregistrar un elemento"""
        # Remover elemento de lista de elementos registrados
        pass
    
    def set_position(self, x, y, smooth=True):
        """Establecer posicion del cursor"""
        if smooth and self.smooth_movement:
            self.target_x = x
            self.target_y = y
        else:
            self.current_x = x
            self.current_y = y
            self.target_x = x
            self.target_y = y
    
    def get_position(self):
        """Obtener posicion actual del cursor"""
        return (self.current_x, self.current_y)
    
    def get_target_position(self):
        """Obtener posicion objetivo del cursor"""
        return (self.target_x, self.target_y)
    
    def get_velocity(self):
        """Obtener velocidad del cursor"""
        return (self.velocity_x, self.velocity_y)
    
    def get_distance_moved(self):
        """Obtener distancia movida desde la ultima posicion"""
        dx = self.current_x - self.last_x
        dy = self.current_y - self.last_y
        return math.sqrt(dx * dx + dy * dy)
    
    def get_drag_distance(self):
        """Obtener distancia de arrastre desde el inicio"""
        if self.is_dragging:
            dx = self.current_x - self.drag_start_x
            dy = self.current_y - self.drag_start_y
            return math.sqrt(dx * dx + dy * dy)
        return 0
    
    def is_in_bounds(self, margin=0):
        """Verificar si el cursor esta dentro de los limites"""
        return (margin <= self.current_x <= self.screen_width - margin and
                margin <= self.current_y <= self.screen_height - margin)
    
    def clamp_to_bounds(self, margin=0):
        """Restringir cursor a los limites de pantalla"""
        self.current_x = max(margin, min(self.screen_width - margin, self.current_x))
        self.current_y = max(margin, min(self.screen_height - margin, self.current_y))
        self.target_x = self.current_x
        self.target_y = self.current_y
    
    def add_move_callback(self, callback):
        """Agregar callback para movimiento del cursor"""
        self.on_move_callbacks.append(callback)
    
    def add_click_callback(self, callback):
        """Agregar callback para clicks del cursor"""
        self.on_click_callbacks.append(callback)
    
    def add_drag_callback(self, callback):
        """Agregar callback para arrastre del cursor"""
        self.on_drag_callbacks.append(callback)
    
    def add_hover_callback(self, callback):
        """Agregar callback para hover del cursor"""
        self.on_hover_callbacks.append(callback)
    
    def remove_move_callback(self, callback):
        """Remover callback de movimiento"""
        if callback in self.on_move_callbacks:
            self.on_move_callbacks.remove(callback)
    
    def remove_click_callback(self, callback):
        """Remover callback de click"""
        if callback in self.on_click_callbacks:
            self.on_click_callbacks.remove(callback)
    
    def remove_drag_callback(self, callback):
        """Remover callback de arrastre"""
        if callback in self.on_drag_callbacks:
            self.on_drag_callbacks.remove(callback)
    
    def remove_hover_callback(self, callback):
        """Remover callback de hover"""
        if callback in self.on_hover_callbacks:
            self.on_hover_callbacks.remove(callback)
    
    def notify_move_callbacks(self):
        """Notificar callbacks de movimiento"""
        for callback in self.on_move_callbacks:
            try:
                callback(self.current_x, self.current_y, self.velocity_x, self.velocity_y)
            except Exception as e:
                print(f"Error en callback de movimiento: {e}")
    
    def notify_click_callbacks(self, event, action):
        """Notificar callbacks de click"""
        for callback in self.on_click_callbacks:
            try:
                callback(event.x, event.y, action, event)
            except Exception as e:
                print(f"Error en callback de click: {e}")
    
    def notify_drag_callbacks(self, event, action):
        """Notificar callbacks de arrastre"""
        for callback in self.on_drag_callbacks:
            try:
                callback(event.x, event.y, action, event)
            except Exception as e:
                print(f"Error en callback de arrastre: {e}")
    
    def notify_hover_callbacks(self, element, hover_state):
        """Notificar callbacks de hover"""
        for callback in self.on_hover_callbacks:
            try:
                callback(element, hover_state, self.current_x, self.current_y)
            except Exception as e:
                print(f"Error en callback de hover: {e}")
    
    def get_cursor_info(self):
        """Obtener informacion completa del cursor"""
        return {
            'position': (self.current_x, self.current_y),
            'target': (self.target_x, self.target_y),
            'velocity': (self.velocity_x, self.velocity_y),
            'is_pressed': self.is_pressed,
            'is_dragging': self.is_dragging,
            'tracking_enabled': self.tracking_enabled,
            'smooth_movement': self.smooth_movement,
            'in_bounds': self.is_in_bounds(),
            'history_length': len(self.position_history)
        }
    
    def reset(self):
        """Resetear estado del cursor"""
        self.current_x = 0
        self.current_y = 0
        self.target_x = 0
        self.target_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_pressed = False
        self.is_dragging = False
        self.position_history.clear()
        self.hovered_elements.clear()
    def cleanup(self):
        """Limpiar completamente el cursor handler"""
        self.disable_tracking()
        self.disable_smooth_movement()
    
        self.on_move_callbacks.clear()
        self.on_click_callbacks.clear()
        self.on_drag_callbacks.clear()
        self.on_hover_callbacks.clear()
    
        try:
            self.canvas.unbind('<Motion>')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<Enter>')
            self.canvas.unbind('<Leave>')
        except:
            pass
