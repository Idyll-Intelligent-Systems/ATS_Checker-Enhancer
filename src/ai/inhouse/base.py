"""In-house lightweight model framework.
Defines abstract base classes and registry for internal extensible models.
Enterprise-grade design: clear contracts, versioning, metadata, health checks.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable, Callable
import time

@runtime_checkable
class SupportsPredict(Protocol):
    def predict(self, input_data: Any) -> Any: ...

@dataclass
class ModelMetadata:
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = "inhouse"
    created: float = field(default_factory=lambda: time.time())
    extra: Dict[str, Any] = field(default_factory=dict)

class BaseModel(SupportsPredict):
    """Base class for all internal models.
    Subclasses should override _predict to implement logic.
    """
    def __init__(self, metadata: ModelMetadata):
        self.metadata = metadata
        self._loaded = False

    def load(self):  # lightweight hook
        self._loaded = True
        return self

    def is_loaded(self) -> bool:
        return self._loaded

    def health(self) -> Dict[str, Any]:
        return {"name": self.metadata.name, "version": self.metadata.version, "loaded": self._loaded}

    def predict(self, input_data: Any) -> Any:
        if not self._loaded:
            self.load()
        return self._predict(input_data)

    def _predict(self, input_data: Any) -> Any:  # pragma: no cover
        raise NotImplementedError

# Registry -----------------------------------------------------------------
class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._constructors: Dict[str, Callable[[], BaseModel]] = {}

    def register(self, key: str, constructor: Callable[[], BaseModel]):
        if key in self._constructors:
            raise ValueError(f"Model key already registered: {key}")
        self._constructors[key] = constructor

    def get(self, key: str) -> BaseModel:
        if key not in self._models:
            if key not in self._constructors:
                raise KeyError(f"Unknown model key: {key}")
            self._models[key] = self._constructors[key]()
        return self._models[key]

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.metadata.__dict__ for k,v in self._models.items()}

registry = ModelRegistry()
