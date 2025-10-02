import time
import random

class BackgroundTimer:
    """Clase para manejar un temporizador individual de fondo"""
    
    def __init__(self, duration, callback, repeat=False, name="timer"):
        self.duration = duration  # Duracion en segundos
        self.callback = callback  # Funcion a ejecutar
        self.repeat = repeat      # Si se repite automaticamente
        self.name = name         # Nombre identificador
        
        self.elapsed_time = 0.0
        self.active = True
        self.paused = False
        
        # Para temporizadores aleatorios
        self.randomize_duration = False
        self.min_duration = duration
        self.max_duration = duration
        
        # Metadatos
        self.creation_time = time.time()
        self.execution_count = 0
        self.last_execution_time = None
    
    def set_random_duration(self, min_duration, max_duration):
        """Establecer duracion aleatoria para el temporizador"""
        self.randomize_duration = True
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.randomize_next_duration()
    
    def randomize_next_duration(self):
        """Generar siguiente duracion aleatoria"""
        if self.randomize_duration:
            self.duration = random.uniform(self.min_duration, self.max_duration)
    
    def update(self, delta_time):
        """Actualizar el temporizador"""
        if not self.active or self.paused:
            return False
        
        self.elapsed_time += delta_time
        
        if self.elapsed_time >= self.duration:
            # Ejecutar callback
            try:
                self.callback()
                self.execution_count += 1
                self.last_execution_time = time.time()
            except Exception as e:
                print(f"ERROR en temporizador {self.name}: {e}")
            
            # Resetear o desactivar
            if self.repeat:
                self.elapsed_time = 0.0
                if self.randomize_duration:
                    self.randomize_next_duration()
            else:
                self.active = False
            
            return True  # Indica que se ejecuto el callback
        
        return False
    
    def reset(self):
        """Resetear el temporizador"""
        self.elapsed_time = 0.0
        self.active = True
        if self.randomize_duration:
            self.randomize_next_duration()
    
    def pause(self):
        """Pausar el temporizador"""
        self.paused = True
    
    def resume(self):
        """Reanudar el temporizador"""
        self.paused = False
    
    def stop(self):
        """Detener el temporizador"""
        self.active = False
    
    def get_progress(self):
        """Obtener progreso del temporizador (0.0 - 1.0)"""
        if self.duration == 0:
            return 1.0
        return min(self.elapsed_time / self.duration, 1.0)
    
    def get_remaining_time(self):
        """Obtener tiempo restante"""
        return max(0, self.duration - self.elapsed_time)
    
    def get_age(self):
        """Obtener edad del temporizador en segundos"""
        return time.time() - self.creation_time


class ScheduledEvent:
    """Clase para eventos programados de fondo"""
    
    def __init__(self, trigger_time, callback, name="event", data=None):
        self.trigger_time = trigger_time  # Tiempo absoluto para ejecutar
        self.callback = callback          # Funcion a ejecutar
        self.name = name                 # Nombre del evento
        self.data = data                 # Datos adicionales
        self.executed = False            # Si ya se ejecuto
        
        # Metadatos
        self.creation_time = time.time()
        self.execution_time = None
    
    def should_execute(self, current_time):
        """Verificar si el evento debe ejecutarse"""
        return not self.executed and current_time >= self.trigger_time
    
    def execute(self):
        """Ejecutar el evento"""
        if not self.executed:
            try:
                if self.data:
                    self.callback(self.data)
                else:
                    self.callback()
                self.executed = True
                self.execution_time = time.time()
                return True
            except Exception as e:
                print(f"ERROR en evento {self.name}: {e}")
        return False
    
    def get_delay_until_trigger(self):
        """Obtener tiempo restante hasta la ejecucion"""
        return max(0, self.trigger_time - time.time())


class BackgroundTimerSystem:
    """Sistema de gestion de temporizadores y eventos para el fondo"""
    
    def __init__(self):
        self.timers = {}
        self.scheduled_events = []
        self.start_time = time.time()
        self.paused = False
        
        # Callbacks para diferentes tipos de eventos
        self.event_callbacks = {}
        
        # Estadisticas
        self.total_timers_created = 0
        self.total_events_created = 0
        self.total_executions = 0
        
        # Configuracion
        self.max_timers = 50  # Limite de temporizadores activos
        self.cleanup_interval = 60.0  # Intervalo de limpieza en segundos
        self.last_cleanup = time.time()
    
    def add_timer(self, name, duration, callback, repeat=False):
        """Agregar un temporizador"""
        if len(self.timers) >= self.max_timers:
            self.cleanup_inactive_timers()
            if len(self.timers) >= self.max_timers:
                print(f"WARNING: Limite de temporizadores de fondo alcanzado ({self.max_timers})")
                return None
        
        timer = BackgroundTimer(duration, callback, repeat, name)
        self.timers[name] = timer
        self.total_timers_created += 1
        return timer
    
    def add_random_timer(self, name, min_duration, max_duration, callback, repeat=False):
        """Agregar temporizador con duracion aleatoria"""
        timer = self.add_timer(name, min_duration, callback, repeat)
        if timer:
            timer.set_random_duration(min_duration, max_duration)
        return timer
    
    def remove_timer(self, name):
        """Remover un temporizador"""
        if name in self.timers:
            del self.timers[name]
            return True
        return False
    
    def get_timer(self, name):
        """Obtener un temporizador por nombre"""
        return self.timers.get(name)
    
    def pause_timer(self, name):
        """Pausar un temporizador especifico"""
        if name in self.timers:
            self.timers[name].pause()
    
    def resume_timer(self, name):
        """Reanudar un temporizador especifico"""
        if name in self.timers:
            self.timers[name].resume()
    
    def reset_timer(self, name):
        """Resetear un temporizador especifico"""
        if name in self.timers:
            self.timers[name].reset()
    
    def schedule_event(self, delay, callback, name="event", data=None):
        """Programar un evento para ejecutar despues de X segundos"""
        trigger_time = time.time() + delay
        event = ScheduledEvent(trigger_time, callback, name, data)
        self.scheduled_events.append(event)
        self.total_events_created += 1
        return event
    
    def schedule_absolute_event(self, trigger_time, callback, name="event", data=None):
        """Programar evento para tiempo absoluto"""
        event = ScheduledEvent(trigger_time, callback, name, data)
        self.scheduled_events.append(event)
        self.total_events_created += 1
        return event
    
    def register_event_callback(self, event_type, callback):
        """Registrar callback para tipo de evento"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def trigger_event(self, event_type, data=None):
        """Disparar eventos de un tipo especifico"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    if data:
                        callback(data)
                    else:
                        callback()
                    self.total_executions += 1
                except Exception as e:
                    print(f"ERROR en callback de evento {event_type}: {e}")
    
    def cleanup_inactive_timers(self):
        """Limpiar temporizadores inactivos"""
        inactive_timers = [name for name, timer in self.timers.items() if not timer.active]
        for name in inactive_timers:
            del self.timers[name]
        return len(inactive_timers)
    
    def update(self, delta_time):
        """Actualizar todos los temporizadores y eventos"""
        if self.paused:
            return
        
        current_time = time.time()
        
        # Limpieza periodica
        if current_time - self.last_cleanup > self.cleanup_interval:
            cleaned = self.cleanup_inactive_timers()
            self.last_cleanup = current_time
            if cleaned > 0:
                print(f"DEBUG: Limpiados {cleaned} temporizadores inactivos de fondo")
        
        # Actualizar temporizadores
        for timer in list(self.timers.values()):
            if timer.update(delta_time):
                self.total_executions += 1
        
        # Procesar eventos programados
        for event in self.scheduled_events[:]:
            if event.should_execute(current_time):
                if event.execute():
                    self.total_executions += 1
                self.scheduled_events.remove(event)
    
    def pause_all(self):
        """Pausar todo el sistema"""
        self.paused = True
        for timer in self.timers.values():
            timer.pause()
    
    def resume_all(self):
        """Reanudar todo el sistema"""
        self.paused = False
        for timer in self.timers.values():
            timer.resume()
    
    def clear_all(self):
        """Limpiar todos los temporizadores y eventos"""
        self.timers.clear()
        self.scheduled_events.clear()
        self.event_callbacks.clear()
    
    def get_timers_by_pattern(self, pattern):
        """Obtener temporizadores que coincidan con un patron en el nombre"""
        return {name: timer for name, timer in self.timers.items() if pattern in name}
    
    def pause_timers_by_pattern(self, pattern):
        """Pausar temporizadores que coincidan con un patron"""
        count = 0
        for name, timer in self.timers.items():
            if pattern in name:
                timer.pause()
                count += 1
        return count
    
    def resume_timers_by_pattern(self, pattern):
        """Reanudar temporizadores que coincidan con un patron"""
        count = 0
        for name, timer in self.timers.items():
            if pattern in name:
                timer.resume()
                count += 1
        return count
    
    def get_system_info(self):
        """Obtener informacion del sistema"""
        active_timers = len([t for t in self.timers.values() if t.active])
        paused_timers = len([t for t in self.timers.values() if t.paused])
        
        return {
            'active_timers': active_timers,
            'paused_timers': paused_timers,
            'total_timers': len(self.timers),
            'scheduled_events': len(self.scheduled_events),
            'total_created': self.total_timers_created,
            'total_executions': self.total_executions,
            'system_paused': self.paused,
            'uptime': time.time() - self.start_time
        }
    
    def get_detailed_stats(self):
        """Obtener estadisticas detalladas"""
        stats = self.get_system_info()
        
        # Estadisticas de temporizadores
        timer_stats = {
            'repeating_timers': len([t for t in self.timers.values() if t.repeat]),
            'random_timers': len([t for t in self.timers.values() if t.randomize_duration]),
            'oldest_timer_age': 0,
            'most_executed_timer': {'name': None, 'count': 0}
        }
        
        if self.timers:
            # Temporizador mas viejo
            oldest_timer = max(self.timers.values(), key=lambda t: t.get_age())
            timer_stats['oldest_timer_age'] = oldest_timer.get_age()
            
            # Temporizador mas ejecutado
            most_executed = max(self.timers.values(), key=lambda t: t.execution_count)
            timer_stats['most_executed_timer'] = {
                'name': most_executed.name,
                'count': most_executed.execution_count
            }
        
        # Estadisticas de eventos
        event_stats = {
            'pending_events': len(self.scheduled_events),
            'events_in_next_minute': len([
                e for e in self.scheduled_events 
                if e.get_delay_until_trigger() <= 60
            ])
        }
        
        stats.update({
            'timer_details': timer_stats,
            'event_details': event_stats
        })
        
        return stats