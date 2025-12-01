from django.db import models
from django.utils import timezone
from datetime import timedelta


class Order(models.Model):
    """Модель для хранения информации о заказах"""
    
    # Автоинкрементное поле для номера заказа
    order_number = models.AutoField(primary_key=True, db_column='order_number')
    
    # Имя клиента
    customer_name = models.CharField(max_length=100)
    
    # Описание заказа
    description = models.TextField()
    
    # Дата и время готовности заказа
    ready_datetime = models.DateTimeField(help_text="Когда должен быть готов заказ")
    
    # Время создания заказа
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f"#{self.order_number:04d} - {self.customer_name}"
    
    def get_working_hours_remaining(self):
        """
        Рассчитывает количество рабочих часов до готовности заказа.
        Рабочее время: пн-пт с 10:00 до 18:00
        """
        now = timezone.now()
        ready_dt = self.ready_datetime
        
        # Если время уже прошло
        if now >= ready_dt:
            return 0
        
        total_hours = 0
        current = now
        
        # Проходим по всем часам до времени готовности
        while current < ready_dt:
            # Проверяем день недели (0=пн, 6=вс)
            day_of_week = current.weekday()
            hour = current.hour
            
            # Если рабочий день (пн-пт) и рабочее время (10-18)
            if day_of_week < 5 and 10 <= hour < 18:
                total_hours += 1
            
            # Переходим на следующий час
            current += timedelta(hours=1)
        
        return total_hours
    
    def to_dict(self):
        """Преобразовать заказ в словарь для JSON"""
        return {
            'order_number': f'{self.order_number:04d}',
            'customer_name': self.customer_name,
            'description': self.description,
            'ready_datetime': self.ready_datetime.strftime('%d.%m.%Y %H:%M'),
            'working_hours_remaining': self.get_working_hours_remaining(),
            'created_at': self.created_at.strftime('%d.%m.%Y %H:%M:%S'),
        }
