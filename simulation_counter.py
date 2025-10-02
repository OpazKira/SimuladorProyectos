import math

class SimulationCounter:
    """Contador inteligente para gestion de semaforos basado en trafico"""
    
    def __init__(self, sim_area_x, sim_area_y, sim_area_width, sim_area_height):
        self.sim_area_x = sim_area_x
        self.sim_area_y = sim_area_y
        self.sim_area_width = sim_area_width
        self.sim_area_height = sim_area_height
        
        center_x = sim_area_x + sim_area_width // 2
        center_y = sim_area_y + sim_area_height // 2
        road_width = 100
        
        self.intersection_bounds = {
            'left': center_x - road_width // 2,
            'right': center_x + road_width // 2,
            'top': center_y - road_width // 2,
            'bottom': center_y + road_width // 2
        }
        
        self.lane_stats = {
            'horizontal_bottom': {'count': 0, 'total_length': 0, 'vehicles': []},
            'horizontal_top': {'count': 0, 'total_length': 0, 'vehicles': []},
            'vertical_left': {'count': 0, 'total_length': 0, 'vehicles': []},
            'vertical_right': {'count': 0, 'total_length': 0, 'vehicles': []}
        }
        
        self.lane_direction_map = {
            'horizontal_bottom': 'right',
            'horizontal_top': 'left',
            'vertical_left': 'down',
            'vertical_right': 'up'
        }
        
        self.congestion_threshold_count = 8
        self.congestion_threshold_length = 400
        
        self.similarity_tolerance = 0.3
        
        self.min_duration = 10.0
        self.max_duration = 20.0
        
        self.debug_enabled = True
    
    def reset_lane_stats(self):
        """Reiniciar estadisticas de todas las pistas"""
        for lane in self.lane_stats:
            self.lane_stats[lane] = {'count': 0, 'total_length': 0, 'vehicles': []}
    
    def has_crossed_intersection(self, vehicle):
        """Determinar si un vehiculo ya cruzo la interseccion"""
        vehicle_center_x = vehicle.x + vehicle.width / 2
        vehicle_center_y = vehicle.y + vehicle.height / 2
        
        if vehicle.direction == 'right':
            return vehicle_center_x > self.intersection_bounds['right']
        elif vehicle.direction == 'left':
            return vehicle_center_x < self.intersection_bounds['left']
        elif vehicle.direction == 'down':
            return vehicle_center_y > self.intersection_bounds['bottom']
        elif vehicle.direction == 'up':
            return vehicle_center_y < self.intersection_bounds['top']
        
        return False
    
    def classify_vehicle_lane(self, vehicle):
        """Clasificar vehiculo en su pista correspondiente"""
        if vehicle.direction == 'right':
            return 'horizontal_bottom'
        elif vehicle.direction == 'left':
            return 'horizontal_top'
        elif vehicle.direction == 'down':
            return 'vertical_left'
        elif vehicle.direction == 'up':
            return 'vertical_right'
        return None
    
    def get_vehicle_length(self, vehicle):
        """Obtener el largo del vehiculo segun su direccion"""
        if vehicle.direction in ['right', 'left']:
            return vehicle.width
        else:
            return vehicle.height
    
    def update(self, vehicles):
        """Actualizar contadores con vehiculos activos"""
        self.reset_lane_stats()
        
        for vehicle in vehicles:
            if not vehicle.is_active():
                continue
            
            if self.has_crossed_intersection(vehicle):
                continue
            
            lane = self.classify_vehicle_lane(vehicle)
            if lane:
                self.lane_stats[lane]['count'] += 1
                self.lane_stats[lane]['total_length'] += self.get_vehicle_length(vehicle)
                self.lane_stats[lane]['vehicles'].append(vehicle)
    
    def is_lane_congested(self, lane):
        """Determinar si una pista esta congestionada"""
        stats = self.lane_stats[lane]
        return (stats['count'] >= self.congestion_threshold_count or 
                stats['total_length'] >= self.congestion_threshold_length)
    
    def are_horizontal_lanes_congested(self):
        """Verificar si las pistas horizontales estan congestionadas"""
        return (self.is_lane_congested('horizontal_bottom') or 
                self.is_lane_congested('horizontal_top'))
    
    def are_vertical_lanes_congested(self):
        """Verificar si las pistas verticales estan congestionadas"""
        return (self.is_lane_congested('vertical_left') or 
                self.is_lane_congested('vertical_right'))
    
    def get_horizontal_totals(self):
        """Obtener totales de pistas horizontales"""
        bottom = self.lane_stats['horizontal_bottom']
        top = self.lane_stats['horizontal_top']
        return {
            'count': bottom['count'] + top['count'],
            'length': bottom['total_length'] + top['total_length']
        }
    
    def get_vertical_totals(self):
        """Obtener totales de pistas verticales"""
        left = self.lane_stats['vertical_left']
        right = self.lane_stats['vertical_right']
        return {
            'count': left['count'] + right['count'],
            'length': left['total_length'] + right['total_length']
        }
    
    def are_totals_similar(self, horizontal_totals, vertical_totals):
        """Determinar si los totales son similares entre horizontales y verticales"""
        h_count = horizontal_totals['count']
        v_count = vertical_totals['count']
        h_length = horizontal_totals['length']
        v_length = vertical_totals['length']
        
        if h_count == 0 and v_count == 0:
            return True
        
        if h_count == 0 or v_count == 0:
            return False
        
        count_ratio = min(h_count, v_count) / max(h_count, v_count)
        count_similar = count_ratio >= (1.0 - self.similarity_tolerance)
        
        if h_length == 0 and v_length == 0:
            length_similar = True
        elif h_length == 0 or v_length == 0:
            length_similar = False
        else:
            length_ratio = min(h_length, v_length) / max(h_length, v_length)
            length_similar = length_ratio >= (1.0 - self.similarity_tolerance)
        
        return count_similar or length_similar
    
    def calculate_next_duration(self, current_state, next_state):
        """
        Calcular duracion del siguiente estado basado en trafico actual
        
        Args:
            current_state: Estado actual del semaforo ('left_go' o 'right_go')
            next_state: Siguiente estado del semaforo
            
        Returns:
            float: Duracion en segundos para el siguiente estado
        """
        horizontal_totals = self.get_horizontal_totals()
        vertical_totals = self.get_vertical_totals()
        
        h_congested = self.are_horizontal_lanes_congested()
        v_congested = self.are_vertical_lanes_congested()
        any_congested = h_congested or v_congested
        
        totals_similar = self.are_totals_similar(horizontal_totals, vertical_totals)
        
        if self.debug_enabled:
            print(f"\n=== CALCULO DE DURACION ===")
            print(f"Estado actual: {current_state} -> Siguiente: {next_state}")
            print(f"Horizontal: {horizontal_totals['count']} vehiculos, {horizontal_totals['length']:.1f}px")
            print(f"Vertical: {vertical_totals['count']} vehiculos, {vertical_totals['length']:.1f}px")
            print(f"Congestion H: {h_congested}, V: {v_congested}")
            print(f"Totales similares: {totals_similar}")
        
        if totals_similar and not any_congested:
            duration = self.min_duration
            if self.debug_enabled:
                print(f"CASO 1: Similares y sin congestion -> {duration}s")
        
        elif totals_similar and any_congested:
            duration = self.max_duration
            if self.debug_enabled:
                print(f"CASO 2: Similares pero congestionado -> {duration}s")
        
        else:
            h_total_score = horizontal_totals['count'] * 2 + horizontal_totals['length'] / 50
            v_total_score = vertical_totals['count'] * 2 + vertical_totals['length'] / 50
            
            if self.debug_enabled:
                print(f"Score H: {h_total_score:.1f}, Score V: {v_total_score:.1f}")
            
            next_favors_horizontal = (next_state == 'left_go')
            
            if h_total_score > v_total_score:
                if next_favors_horizontal:
                    duration = self.max_duration
                    if self.debug_enabled:
                        print(f"CASO 3A: Mas trafico H, siguiente favorece H -> {duration}s")
                else:
                    duration = self.min_duration
                    if self.debug_enabled:
                        print(f"CASO 3B: Mas trafico H, siguiente favorece V -> {duration}s")
            else:
                if next_favors_horizontal:
                    duration = self.min_duration
                    if self.debug_enabled:
                        print(f"CASO 3C: Mas trafico V, siguiente favorece H -> {duration}s")
                else:
                    duration = self.max_duration
                    if self.debug_enabled:
                        print(f"CASO 3D: Mas trafico V, siguiente favorece V -> {duration}s")
        
        if self.debug_enabled:
            print(f"=========================\n")
        
        return duration
    
    def get_lane_stats_summary(self):
        """Obtener resumen de estadisticas de todas las pistas"""
        return {
            'horizontal_bottom': {
                'count': self.lane_stats['horizontal_bottom']['count'],
                'length': self.lane_stats['horizontal_bottom']['total_length'],
                'congested': self.is_lane_congested('horizontal_bottom')
            },
            'horizontal_top': {
                'count': self.lane_stats['horizontal_top']['count'],
                'length': self.lane_stats['horizontal_top']['total_length'],
                'congested': self.is_lane_congested('horizontal_top')
            },
            'vertical_left': {
                'count': self.lane_stats['vertical_left']['count'],
                'length': self.lane_stats['vertical_left']['total_length'],
                'congested': self.is_lane_congested('vertical_left')
            },
            'vertical_right': {
                'count': self.lane_stats['vertical_right']['count'],
                'length': self.lane_stats['vertical_right']['total_length'],
                'congested': self.is_lane_congested('vertical_right')
            },
            'horizontal_totals': self.get_horizontal_totals(),
            'vertical_totals': self.get_vertical_totals()
        }
    
    def set_congestion_thresholds(self, count_threshold, length_threshold):
        """Configurar umbrales de congestion"""
        self.congestion_threshold_count = count_threshold
        self.congestion_threshold_length = length_threshold
    
    def set_similarity_tolerance(self, tolerance):
        """Configurar tolerancia de similitud (0.0 - 1.0)"""
        self.similarity_tolerance = max(0.0, min(1.0, tolerance))
    
    def set_duration_range(self, min_duration, max_duration):
        """Configurar rango de duraciones"""
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def enable_debug(self, enabled=True):
        """Habilitar o deshabilitar modo debug"""
        self.debug_enabled = enabled
