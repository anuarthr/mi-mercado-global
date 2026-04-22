import json
import threading
from config import redis_client

# ── Canales ──────────────────────────────────────────────────────────────────
CHANNEL_PEDIDO_CREADO = 'pedidos.creado'
CHANNEL_PEDIDO_ESTADO = 'pedidos.estado'
CHANNEL_ITEM_AGREGADO = 'items.agregado'

ALL_CHANNELS = [CHANNEL_PEDIDO_CREADO, CHANNEL_PEDIDO_ESTADO, CHANNEL_ITEM_AGREGADO]


# ── Publisher ─────────────────────────────────────────────────────────────────
def publish(channel: str, message: dict) -> int:
    """Publica un evento JSON en el canal indicado.
    Retorna el número de suscriptores que recibieron el mensaje."""
    return redis_client.publish(channel, json.dumps(message))


# ── Subscriber ────────────────────────────────────────────────────────────────
class Subscriber:
    """Suscriptor Redis Pub/Sub.

    Uso básico (bloqueante):
        sub = Subscriber(['pedidos.creado'])
        sub.listen(lambda channel, data: print(channel, data))

    Uso en hilo daemon (no bloqueante):
        sub = Subscriber(['pedidos.creado'])
        sub.listen_in_background(lambda channel, data: print(channel, data))
    """

    def __init__(self, channels: list[str]):
        self._pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        self._pubsub.subscribe(*channels)
        self._channels = channels

    def listen(self, handler):
        """Bucle bloqueante. Llama a handler(channel, data) por cada mensaje."""
        for message in self._pubsub.listen():
            if message and message.get('type') == 'message':
                channel = message['channel']
                if isinstance(channel, bytes):
                    channel = channel.decode()
                data = json.loads(message['data'])
                handler(channel, data)

    def listen_in_background(self, handler) -> threading.Thread:
        """Lanza el bucle en un hilo daemon y lo retorna."""
        thread = threading.Thread(target=self.listen, args=(handler,), daemon=True)
        thread.start()
        return thread

    def stop(self):
        self._pubsub.unsubscribe()
        self._pubsub.close()
