from django.db import models

# ===== МОДЕЛЬ ЗАКАЗА =====
class Order(models.Model):
    """
    Модель для хранения информации о заказах.
    Каждый заказ имеет:
    - customer_name: имя клиента
    - order_number: номер заказа
    - description: описание заказа
    - created_at: когда был создан заказ
    """
    
    # CharField = поле для текста (максимум 100 символов)
    customer_name = models.CharField(max_length=100)
    
    # CharField для номера заказа с уникальностью
    order_number = models.CharField(max_length=50, unique=True)
    
    # TextField = большое поле для длинного текста (без ограничений)
    description = models.TextField()
    
    # DateTimeField с auto_now_add=True автоматически сохраняет время создания
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # ordering = ['-created_at'] означает: сортировать по дате СВЕРХУ ВНИЗ
        # Минус (-) означает обратный порядок (новые заказы первыми)
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        # Этот метод определяет как заказ выглядит в админке
        return f"#{self.order_number} - {self.customer_name}"
    
    @classmethod
    def get_all_orders(cls):
        """Получить все заказы из БД"""
        return list(cls.objects.all())
    
    def to_dict(self):
        """Преобразовать заказ в словарь для JSON"""
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'order_number': self.order_number,
            'description': self.description,
            'created_at': self.created_at.strftime('%d.%m.%Y %H:%M:%S'),
        }