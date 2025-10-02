import math
import random

class BackgroundElement:
    """Clase base para todos los elementos del fondo"""
    
    def __init__(self, x, y, width=0, height=0):
        # Posición y dimensiones
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Posición original (para resetear)
        self.original_x = x
        self.original_y = y
        
        # Offsets para transiciones y movimiento
        self.offset_x = 0
        self.offset_y = 0
        
        # Propiedades visuales
        self.visible = True
        self.active = True
        self.opacity = 1.0
        self.color = "#FFFFFF"
        self.depth = 0  # Z-index para layering
        
        # Propiedades de movimiento
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.acceleration_y = 0
        
        # Propiedades de animación
        self.rotation = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Tiempo de vida
        self.lifetime = -1  # -1 = infinito
        self.age = 0
        
        # Tags para identificación
        self.tags = set()
        self.element_type = "base"
        
    def update(self, delta_time):
        """Actualizar el elemento en cada frame"""
        if not self.active:
            return
        
        # Actualizar edad
        if self.lifetime > 0:
            self.age += delta_time
            if self.age >= self.lifetime:
                self.active = False
                return
        
        # Aplicar aceleración a velocidad
        self.velocity_x += self.acceleration_x * delta_time
        self.velocity_y += self.acceleration_y * delta_time
        
        # Aplicar velocidad a posición
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # Llamar a update específico de la subclase
        self.custom_update(delta_time)
    
    def custom_update(self, delta_time):
        """Método para override en subclases"""
        pass
    
    def draw(self, canvas):
        """Dibujar el elemento en el canvas"""
        if not self.visible:
            return
        
        # Calcular posición final con offsets
        final_x = self.x + self.offset_x
        final_y = self.y + self.offset_y
        
        # Aplicar transformaciones si es necesario
        if self.scale_x != 1.0 or self.scale_y != 1.0 or self.rotation != 0:
            self.draw_transformed(canvas, final_x, final_y)
        else:
            self.draw_simple(canvas, final_x, final_y)
    
    def draw_simple(self, canvas, x, y):
        """Dibujo simple sin transformaciones - override en subclases"""
        # Dibujo básico como rectángulo
        canvas.create_rectangle(
            x, y, x + self.width, y + self.height,
            fill=self.color, outline="", tags="background_layer"
        )
    
    def draw_transformed(self, canvas, x, y):
        """Dibujo con transformaciones - override en subclases si es necesario"""
        # Por defecto, usar dibujo simple
        self.draw_simple(canvas, x, y)
    
    def set_position(self, x, y):
        """Establecer nueva posición"""
        self.x = x
        self.y = y
    
    def set_offset(self, offset_x, offset_y):
        """Establecer offset para transiciones"""
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def set_velocity(self, vel_x, vel_y):
        """Establecer velocidad"""
        self.velocity_x = vel_x
        self.velocity_y = vel_y
    
    def set_acceleration(self, acc_x, acc_y):
        """Establecer aceleración"""
        self.acceleration_x = acc_x
        self.acceleration_y = acc_y
    
    def set_color(self, color):
        """Establecer color del elemento"""
        self.color = color
    
    def set_opacity(self, opacity):
        """Establecer opacidad (0.0 - 1.0)"""
        self.opacity = max(0.0, min(1.0, opacity))
        self.visible = self.opacity > 0.0
    
    def set_depth(self, depth):
        """Establecer profundidad para layering"""
        self.depth = depth
    
    def get_depth(self):
        """Obtener profundidad"""
        return self.depth
    
    def set_scale(self, scale_x, scale_y=None):
        """Establecer escala"""
        self.scale_x = scale_x
        self.scale_y = scale_y if scale_y is not None else scale_x
    
    def set_rotation(self, rotation):
        """Establecer rotación en radianes"""
        self.rotation = rotation
    
    def set_lifetime(self, lifetime):
        """Establecer tiempo de vida en segundos"""
        self.lifetime = lifetime
        self.age = 0
    
    def add_tag(self, tag):
        """Agregar tag para identificación"""
        self.tags.add(tag)
    
    def remove_tag(self, tag):
        """Remover tag"""
        self.tags.discard(tag)
    
    def has_tag(self, tag):
        """Verificar si tiene un tag específico"""
        return tag in self.tags
    
    def is_visible(self):
        """Verificar si el elemento es visible"""
        return self.visible and self.active and self.opacity > 0.0
    
    def is_active(self):
        """Verificar si el elemento está activo"""
        return self.active
    
    def deactivate(self):
        """Desactivar el elemento"""
        self.active = False
    
    def activate(self):
        """Activar el elemento"""
        self.active = True
    
    def hide(self):
        """Ocultar el elemento"""
        self.visible = False
    
    def show(self):
        """Mostrar el elemento"""
        self.visible = True
    
    def reset_position(self):
        """Resetear a posición original"""
        self.x = self.original_x
        self.y = self.original_y
        self.offset_x = 0
        self.offset_y = 0
    
    def get_bounds(self):
        """Obtener límites del elemento"""
        final_x = self.x + self.offset_x
        final_y = self.y + self.offset_y
        return {
            'left': final_x,
            'top': final_y,
            'right': final_x + self.width * self.scale_x,
            'bottom': final_y + self.height * self.scale_y
        }
    
    def is_in_bounds(self, screen_width, screen_height, margin=50):
        """Verificar si el elemento está dentro de los límites de pantalla"""
        bounds = self.get_bounds()
        return (bounds['right'] >= -margin and 
                bounds['left'] <= screen_width + margin and
                bounds['bottom'] >= -margin and 
                bounds['top'] <= screen_height + margin)
    
    def distance_to(self, other_element):
        """Calcular distancia a otro elemento"""
        dx = self.x - other_element.x
        dy = self.y - other_element.y
        return math.sqrt(dx * dx + dy * dy)
    
    def move_toward(self, target_x, target_y, speed):
        """Mover hacia una posición objetivo"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
    
    def apply_force(self, force_x, force_y):
        """Aplicar una fuerza al elemento"""
        self.acceleration_x += force_x
        self.acceleration_y += force_y
    
    def clone(self):
        """Crear una copia del elemento"""
        new_element = BackgroundElement(self.x, self.y, self.width, self.height)
        new_element.color = self.color
        new_element.opacity = self.opacity
        new_element.depth = self.depth
        new_element.velocity_x = self.velocity_x
        new_element.velocity_y = self.velocity_y
        new_element.tags = self.tags.copy()
        return new_element
    
    def __str__(self):
        """Representación en string del elemento"""
        return f"{self.element_type}(x={self.x:.1f}, y={self.y:.1f}, active={self.active})"
    
    def __repr__(self):
        return self.__str__()
