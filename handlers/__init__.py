from .base import register_base_handlers
from .add_skin import register_add_skin_handlers
from .delete_skin import register_delete_skin_handlers
from .monitoring import register_monitoring_handlers
from .cookies import register_cookies_handlers
from .check_skins import register_check_skins_handlers

__all__ = [
    "register_all_handlers",
]

def register_all_handlers(dp):
    register_base_handlers(dp)
    register_add_skin_handlers(dp)
    register_delete_skin_handlers(dp)
    register_monitoring_handlers(dp)
    register_cookies_handlers(dp)
    register_check_skins_handlers(dp)