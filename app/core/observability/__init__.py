import os
from .opentelemetry_provider import OpenTelemetryProvider

def _get_provider():
    provider_name = os.getenv("OBSERVABILITY_PROVIDER", "opentelemetry").lower()
    
    if provider_name == "opentelemetry":
        return OpenTelemetryProvider()
    
    # Aqui você pode plugar outros providers no futuro:
    # elif provider_name == "new_relic":
    #     from .new_relic_provider import NewRelicProvider
    #     return NewRelicProvider()
    
    # Fallback default
    return OpenTelemetryProvider()

_active_provider = _get_provider()

def setup_observability(app):
    """Delega a inicialização da telemetria para o provedor ativo."""
    return _active_provider.setup(app)

def instrument_tool(func):
    """Delega o decorator de instrumentação para o provedor ativo."""
    return _active_provider.instrument_tool(func)

def set_span_attribute(key: str, value):
    """Delega a adição de atributos no span para o provedor ativo."""
    return _active_provider.set_span_attribute(key, value)
