#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Add the project root directory to the Python path
    # This assumes that the manage.py file is in the project root
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hwrkannada.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# #!/usr/bin/env python
# import os
# import sys

# if __name__ == "__main__":
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hwrkannada.settings")
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)
