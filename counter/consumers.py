import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Order


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
            order_number = data.get('order_number')
            description = data.get('description')
            
            # Добавляем новый заказ в БД
            await self.add_order(customer_name, order_number, description)
            
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
    
    async def order_update(self, event):
        """Метод order_update() вызывается когда группа отправляет сообщение"""
        orders = event['orders']
        
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'orders': orders
        }))
    
    @database_sync_to_async
    def add_order(self, customer_name, order_number, description):
        """Добавляет новый заказ в БД"""
        order = Order.objects.create(
            customer_name=customer_name,
            order_number=order_number,
            description=description
        )
        return order
    
    @database_sync_to_async
    def get_all_orders(self):
        """Получает все заказы из БД и преобразует в список словарей"""
        orders = Order.objects.all()
        return [order.to_dict() for order in orders]
