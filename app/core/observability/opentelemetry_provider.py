import os
import logging
import functools
import inspect
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from .provider import ObservabilityProvider

class OpenTelemetryProvider(ObservabilityProvider):
    def setup(self, app):
        """
        Configura toda a stack de telemetria da aplicação:
        1. Prometheus FastAPI Instrumentator (Métricas)
        2. OpenTelemetry TracerProvider e Exportador gRPC OTLP (Tempo - Traces)
        3. Loki Logging Handler (Loki - Logs)
        """

        # 1. Inicializa o exportador de métricas do Prometheus
        Instrumentator().instrument(app).expose(app)

        # 2. Configura o OpenTelemetry Tracer Provider
        otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otel_endpoint:
            resource = Resource.create(attributes={
                "service.name": os.getenv("OTEL_SERVICE_NAME", "ticket-triage-service")
            })
            provider = TracerProvider(resource=resource)
            
            # O exporter OTLP aponta para o collector/Tempo. 
            # gRPC endpoint padrão do tempo no compose: http://tempo:4317
            otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)
            trace.set_tracer_provider(provider)
            
            # Instrumenta o FastAPI para capturar as rotas automaticamente
            FastAPIInstrumentor.instrument_app(app)
            
            # 3. Configura exportação de logs para o Grafana Loki de forma assíncrona
            try:
                import logging_loki
                import queue
                from logging.handlers import QueueHandler, QueueListener
                
                loki_handler = logging_loki.LokiHandler(
                    url="http://localhost:3100/loki/api/v1/push",
                    tags={"application": "ticket-triage-service"},
                    version="1",
                )
                
                # Fila sem limite de tamanho (ou use maxsize se preferir)
                log_queue = queue.Queue()
                queue_handler = QueueHandler(log_queue)
                
                # O QueueListener roda em uma thread separada, processando a fila e 
                # enviando para o LokiHandler real sem bloquear a thread principal (API)
                listener = QueueListener(log_queue, loki_handler, respect_handler_level=True)
                listener.start()
                
                # Define o level do root logger para INFO e adiciona o QueueHandler
                logging.getLogger().setLevel(logging.INFO)
                logging.getLogger().addHandler(queue_handler)
            except ImportError:
                pass

    def instrument_tool(self, func):
        """
        Decorator to automatically wrap an async function in an OpenTelemetry span,
        injecting its arguments as span attributes.
        """
        tracer = trace.get_tracer("agent_tools")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"tool_{func.__name__}") as span:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for key, value in bound_args.arguments.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"tool.{key}", value)
                    else:
                        span.set_attribute(f"tool.{key}", str(value))
                        
                return await func(*args, **kwargs)
                
        return async_wrapper

    def set_span_attribute(self, key: str, value):
        """
        Abstrai a adição de atributos ao span atual para que a camada de domínio
        ou ferramentas não precisem importar bibliotecas de telemetria (OpenTelemetry).
        """
        span = trace.get_current_span()
        if span and span.is_recording():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(key, value)
            else:
                span.set_attribute(key, str(value))
