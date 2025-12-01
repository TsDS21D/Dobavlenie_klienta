import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order
from django.utils import timezone


class OrderConsumer(AsyncWebsocketConsumer):
    """WebSocket обработчик для системы заказов"""
    
    async def connect(self):
        """Метод connect() вызывается когда браузер подключается к WebSocket"""
        self.room_group_name = 'orders'
        
        # Добавляем это соединение в группу
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Принимаем WebSocket соединение
        await self.accept()
        
        # Получаем все заказы и отправляем браузеру при подключении
        orders = await self.get_all_orders()
        
        await self.send(text_data=json.dumps({
            'type': 'initial_load',
            'orders': orders
        }))
    
    async def disconnect(self, close_code):
        """Метод disconnect() вызывается когда браузер отключается от WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Метод receive() вызывается когда браузер отправляет сообщение на сервер"""
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'add_order':
            # Браузер отправил новый заказ
            customer_name = data.get('customer_name')
            description = data.get('description')
            ready_datetime_str = data.get('ready_datetime')
            
            # Добавляем новый заказ в БД (номер генерируется автоматически)
            await self.add_order(customer_name, description, ready_datetime_str)
            
            # Получаем обновленный список всех заказов
            orders = await self.get_all_orders()
            
            # Отправляем обновленный список ВСЕМ клиентам в группе
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'order_update',
                    'orders': orders
                }
            )
        
        elif action == 'delete_order':
            # Браузер хочет удалить заказ
            order_number = data.get('order_number')
            await self.delete_order(order_number)
            
            # Получаем обновленный список всех заказов
            orders = await self.get_all_orders()
            
            # Отправляем обновленный список ВСЕМ клиентам в группе
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'order_update',
                    'orders': orders
                }
            )
        
        elif action == 'update_order':
            # Браузер хочет обновить заказ
            order_number = data.get('order_number')
            customer_name = data.get('customer_name')
            description = data.get('description')
            ready_datetime_str = data.get('ready_datetime')
            
            await self.update_order(order_number, customer_name, description, ready_datetime_str)
            
            # Получаем обновленный список всех заказов
            orders = await self.get_all_orders()
            
            # Отправляем обновленный список ВСЕМ клиентам в группе
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'order_update',
                    'orders': orders
                }
            )
        
        elif action == 'refresh_orders':
            # Браузер просит обновить список заказов (для пересчета рабочих часов)
            orders = await self.get_all_orders()
            
            await self.send(text_data=json.dumps({
                'type': 'order_update',
                'orders': orders
            }))
    
    async def order_update(self, event):
        """Метод order_update() вызывается когда группа отправляет сообщение"""
        orders = event['orders']
        
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'orders': orders
        }))
    
    @database_sync_to_async
    def add_order(self, customer_name, description, ready_datetime_str):
        """Добавляет новый заказ в БД"""
        # Парсим дату-время из строки (формат: YYYY-MM-DDTHH:MM)
        # datetime.fromisoformat создает naive datetime, нужно сделать его aware
        ready_dt_naive = timezone.datetime.fromisoformat(ready_datetime_str)
        
        # Если naive - сделать aware в текущей timezone
        if ready_dt_naive.tzinfo is None:
            ready_dt = timezone.make_aware(ready_dt_naive)
        else:
            ready_dt = ready_dt_naive
        
        order = Order.objects.create(
            customer_name=customer_name,
            description=description,
            ready_datetime=ready_dt
        )
        return order
    
    @database_sync_to_async
    def update_order(self, order_number, customer_name, description, ready_datetime_str):
        """Обновляет существующий заказ"""
        try:
            order = Order.objects.get(order_number=order_number)
            order.customer_name = customer_name
            order.description = description
            
            # Парсим дату-время
            ready_dt_naive = timezone.datetime.fromisoformat(ready_datetime_str)
            if ready_dt_naive.tzinfo is None:
                ready_dt = timezone.make_aware(ready_dt_naive)
            else:
                ready_dt = ready_dt_naive
            
            order.ready_datetime = ready_dt
            order.save()
        except Order.DoesNotExist:
            pass
    
    @database_sync_to_async
    def delete_order(self, order_number):
        """Удаляет заказ из БД"""
        try:
            order = Order.objects.get(order_number=order_number)
            order.delete()
        except Order.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_all_orders(self):
        """Получает все заказы из БД и преобразует в список словарей"""
        orders = Order.objects.all()
        return [order.to_dict() for order in orders]
