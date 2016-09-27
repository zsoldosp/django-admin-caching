try:
    from mock import patch, Mock  # noqa: F401
except ImportError:
    from unittest.mock import patch, Mock  # noqa: F401
