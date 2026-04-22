import json
from django.core.management.base import BaseCommand
from core.pubsub import Subscriber, ALL_CHANNELS


class Command(BaseCommand):
    help = 'Escucha eventos Redis Pub/Sub en todos los canales de Mi Mercado Global.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channels',
            nargs='+',
            default=ALL_CHANNELS,
            help='Canales a escuchar (por defecto: todos).',
        )

    def handle(self, *args, **options):
        channels = options['channels']
        subscriber = Subscriber(channels)

        self.stdout.write(self.style.SUCCESS(
            f'Escuchando {len(channels)} canal(es): {", ".join(channels)}'
        ))
        self.stdout.write('Presiona Ctrl+C para detener.\n')

        def handler(channel: str, data: dict):
            self.stdout.write(
                self.style.HTTP_INFO(f'\n[{channel}]') +
                f' {json.dumps(data, indent=2, ensure_ascii=False)}'
            )

        try:
            subscriber.listen(handler)
        except KeyboardInterrupt:
            subscriber.stop()
            self.stdout.write(self.style.WARNING('\nSuscriptor detenido.'))
