from abc import ABC, abstractmethod

class Metric(ABC):
    
    @abstractmethod
    def evaluate(self, dataset):
        pass    
    
    @abstractmethod
    def to_dict(self):
        return {
            "name": self.name,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value
        }