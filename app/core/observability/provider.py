from abc import ABC, abstractmethod

class ObservabilityProvider(ABC):
    @abstractmethod
    def setup(self, app):
        """Configura a stack de observabilidade da aplicação."""
        pass

    @abstractmethod
    def instrument_tool(self, func):
        """Decorator para instrumentar a execução de uma tool/função."""
        pass

    @abstractmethod
    def set_span_attribute(self, key: str, value):
        """Adiciona um atributo ao trace/span atual."""
        pass
