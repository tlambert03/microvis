from microvis.backend.vispy._constants import VISPY_BACKEND_NAME


class VispyBackend:
    """Mixin so that all objects contain a reference to their backend."""
    _backend_name: str = VISPY_BACKEND_NAME