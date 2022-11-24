import sys
import importlib
import logging
from .core.config import Config

logger = logging.getLogger("six")
config = Config()


def load_plugin(plugin_dir, plugin_name):
    """
    按路径加载第三方模块
    """
    sys.path.append(plugin_dir)
    config._push(plugin_name)
    importlib.import_module(plugin_name)
    config._pop()
    sys.path.remove(plugin_dir)

    logger.info(f"@start-up Plugin [{plugin_name}] load successfully.")
