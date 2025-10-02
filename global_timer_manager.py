import time
from enum import Enum

class TimerContext(Enum):
    """Contextos para diferentes tipos de temporizadores"""
    UI = "ui"                    # Interfaces de usuario
    BACKGROUND = "background"    # Elementos de fondo
    ANIMATION = "animation"      # Animaciones generales
    GAME = "game"               # Logica de juego
    SYSTEM = "system"           # Eventos de sistema
    AUDIO = "audio"             # Efectos de sonido y musica
    NETWORK = "network"         # Eventos de red
    INPUT = "input"             # Manejo de entrada del usuario

class GlobalTimerManager:
    """Manejador global que coordina todos los sistemas de temporizadores"""
    
    def __init__(self):
        # Sistemas de temporizadores
        self.ui_timer_system = None
        self.background_timer_system = None
        
        # Estado global
        self.global_paused = False
        self.global_time_scale = 1.0  # Escala de tiempo global
        self.start_time = time.time()
        
        # Contextos activos
        self.active_contexts = set()
        self.context_priorities = {
            TimerContext.SYSTEM: 10,
            TimerContext.UI: 9,
            TimerContext.INPUT: 8,
            TimerContext.ANIMATION: 7,
            TimerContext.GAME: 6,
            TimerContext.AUDIO: 5,
            TimerContext.NETWORK: 4,
            TimerContext.BACKGROUND: 3
        }
        
        # Contextos pausados individualmente
        self.paused_contexts = set()
        
        # Callbacks globales
        self.global_callbacks = {}
        self.context_callbacks = {}
        
        # Estadisticas globales
        self.total_updates = 0
        self.performance_stats = {
            'avg_update_time': 0.0,
            'max_update_time': 0.0,
            'last_update_time': 0.0,
            'total_update_time': 0.0,
            'fps_history': [],
            'fps_history_size': 60  # Mantener historial de 60 frames
        }
        
        # Control de calidad
        self.quality_settings = {
            'max_fps': 60,
            'min_fps': 30,
            'auto_quality_adjust': True,
            'performance_threshold': 0.016  # 16ms para 60fps
        }
        
        # Sistema de alertas
        self.alert_thresholds = {
            'high_cpu_usage': 0.025,  # 25ms = problema de rendimiento
            'memory_leak_detection': 1000,  # Mas de 1000 temporizadores
            'fps_drop_threshold': 45  # FPS por debajo de 45
        }
        
        # Inicializar sistemas
        self.initialize_timer_systems()
    
    def initialize_timer_systems(self):
        """Inicializar sistemas de temporizadores"""
        try:
            from ui_timer_system import UITimerSystem
            self.ui_timer_system = UITimerSystem()
            self.activate_context(TimerContext.UI)
            print("DEBUG: UI Timer System inicializado correctamente")
        except ImportError as e:
            print(f"WARNING: UI Timer System no disponible: {e}")
        
        try:
            from background_timer_system import BackgroundTimerSystem
            self.background_timer_system = BackgroundTimerSystem()
            self.activate_context(TimerContext.BACKGROUND)
            print("DEBUG: Background Timer System inicializado correctamente")
        except ImportError as e:
            print(f"WARNING: Background Timer System no disponible: {e}")
    
    def activate_context(self, context):
        """Activar un contexto de temporizadores"""
        self.active_contexts.add(context)
        self.paused_contexts.discard(context)  # Asegurar que no este pausado
        
        # Ejecutar callbacks de activacion de contexto
        if context in self.context_callbacks:
            for callback in self.context_callbacks[context]:
                try:
                    callback('activated', context)
                except Exception as e:
                    print(f"ERROR en callback de contexto {context}: {e}")
    
    def deactivate_context(self, context):
        """Desactivar un contexto de temporizadores"""
        self.active_contexts.discard(context)
        self.paused_contexts.discard(context)
        
        # Ejecutar callbacks de desactivacion de contexto
        if context in self.context_callbacks:
            for callback in self.context_callbacks[context]:
                try:
                    callback('deactivated', context)
                except Exception as e:
                    print(f"ERROR en callback de contexto {context}: {e}")
    
    def is_context_active(self, context):
        """Verificar si un contexto esta activo"""
        return context in self.active_contexts and context not in self.paused_contexts
    
    def set_global_time_scale(self, scale):
        """Establecer escala de tiempo global (1.0 = normal, 0.5 = mitad, 2.0 = doble)"""
        old_scale = self.global_time_scale
        self.global_time_scale = max(0.0, scale)
        
        # Notificar cambio de escala
        self.trigger_global_event('time_scale_changed', {
            'old_scale': old_scale,
            'new_scale': self.global_time_scale
        })
    
    def pause_global(self):
        """Pausar todos los sistemas globalmente"""
        if not self.global_paused:
            self.global_paused = True
            
            if self.ui_timer_system:
                self.ui_timer_system.pause_all()
            if self.background_timer_system:
                self.background_timer_system.pause_all()
            
            self.trigger_global_event('global_pause', {'timestamp': time.time()})
    
    def resume_global(self):
        """Reanudar todos los sistemas globalmente"""
        if self.global_paused:
            self.global_paused = False
            
            if self.ui_timer_system:
                self.ui_timer_system.resume_all()
            if self.background_timer_system:
                self.background_timer_system.resume_all()
            
            self.trigger_global_event('global_resume', {'timestamp': time.time()})
    
    def pause_context(self, context):
        """Pausar solo un contexto especifico"""
        if context in self.active_contexts:
            self.paused_contexts.add(context)
            
            if context == TimerContext.UI and self.ui_timer_system:
                self.ui_timer_system.pause_all()
            elif context == TimerContext.BACKGROUND and self.background_timer_system:
                self.background_timer_system.pause_all()
            
            self.trigger_global_event('context_paused', {'context': context.value})
    
    def resume_context(self, context):
        """Reanudar solo un contexto especifico"""
        self.paused_contexts.discard(context)
        
        if context == TimerContext.UI and self.ui_timer_system:
            self.ui_timer_system.resume_all()
        elif context == TimerContext.BACKGROUND and self.background_timer_system:
            self.background_timer_system.resume_all()
        
        self.trigger_global_event('context_resumed', {'context': context.value})
    
    def add_ui_timer(self, name, duration, callback, repeat=False, priority=None):
        """Agregar temporizador de UI (proxy method)"""
        if self.ui_timer_system and self.is_context_active(TimerContext.UI):
            from ui_timer_system import TimerPriority
            ui_priority = priority or TimerPriority.NORMAL
            timer = self.ui_timer_system.add_timer(name, duration, callback, repeat, ui_priority)
            
            if timer:
                self.trigger_global_event('timer_created', {
                    'context': 'ui',
                    'name': name,
                    'duration': duration,
                    'repeat': repeat
                })
            
            return timer
        return None
    
    def add_ui_interpolation_timer(self, name, duration, start_value, end_value, 
                                 interpolation_callback, completion_callback=None, easing=None):
        """Agregar temporizador de interpolacion de UI"""
        if self.ui_timer_system and self.is_context_active(TimerContext.UI):
            timer = self.ui_timer_system.add_interpolation_timer(
                name, duration, start_value, end_value, 
                interpolation_callback, completion_callback, easing=easing
            )
            
            if timer:
                self.trigger_global_event('interpolation_timer_created', {
                    'context': 'ui',
                    'name': name,
                    'duration': duration,
                    'has_easing': easing is not None
                })
            
            return timer
        return None
    
    def schedule_ui_event(self, delay, callback, name="ui_event", data=None):
        """Programar evento de UI"""
        if self.ui_timer_system and self.is_context_active(TimerContext.UI):
            event = self.ui_timer_system.schedule_event(delay, callback, name, data)
            
            if event:
                self.trigger_global_event('event_scheduled', {
                    'context': 'ui',
                    'name': name,
                    'delay': delay
                })
            
            return event
        return None
    
    def add_background_timer(self, name, duration, callback, repeat=False):
        """Agregar temporizador de fondo (proxy method)"""
        if self.background_timer_system and self.is_context_active(TimerContext.BACKGROUND):
            timer = self.background_timer_system.add_timer(name, duration, callback, repeat)
            
            if timer:
                self.trigger_global_event('timer_created', {
                    'context': 'background',
                    'name': name,
                    'duration': duration,
                    'repeat': repeat
                })
            
            return timer
        return None
    
    def add_background_random_timer(self, name, min_duration, max_duration, callback, repeat=False):
        """Agregar temporizador de fondo con duracion aleatoria"""
        if self.background_timer_system and self.is_context_active(TimerContext.BACKGROUND):
            timer = self.background_timer_system.add_random_timer(
                name, min_duration, max_duration, callback, repeat
            )
            
            if timer:
                self.trigger_global_event('random_timer_created', {
                    'context': 'background',
                    'name': name,
                    'min_duration': min_duration,
                    'max_duration': max_duration,
                    'repeat': repeat
                })
            
            return timer
        return None
    
    def schedule_background_event(self, delay, callback, name="bg_event", data=None):
        """Programar evento de fondo"""
        if self.background_timer_system and self.is_context_active(TimerContext.BACKGROUND):
            event = self.background_timer_system.schedule_event(delay, callback, name, data)
            
            if event:
                self.trigger_global_event('event_scheduled', {
                    'context': 'background',
                    'name': name,
                    'delay': delay
                })
            
            return event
        return None
    
    def register_global_callback(self, event_type, callback):
        """Registrar callback global para eventos"""
        if event_type not in self.global_callbacks:
            self.global_callbacks[event_type] = []
        self.global_callbacks[event_type].append(callback)
    
    def unregister_global_callback(self, event_type, callback):
        """Desregistrar callback global"""
        if event_type in self.global_callbacks and callback in self.global_callbacks[event_type]:
            self.global_callbacks[event_type].remove(callback)
            if not self.global_callbacks[event_type]:
                del self.global_callbacks[event_type]
    
    def register_context_callback(self, context, callback):
        """Registrar callback para eventos de contexto especifico"""
        if context not in self.context_callbacks:
            self.context_callbacks[context] = []
        self.context_callbacks[context].append(callback)
    
    def trigger_global_event(self, event_type, data=None):
        """Disparar evento global"""
        if event_type in self.global_callbacks:
            for callback in self.global_callbacks[event_type]:
                try:
                    if data is not None:
                        callback(data)
                    else:
                        callback()
                except Exception as e:
                    print(f"ERROR en callback global {event_type}: {e}")
    
    def calculate_fps(self, delta_time):
        """Calcular FPS basado en delta_time"""
        if delta_time > 0:
            current_fps = 1.0 / delta_time
            
            # Mantener historial de FPS
            fps_history = self.performance_stats['fps_history']
            fps_history.append(current_fps)
            
            # Limitar tamaño del historial
            if len(fps_history) > self.performance_stats['fps_history_size']:
                fps_history.pop(0)
            
            return current_fps
        return 0
    
    def get_average_fps(self):
        """Obtener FPS promedio del historial"""
        fps_history = self.performance_stats['fps_history']
        if fps_history:
            return sum(fps_history) / len(fps_history)
        return 0
    
    def check_performance_alerts(self, update_duration, current_fps):
        """Verificar alertas de rendimiento"""
        alerts = []
        
        # Alerta de alto uso de CPU
        if update_duration > self.alert_thresholds['high_cpu_usage']:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f'Update time: {update_duration:.4f}s',
                'threshold': self.alert_thresholds['high_cpu_usage']
            })
        
        # Alerta de caida de FPS
        if current_fps < self.alert_thresholds['fps_drop_threshold']:
            alerts.append({
                'type': 'fps_drop',
                'severity': 'warning',
                'message': f'FPS: {current_fps:.1f}',
                'threshold': self.alert_thresholds['fps_drop_threshold']
            })
        
        # Alerta de posible memory leak
        total_timers = 0
        if self.ui_timer_system:
            total_timers += len(self.ui_timer_system.timers)
        if self.background_timer_system:
            total_timers += len(self.background_timer_system.timers)
        
        if total_timers > self.alert_thresholds['memory_leak_detection']:
            alerts.append({
                'type': 'memory_leak_detection',
                'severity': 'critical',
                'message': f'Timers: {total_timers}',
                'threshold': self.alert_thresholds['memory_leak_detection']
            })
        
        # Disparar eventos de alerta
        for alert in alerts:
            self.trigger_global_event('performance_alert', alert)
        
        return alerts
    
    def auto_adjust_quality(self, current_fps):
        """Ajustar automaticamente la calidad basado en rendimiento"""
        if not self.quality_settings['auto_quality_adjust']:
            return
        
        if current_fps < self.quality_settings['min_fps']:
            # Reducir calidad
            if self.global_time_scale > 0.8:
                self.set_global_time_scale(self.global_time_scale * 0.95)
                self.trigger_global_event('quality_adjusted', {
                    'action': 'reduced',
                    'new_time_scale': self.global_time_scale,
                    'fps': current_fps
                })
        
        elif current_fps > self.quality_settings['max_fps'] * 0.9:
            # Aumentar calidad si esta muy por encima
            if self.global_time_scale < 1.0:
                self.set_global_time_scale(min(1.0, self.global_time_scale * 1.02))
                self.trigger_global_event('quality_adjusted', {
                    'action': 'increased',
                    'new_time_scale': self.global_time_scale,
                    'fps': current_fps
                })
    
    def update(self, delta_time):
        """Actualizar todos los sistemas de temporizadores"""
        if self.global_paused:
            return
        
        update_start_time = time.time()
        
        # Aplicar escala de tiempo global
        scaled_delta = delta_time * self.global_time_scale
        
        # Calcular FPS actual
        current_fps = self.calculate_fps(delta_time)
        
        # Actualizar por orden de prioridad de contexto
        sorted_contexts = sorted(
            [ctx for ctx in self.active_contexts if ctx not in self.paused_contexts], 
            key=lambda c: self.context_priorities.get(c, 0), 
            reverse=True
        )
        
        for context in sorted_contexts:
            if context == TimerContext.UI and self.ui_timer_system:
                self.ui_timer_system.update(scaled_delta)
            elif context == TimerContext.BACKGROUND and self.background_timer_system:
                self.background_timer_system.update(scaled_delta)
        
        # Actualizar estadisticas de rendimiento
        self.total_updates += 1
        update_duration = time.time() - update_start_time
        
        self.performance_stats['last_update_time'] = update_duration
        self.performance_stats['max_update_time'] = max(
            self.performance_stats['max_update_time'], 
            update_duration
        )
        self.performance_stats['total_update_time'] += update_duration
        
        # Calcular promedio móvil simple
        alpha = 0.1  # Factor de suavizado
        self.performance_stats['avg_update_time'] = (
            (1 - alpha) * self.performance_stats['avg_update_time'] + 
            alpha * update_duration
        )
        
        # Verificar alertas de rendimiento
        alerts = self.check_performance_alerts(update_duration, current_fps)
        
        # Ajuste automatico de calidad
        self.auto_adjust_quality(current_fps)
        
        # Disparar evento de update completado
        if self.total_updates % 60 == 0:  # Cada 60 updates (~1 segundo a 60fps)
            self.trigger_global_event('periodic_update', {
                'updates': self.total_updates,
                'avg_fps': self.get_average_fps(),
                'avg_update_time': self.performance_stats['avg_update_time'],
                'active_contexts': [ctx.value for ctx in self.active_contexts]
            })
    
    def get_ui_timer(self, name):
        """Obtener temporizador de UI por nombre"""
        if self.ui_timer_system:
            return self.ui_timer_system.get_timer(name)
        return None
    
    def get_background_timer(self, name):
        """Obtener temporizador de fondo por nombre"""
        if self.background_timer_system:
            return self.background_timer_system.get_timer(name)
        return None
    
    def remove_ui_timer(self, name):
        """Remover temporizador de UI"""
        if self.ui_timer_system:
            success = self.ui_timer_system.remove_timer(name)
            if success:
                self.trigger_global_event('timer_removed', {
                    'context': 'ui',
                    'name': name
                })
            return success
        return False
    
    def remove_background_timer(self, name):
        """Remover temporizador de fondo"""
        if self.background_timer_system:
            success = self.background_timer_system.remove_timer(name)
            if success:
                self.trigger_global_event('timer_removed', {
                    'context': 'background',
                    'name': name
                })
            return success
        return False
    
    def get_comprehensive_stats(self):
        """Obtener estadisticas comprehensivas de todos los sistemas"""
        stats = {
            'global': {
                'uptime': time.time() - self.start_time,
                'global_paused': self.global_paused,
                'time_scale': self.global_time_scale,
                'active_contexts': [c.value for c in self.active_contexts],
                'paused_contexts': [c.value for c in self.paused_contexts],
                'total_updates': self.total_updates,
                'performance': self.performance_stats.copy(),
                'current_fps': self.get_average_fps(),
                'quality_settings': self.quality_settings.copy()
            }
        }
        
        if self.ui_timer_system:
            stats['ui'] = self.ui_timer_system.get_system_stats()
            stats['ui']['performance_report'] = self.ui_timer_system.get_performance_report()
        
        if self.background_timer_system:
            stats['background'] = self.background_timer_system.get_system_info()
            if hasattr(self.background_timer_system, 'get_detailed_stats'):
                stats['background']['detailed'] = self.background_timer_system.get_detailed_stats()
        
        return stats
    
    def emergency_stop(self):
        """Parada de emergencia de todos los sistemas"""
        self.pause_global()
        
        if self.ui_timer_system:
            self.ui_timer_system.clear_all()
        if self.background_timer_system:
            self.background_timer_system.clear_all()
        
        self.global_callbacks.clear()
        self.context_callbacks.clear()
        
        self.trigger_global_event('emergency_stop', {
            'timestamp': time.time(),
            'reason': 'Manual emergency stop'
        })
        
        print("EMERGENCY STOP: Todos los temporizadores detenidos y limpiados")
    
    def get_system_health(self):
        """Obtener indicadores de salud del sistema"""
        health = {
            'status': 'healthy',
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Verificar rendimiento
        avg_fps = self.get_average_fps()
        if avg_fps > 0 and avg_fps < 45:
            health['warnings'].append(f'FPS bajo detectado: {avg_fps:.1f}')
            health['recommendations'].append('Considerar reducir efectos visuales')
        
        if self.performance_stats['avg_update_time'] > 0.020:  # >20ms
            health['warnings'].append('Tiempo de actualización alto')
            health['recommendations'].append('Optimizar temporizadores activos')
        
        # Verificar carga de temporizadores
        total_timers = 0
        if self.ui_timer_system:
            ui_stats = self.ui_timer_system.get_system_stats()
            total_timers += ui_stats['total_timers']
            if ui_stats['total_timers'] > 80:
                health['warnings'].append('Alto número de temporizadores de UI')
        
        if self.background_timer_system:
            bg_stats = self.background_timer_system.get_system_info()
            total_timers += bg_stats['total_timers']
            if bg_stats['total_timers'] > 40:
                health['warnings'].append('Alto número de temporizadores de fondo')
        
        if total_timers > 150:
            health['errors'].append('Número crítico de temporizadores activos')
            health['recommendations'].append('Limpiar temporizadores no utilizados')
        
        # Verificar contextos
        if len(self.active_contexts) == 0:
            health['warnings'].append('No hay contextos activos')
        
        if len(self.paused_contexts) > 0:
            health['warnings'].append(f'Contextos pausados: {[c.value for c in self.paused_contexts]}')
        
        # Determinar estado general
        if health['errors']:
            health['status'] = 'critical'
        elif len(health['warnings']) > 3:
            health['status'] = 'warning'
        elif health['warnings']:
            health['status'] = 'caution'
        
        return health
    
    def create_performance_snapshot(self):
        """Crear snapshot detallado del rendimiento actual"""
        return {
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'fps': {
                'current': self.get_average_fps(),
                'history': self.performance_stats['fps_history'].copy(),
                'target': self.quality_settings['max_fps']
            },
            'update_times': {
                'average': self.performance_stats['avg_update_time'],
                'maximum': self.performance_stats['max_update_time'],
                'last': self.performance_stats['last_update_time'],
                'total': self.performance_stats['total_update_time']
            },
            'timer_counts': {
                'ui': len(self.ui_timer_system.timers) if self.ui_timer_system else 0,
                'background': len(self.background_timer_system.timers) if self.background_timer_system else 0
            },
            'contexts': {
                'active': [c.value for c in self.active_contexts],
                'paused': [c.value for c in self.paused_contexts]
            },
            'system_state': {
                'global_paused': self.global_paused,
                'time_scale': self.global_time_scale,
                'total_updates': self.total_updates
            },
            'health': self.get_system_health()
        }
    
    def debug_dump_all(self):
        """Volcar toda la informacion de debug de todos los sistemas"""
        print("=== GLOBAL TIMER MANAGER DEBUG DUMP ===")
        
        # Informacion global
        print(f"Uptime: {time.time() - self.start_time:.2f}s")
        print(f"Global paused: {self.global_paused}")
        print(f"Time scale: {self.global_time_scale}")
        print(f"Total updates: {self.total_updates}")
        print(f"Average FPS: {self.get_average_fps():.1f}")
        
        # Contextos
        print(f"\nActive contexts: {[c.value for c in self.active_contexts]}")
        print(f"Paused contexts: {[c.value for c in self.paused_contexts]}")
        
        # Sistemas individuales
        if self.ui_timer_system:
            print("\n--- UI TIMER SYSTEM ---")
            self.ui_timer_system.debug_dump()
        
        if self.background_timer_system:
            print("\n--- BACKGROUND TIMER SYSTEM ---")
            bg_stats = self.background_timer_system.get_detailed_stats()
            print(f"Active timers: {bg_stats['active_timers']}")
            print(f"Total created: {bg_stats['total_created']}")
            print(f"Total executions: {bg_stats['total_executions']}")
        
        # Salud del sistema
        health = self.get_system_health()
        print(f"\n--- SYSTEM HEALTH ---")
        print(f"Status: {health['status']}")
        if health['warnings']:
            print(f"Warnings: {health['warnings']}")
        if health['errors']:
            print(f"Errors: {health['errors']}")
        
        print("=== END GLOBAL DEBUG DUMP ===\n")


# Instancia global singleton
_global_timer_manager = None

def get_global_timer_manager():
    """Obtener instancia global del manejador de temporizadores"""
    global _global_timer_manager
    if _global_timer_manager is None:
        _global_timer_manager = GlobalTimerManager()
    return _global_timer_manager

def reset_global_timer_manager():
    """Resetear la instancia global (util para testing)"""
    global _global_timer_manager
    if _global_timer_manager:
        _global_timer_manager.emergency_stop()
    _global_timer_manager = None