#app.models.__init__.py
import importlib
import pkgutil

# Automatically import all modules in this package
package_name = __name__

for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if module_name not in ["__init__", "base_entity"]:  # exclude helpers
        importlib.import_module(f"{package_name}.{module_name}")
