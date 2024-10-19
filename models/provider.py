from abc import ABC, abstractmethod

class Provider(ABC):
    @abstractmethod
    def generate(self, model, messages):
        pass
