import importlib
from .provider import Provider


class Client:
    def __init__(self, provider_name, config = {}):
        provider_module = f"models.providers.{provider_name}"
        module = importlib.import_module(provider_module, package="models")
        provider_class = getattr(module, "ProviderImplementation")

        if not issubclass(provider_class, Provider):
            raise TypeError(
                f"{provider_class.__name__} does not use the Provider interface."
            )

        self.provider = provider_class(config)

    def generate(self, model, messages, response_model):
        return self.provider.generate(model, messages, response_model)
