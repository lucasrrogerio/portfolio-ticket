import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

def setup_observability(app):
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
        
        # 3. Configura exportação de logs para o Grafana Loki
        try:
            import logging_loki
            loki_handler = logging_loki.LokiHandler(
                url="http://localhost:3100/loki/api/v1/push",
                tags={"application": "ticket-triage-service"},
                version="1",
            )
            # Define o level do root logger para INFO e adiciona o handler
            logging.getLogger().setLevel(logging.INFO)
            logging.getLogger().addHandler(loki_handler)
        except ImportError:
            pass
