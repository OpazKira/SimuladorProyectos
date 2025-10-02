import time
import random
from enum import Enum

class TimerPriority(Enum):
    """Prioridades para temporizadores de UI"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class UITimer:
    """Temporizador para elementos de interfaz de usuario"""
    
    def __init__(self, duration, callback, repeat=False, name="ui_timer", priority=TimerPriority.NORMAL):
        self.duration = duration
        self.callback = callback
        self.repeat = repeat
        self.name = name
        self.priority = priority
        
        self.elapsed_time = 0.0
        self.active = True
        self.paused = False
        
        # Metadatos del temporizador
        self.creation_time = time.time()
        self.execution_count = 0
        self.last_execution_time = None
        
        # Para temporizadores con interpolacion
        self.interpolation_callback = None
        self.start_value = None
        self.end_value = None
        
        # Para temporizadores condicionales
        self.condition_callback = None
        
        # Etiquetas para organizacion
        self.tags = set()
        
        # Control de easing para animaciones
        self.easing_function = None
    
    def set_interpolation(self, start_value, end_value, interpolation_callback):
        """Configurar interpolacion de valores durante la duracion del timer"""
        self.start_value = start_value
        self.end_value = end_value
        self.interpolation_callback = interpolation_callback
    
    def set_condition(self, condition_callback):
        """Establecer condicion que debe cumplirse para ejecutar el callback"""
        self.condition_callback = condition_callback
    
    def set_easing(self, easing_function):
        """Establecer funcion de easing para suavizar animaciones"""
        self.easing_function = easing_function
    
    def add_tag(self, tag):
        """Agregar etiqueta al temporizador"""
        self.tags.add(tag)
    
    def remove_tag(self, tag):
        """Remover etiqueta del temporizador"""
        self.tags.discard(tag)
    
    def has_tag(self, tag):
        """Verificar si tiene una etiqueta especifica"""
        return tag in self.tags
    
    def apply_easing(self, progress):
        """Aplicar funcion de easing al progreso"""
        if self.easing_function:
            return self.easing_function(progress)
        return progress
    
    def update(self, delta_time):
        """Actualizar temporizador de UI"""
        if not self.active or self.paused:
            return False
        
        self.elapsed_time += delta_time
        raw_progress = min(self.elapsed_time / self.duration, 1.0)
        
        # Aplicar easing al progreso
        eased_progress = self.apply_easing(raw_progress)
        
        # Llamar interpolacion si esta configurada
        if self.interpolation_callback and self.start_value is not None and self.end_value is not None:
            try:
                # Calcular valor interpolado
                if isinstance(self.start_value, (int, float)) and isinstance(self.end_value, (int, float)):
                    interpolated_value = self.start_value + (self.end_value - self.start_value) * eased_progress
                else:
                    interpolated_value = eased_progress
                
                self.interpolation_callback(interpolated_value, eased_progress)
            except Exception as e:
                print(f"ERROR en interpolacion de timer {self.name}: {e}")
        
        # Verificar si debe ejecutarse el callback principal
        if self.elapsed_time >= self.duration:
            # Verificar condicion si existe
            should_execute = True
            if self.condition_callback:
                try:
                    should_execute = self.condition_callback()
                except Exception as e:
                    print(f"ERROR en condicion de timer {self.name}: {e}")
                    should_execute = False
            
            if should_execute:
                try:
                    self.callback()
                    self.execution_count += 1
                    self.last_execution_time = time.time()
                except Exception as e:
                    print(f"ERROR en callback de timer {self.name}: {e}")
            
            # Resetear o desactivar
            if self.repeat:
                self.elapsed_time = 0.0
            else:
                self.active = False
            
            return True
        
        return False
    
    def get_progress(self):
        """Obtener progreso normalizado (0.0 - 1.0)"""
        if self.duration == 0:
            return 1.0
        return min(self.elapsed_time / self.duration, 1.0)
    
    def get_eased_progress(self):
        """Obtener progreso con easing aplicado"""
        return self.apply_easing(self.get_progress())
    
    def get_remaining_time(self):
        """Obtener tiempo restante"""
        return max(0, self.duration - self.elapsed_time)
    
    def reset(self):
        """Resetear temporizador"""
        self.elapsed_time = 0.0
        self.active = True
        self.paused = False
    
    def extend_duration(self, additional_time):
        """Extender la duracion del temporizador"""
        self.duration += additional_time
    
    def get_age(self):
        """Obtener edad del temporizador en segundos"""
        return time.time() - self.creation_time
    
    def get_info(self):
        """Obtener informacion completa del temporizador"""
        return {
            'name': self.name,
            'priority': self.priority.name,
            'progress': self.get_progress(),
            'eased_progress': self.get_eased_progress(),
            'remaining_time': self.get_remaining_time(),
            'execution_count': self.execution_count,
            'active': self.active,
            'paused': self.paused,
            'tags': list(self.tags),
            'age': self.get_age(),
            'repeat': self.repeat,
            'has_interpolation': self.interpolation_callback is not None,
            'has_condition': self.condition_callback is not None,
            'has_easing': self.easing_function is not None
        }


class UIScheduledEvent:
    """Evento programado para interfaces de usuario"""
    
    def __init__(self, trigger_time, callback, name="ui_event", data=None, priority=TimerPriority.NORMAL):
        self.trigger_time = trigger_time
        self.callback = callback
        self.name = name
        self.data = data
        self.priority = priority
        self.executed = False
        self.creation_time = time.time()
        
        # Condiciones de ejecucion
        self.condition_callback = None
        self.max_delay = None  # Tiempo maximo para ejecutar despues del trigger
        
        # Metadatos
        self.tags = set()
        self.execution_time = None
    
    def set_condition(self, condition_callback):
        """Establecer condicion para la ejecucion"""
        self.condition_callback = condition_callback
    
    def set_max_delay(self, max_delay):
        """Establecer tiempo maximo de retraso permitido"""
        self.max_delay = max_delay
    
    def add_tag(self, tag):
        """Agregar etiqueta al evento"""
        self.tags.add(tag)
    
    def has_tag(self, tag):
        """Verificar si tiene una etiqueta especifica"""
        return tag in self.tags
    
    def should_execute(self, current_time):
        """Verificar si debe ejecutarse"""
        if self.executed:
            return False
        
        if current_time < self.trigger_time:
            return False
        
        # Verificar si ha pasado demasiado tiempo
        if self.max_delay and (current_time - self.trigger_time) > self.max_delay:
            self.executed = True  # Marcar como perdido
            return False
        
        return True
    
    def execute(self):
        """Ejecutar el evento"""
        if self.executed:
            return False
        
        # Verificar condicion si existe
        if self.condition_callback:
            try:
                if not self.condition_callback():
                    return False
            except Exception as e:
                print(f"ERROR en condicion de evento {self.name}: {e}")
                return False
        
        try:
            if self.data is not None:
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


class EasingFunctions:
    """Funciones de easing para animaciones suaves"""
    
    @staticmethod
    def ease_in_quad(t):
        """Ease in cuadratico"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t):
        """Ease out cuadratico"""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t):
        """Ease in-out cuadratico"""
        if t < 0.5:
            return 2 * t * t
        return 1 - 2 * (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_cubic(t):
        """Ease in cubico"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t):
        """Ease out cubico"""
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def ease_in_out_cubic(t):
        """Ease in-out cubico"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - 4 * (1 - t) ** 3
    
    @staticmethod
    def ease_out_bounce(t):
        """Efecto de rebote al final"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375


class UITimerSystem:
    """Sistema de gestion de temporizadores para interfaces de usuario"""
    
    def __init__(self):
        self.timers = {}
        self.scheduled_events = []
        self.start_time = time.time()
        self.paused = False
        
        # Sistema de callbacks por etiquetas
        self.tag_callbacks = {}
        
        # Estadisticas
        self.total_timers_created = 0
        self.total_events_created = 0
        self.total_executions = 0
        
        # Configuracion
        self.max_timers = 100  # Limite de temporizadores activos
        self.cleanup_interval = 30.0  # Intervalo de limpieza en segundos
        self.last_cleanup = time.time()
        
        # Monitoreo de rendimiento
        self.performance_stats = {
            'avg_update_time': 0.0,
            'max_update_time': 0.0,
            'update_count': 0
        }
    
    def add_timer(self, name, duration, callback, repeat=False, priority=TimerPriority.NORMAL):
        """Agregar temporizador de UI"""
        if len(self.timers) >= self.max_timers:
            self.cleanup_inactive_timers()
            if len(self.timers) >= self.max_timers:
                print(f"WARNING: Limite de temporizadores alcanzado ({self.max_timers})")
                return None
        
        timer = UITimer(duration, callback, repeat, name, priority)
        self.timers[name] = timer
        self.total_timers_created += 1
        return timer
    
    def add_interpolation_timer(self, name, duration, start_value, end_value, 
                              interpolation_callback, completion_callback=None, 
                              priority=TimerPriority.NORMAL, easing=None):
        """Agregar temporizador con interpolacion de valores"""
        timer = self.add_timer(name, duration, completion_callback or (lambda: None), False, priority)
        if timer:
            timer.set_interpolation(start_value, end_value, interpolation_callback)
            if easing:
                timer.set_easing(easing)
        return timer
    
    def add_conditional_timer(self, name, duration, callback, condition_callback, 
                            repeat=False, priority=TimerPriority.NORMAL):
        """Agregar temporizador con condicion de ejecucion"""
        timer = self.add_timer(name, duration, callback, repeat, priority)
        if timer:
            timer.set_condition(condition_callback)
        return timer
    
    def add_eased_timer(self, name, duration, callback, easing_function, repeat=False):
        """Agregar temporizador con easing"""
        timer = self.add_timer(name, duration, callback, repeat)
        if timer:
            timer.set_easing(easing_function)
        return timer
    
    def schedule_event(self, delay, callback, name="ui_event", data=None, priority=TimerPriority.NORMAL):
        """Programar evento para ejecutar despues de X segundos"""
        trigger_time = time.time() + delay
        event = UIScheduledEvent(trigger_time, callback, name, data, priority)
        self.scheduled_events.append(event)
        self.total_events_created += 1
        return event
    
    def schedule_conditional_event(self, delay, callback, condition_callback, 
                                 name="conditional_event", data=None):
        """Programar evento con condicion"""
        event = self.schedule_event(delay, callback, name, data)
        if event:
            event.set_condition(condition_callback)
        return event
    
    def get_timer(self, name):
        """Obtener temporizador por nombre"""
        return self.timers.get(name)
    
    def remove_timer(self, name):
        """Remover temporizador especifico"""
        if name in self.timers:
            del self.timers[name]
            return True
        return False
    
    def pause_timer(self, name):
        """Pausar temporizador especifico"""
        if name in self.timers:
            self.timers[name].paused = True
    
    def resume_timer(self, name):
        """Reanudar temporizador especifico"""
        if name in self.timers:
            self.timers[name].paused = False
    
    def get_timers_by_tag(self, tag):
        """Obtener temporizadores por etiqueta"""
        return [timer for timer in self.timers.values() if timer.has_tag(tag)]
    
    def pause_timers_by_tag(self, tag):
        """Pausar todos los temporizadores con una etiqueta"""
        count = 0
        for timer in self.get_timers_by_tag(tag):
            timer.paused = True
            count += 1
        return count
    
    def resume_timers_by_tag(self, tag):
        """Reanudar todos los temporizadores con una etiqueta"""
        count = 0
        for timer in self.get_timers_by_tag(tag):
            timer.paused = False
            count += 1
        return count
    
    def remove_timers_by_tag(self, tag):
        """Remover todos los temporizadores con una etiqueta"""
        to_remove = [name for name, timer in self.timers.items() if timer.has_tag(tag)]
        for name in to_remove:
            del self.timers[name]
        return len(to_remove)
    
    def get_timers_by_priority(self, priority):
        """Obtener temporizadores por prioridad"""
        return [timer for timer in self.timers.values() if timer.priority == priority]
    
    def register_tag_callback(self, tag, callback):
        """Registrar callback que se ejecuta cuando se completa cualquier timer con esta etiqueta"""
        if tag not in self.tag_callbacks:
            self.tag_callbacks[tag] = []
        self.tag_callbacks[tag].append(callback)
    
    def unregister_tag_callback(self, tag, callback):
        """Desregistrar callback de etiqueta"""
        if tag in self.tag_callbacks and callback in self.tag_callbacks[tag]:
            self.tag_callbacks[tag].remove(callback)
            if not self.tag_callbacks[tag]:
                del self.tag_callbacks[tag]
    
    def cleanup_inactive_timers(self):
        """Limpiar temporizadores inactivos"""
        inactive = [name for name, timer in self.timers.items() if not timer.active]
        for name in inactive:
            del self.timers[name]
        return len(inactive)
    
    def update(self, delta_time):
        """Actualizar sistema de temporizadores de UI"""
        if self.paused:
            return
        
        update_start = time.time()
        current_time = time.time()
        
        # Limpieza periodica
        if current_time - self.last_cleanup > self.cleanup_interval:
            cleaned = self.cleanup_inactive_timers()
            self.last_cleanup = current_time
            if cleaned > 0:
                print(f"DEBUG: Limpiados {cleaned} temporizadores inactivos de UI")
        
        # Actualizar temporizadores por prioridad (CRITICAL primero)
        sorted_timers = sorted(self.timers.values(), key=lambda t: t.priority.value, reverse=True)
        
        for timer in sorted_timers:
            if timer.update(delta_time):
                self.total_executions += 1
                # Ejecutar callbacks de etiquetas
                for tag in timer.tags:
                    if tag in self.tag_callbacks:
                        for callback in self.tag_callbacks[tag]:
                            try:
                                callback(timer)
                            except Exception as e:
                                print(f"ERROR en callback de etiqueta {tag}: {e}")
        
        # Procesar eventos programados por prioridad
        sorted_events = sorted(self.scheduled_events, key=lambda e: e.priority.value, reverse=True)
        
        for event in sorted_events[:]:
            if event.should_execute(current_time):
                if event.execute():
                    self.total_executions += 1
                self.scheduled_events.remove(event)
        
        # Actualizar estadisticas de rendimiento
        update_duration = time.time() - update_start
        self.performance_stats['update_count'] += 1
        self.performance_stats['max_update_time'] = max(
            self.performance_stats['max_update_time'], 
            update_duration
        )
        
        # Promedio movil simple
        alpha = 0.1
        self.performance_stats['avg_update_time'] = (
            (1 - alpha) * self.performance_stats['avg_update_time'] + 
            alpha * update_duration
        )
    
    def pause_all(self):
        """Pausar todo el sistema"""
        self.paused = True
        for timer in self.timers.values():
            timer.paused = True
    
    def resume_all(self):
        """Reanudar todo el sistema"""
        self.paused = False
        for timer in self.timers.values():
            timer.paused = False
    
    def clear_all(self):
        """Limpiar todo el sistema"""
        self.timers.clear()
        self.scheduled_events.clear()
        self.tag_callbacks.clear()
    
    def clear_by_pattern(self, pattern):
        """Limpiar temporizadores que contengan un patron en el nombre"""
        to_remove = [name for name in self.timers.keys() if pattern in name]
        for name in to_remove:
            del self.timers[name]
        return len(to_remove)
    
    def get_system_stats(self):
        """Obtener estadisticas del sistema"""
        active_timers = len([t for t in self.timers.values() if t.active])
        paused_timers = len([t for t in self.timers.values() if t.paused])
        interpolation_timers = len([t for t in self.timers.values() if t.interpolation_callback])
        conditional_timers = len([t for t in self.timers.values() if t.condition_callback])
        
        return {
            'active_timers': active_timers,
            'paused_timers': paused_timers,
            'total_timers': len(self.timers),
            'interpolation_timers': interpolation_timers,
            'conditional_timers': conditional_timers,
            'scheduled_events': len(self.scheduled_events),
            'total_created': self.total_timers_created,
            'total_events_created': self.total_events_created,
            'total_executions': self.total_executions,
            'system_paused': self.paused,
            'uptime': time.time() - self.start_time,
            'performance': self.performance_stats.copy()
        }
    
    def get_timer_info(self, name):
        """Obtener informacion detallada de un temporizador"""
        timer = self.get_timer(name)
        return timer.get_info() if timer else None
    
    def get_priority_distribution(self):
        """Obtener distribucion de temporizadores por prioridad"""
        distribution = {priority.name: 0 for priority in TimerPriority}
        for timer in self.timers.values():
            distribution[timer.priority.name] += 1
        return distribution
    
    def get_tag_distribution(self):
        """Obtener distribucion de temporizadores por etiquetas"""
        tag_count = {}
        for timer in self.timers.values():
            for tag in timer.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        return tag_count
    
    def get_performance_report(self):
        """Obtener reporte de rendimiento detallado"""
        stats = self.performance_stats.copy()
        
        # Calcular FPS estimado
        if stats['avg_update_time'] > 0:
            estimated_fps = 1.0 / stats['avg_update_time']
        else:
            estimated_fps = float('inf')
        
        # Evaluar salud del sistema
        health_status = "healthy"
        warnings = []
        
        if stats['avg_update_time'] > 0.016:  # >16ms = <60fps
            health_status = "warning"
            warnings.append("Rendimiento por debajo de 60fps")
        
        if stats['max_update_time'] > 0.033:  # >33ms = <30fps
            warnings.append("Picos de latencia detectados")
        
        if len(self.timers) > self.max_timers * 0.8:
            warnings.append("Acercandose al limite de temporizadores")
        
        return {
            'performance_stats': stats,
            'estimated_fps': estimated_fps,
            'health_status': health_status,
            'warnings': warnings,
            'timer_load': len(self.timers) / self.max_timers
        }
    
    def create_animation_sequence(self, sequence_name, animations):
        """Crear secuencia de animaciones encadenadas"""
        """
        animations: lista de diccionarios con:
        {
            'delay': tiempo antes de ejecutar (desde el inicio de la secuencia),
            'duration': duracion de la animacion,
            'start_value': valor inicial,
            'end_value': valor final,
            'callback': funcion de interpolacion,
            'completion': funcion al completar (opcional),
            'easing': funcion de easing (opcional)
        }
        """
        for i, anim in enumerate(animations):
            timer_name = f"{sequence_name}_step_{i}"
            
            # Programar inicio de la animacion
            def start_animation(animation=anim, name=timer_name):
                self.add_interpolation_timer(
                    name, 
                    animation['duration'],
                    animation['start_value'],
                    animation['end_value'],
                    animation['callback'],
                    animation.get('completion'),
                    TimerPriority.NORMAL,
                    animation.get('easing')
                )
            
            # Programar el inicio con el delay especificado
            self.schedule_event(
                anim['delay'], 
                start_animation, 
                f"{sequence_name}_trigger_{i}"
            )
    
    def create_staggered_animation(self, base_name, elements, animation_func, stagger_delay=0.1):
        """Crear animacion escalonada para multiples elementos"""
        """
        elements: lista de elementos a animar
        animation_func: funcion que recibe (element, index, timer_system) y crea la animacion
        stagger_delay: retraso entre cada elemento
        """
        for i, element in enumerate(elements):
            delay = i * stagger_delay
            
            def create_delayed_animation(elem=element, idx=i):
                animation_func(elem, idx, self)
            
            self.schedule_event(
                delay, 
                create_delayed_animation, 
                f"{base_name}_stagger_{i}"
            )
    
    def debug_dump(self):
        """Volcar informacion de debug del sistema"""
        print("=== UI Timer System Debug Dump ===")
        print(f"Total timers: {len(self.timers)}")
        print(f"Scheduled events: {len(self.scheduled_events)}")
        print(f"System paused: {self.paused}")
        
        if self.timers:
            print("\nActive Timers:")
            for name, timer in self.timers.items():
                status = "PAUSED" if timer.paused else "ACTIVE" if timer.active else "INACTIVE"
                print(f"  {name}: {status}, Progress: {timer.get_progress():.2%}, "
                      f"Priority: {timer.priority.name}, Tags: {list(timer.tags)}")
        
        if self.scheduled_events:
            print("\nScheduled Events:")
            for event in self.scheduled_events:
                delay = event.get_delay_until_trigger()
                print(f"  {event.name}: {delay:.2f}s remaining, Priority: {event.priority.name}")
        
        performance = self.get_performance_report()
        print(f"\nPerformance:")
        print(f"  Avg update time: {performance['performance_stats']['avg_update_time']:.4f}s")
        print(f"  Max update time: {performance['performance_stats']['max_update_time']:.4f}s")
        print(f"  Estimated FPS: {performance['estimated_fps']:.1f}")
        print(f"  Health: {performance['health_status']}")
        if performance['warnings']:
            print(f"  Warnings: {', '.join(performance['warnings'])}")
        
        print("=== End Debug Dump ===\n")