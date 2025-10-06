import math

class SimulationCounter:
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
        
        self.min_duration = 10.0
        self.max_duration = 20.0
        
        self.debug_enabled = True
    
    def reset_lane_stats(self):
        for lane in self.lane_stats:
            self.lane_stats[lane] = {'count': 0, 'total_length': 0, 'vehicles': []}
    
    def has_crossed_intersection(self, vehicle):
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
    
    def is_in_intersection(self, vehicle):
        vehicle_center_x = vehicle.x + vehicle.width / 2
        vehicle_center_y = vehicle.y + vehicle.height / 2
        
        in_horizontal_range = (self.intersection_bounds['left'] <= vehicle_center_x <= 
                              self.intersection_bounds['right'])
        in_vertical_range = (self.intersection_bounds['top'] <= vehicle_center_y <= 
                            self.intersection_bounds['bottom'])
        
        return in_horizontal_range and in_vertical_range
    
    def classify_vehicle_lane(self, vehicle):
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
        if vehicle.direction in ['right', 'left']:
            return vehicle.width
        else:
            return vehicle.height
    
    def update(self, vehicles):
        self.reset_lane_stats()
        
        for vehicle in vehicles:
            if not vehicle.is_active():
                continue
            
            if self.has_crossed_intersection(vehicle):
                continue
            
            if self.is_in_intersection(vehicle):
                continue
            
            lane = self.classify_vehicle_lane(vehicle)
            if lane:
                self.lane_stats[lane]['count'] += 1
                self.lane_stats[lane]['total_length'] += self.get_vehicle_length(vehicle)
                self.lane_stats[lane]['vehicles'].append(vehicle)
    
    def is_lane_congested(self, lane):
        stats = self.lane_stats[lane]
        return (stats['count'] >= self.congestion_threshold_count or 
                stats['total_length'] >= self.congestion_threshold_length)
    
    def are_horizontal_lanes_congested(self):
        return (self.is_lane_congested('horizontal_bottom') or 
                self.is_lane_congested('horizontal_top'))
    
    def are_vertical_lanes_congested(self):
        return (self.is_lane_congested('vertical_left') or 
                self.is_lane_congested('vertical_right'))
    
    def get_horizontal_totals(self):
        bottom = self.lane_stats['horizontal_bottom']
        top = self.lane_stats['horizontal_top']
        return {
            'count': bottom['count'] + top['count'],
            'length': bottom['total_length'] + top['total_length']
        }
    
    def get_vertical_totals(self):
        left = self.lane_stats['vertical_left']
        right = self.lane_stats['vertical_right']
        return {
            'count': left['count'] + right['count'],
            'length': left['total_length'] + right['total_length']
        }
    
    def calculate_next_duration(self, current_state, next_state):
        horizontal_totals = self.get_horizontal_totals()
        vertical_totals = self.get_vertical_totals()
        
        h_congested = self.are_horizontal_lanes_congested()
        v_congested = self.are_vertical_lanes_congested()
        
        if self.debug_enabled:
            print(f"\n=== CALCULO DE DURACION ===")
            print(f"Estado actual: {current_state} -> Siguiente: {next_state}")
            print(f"Horizontal: {horizontal_totals['count']} vehiculos, {horizontal_totals['length']:.1f}px")
            print(f"Vertical: {vertical_totals['count']} vehiculos, {vertical_totals['length']:.1f}px")
            print(f"Congestion H: {h_congested}, V: {v_congested}")
        
        if next_state == 'left_go':
            if h_congested:
                duration = self.max_duration
                if self.debug_enabled:
                    print(f"Direccion horizontal CONGESTIONADA -> {duration}s")
            else:
                duration = self.min_duration
                if self.debug_enabled:
                    print(f"Direccion horizontal normal -> {duration}s")
        
        elif next_state == 'right_go':
            if v_congested:
                duration = self.max_duration
                if self.debug_enabled:
                    print(f"Direccion vertical CONGESTIONADA -> {duration}s")
            else:
                duration = self.min_duration
                if self.debug_enabled:
                    print(f"Direccion vertical normal -> {duration}s")
        
        else:
            duration = self.min_duration
            if self.debug_enabled:
                print(f"Estado desconocido, usando duracion minima -> {duration}s")
        
        if self.debug_enabled:
            print(f"=========================\n")
        
        return duration
    
    def get_lane_stats_summary(self):
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
        self.congestion_threshold_count = count_threshold
        self.congestion_threshold_length = length_threshold
    
    def set_duration_range(self, min_duration, max_duration):
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def enable_debug(self, enabled=True):
        self.debug_enabled = enabled
