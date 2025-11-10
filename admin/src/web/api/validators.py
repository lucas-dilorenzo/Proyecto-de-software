from functools import wraps
from flask import request
from .exceptions import ValidationError


def validate_params(schema):
    """
    Decorador para validar parámetros de query string
    
    Ejemplo:
        @validate_params({
            'lat': {'type': float, 'min': -90, 'max': 90},
            'per_page': {'type': int, 'min': 1, 'max': 100},
        })
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            errors = {}
            
            for param, rules in schema.items():
                value = request.args.get(param)
                
                # Si es opcional y no está presente, continuar
                if value is None:
                    if rules.get('required', False):
                        errors[param] = ["This field is required"]
                    continue
                
                # Validar tipo
                param_type = rules.get('type', str)
                try:
                    if param_type == int:
                        value = int(value)
                    elif param_type == float:
                        value = float(value)
                    elif param_type == bool:
                        value = value.lower() in ('true', '1', 'yes')
                except (ValueError, AttributeError):
                    errors[param] = [f"Must be a valid {param_type.__name__}"]
                    continue
                
                # Validar min/max
                if 'min' in rules and value < rules['min']:
                    errors[param] = [f"Must be at least {rules['min']}"]
                if 'max' in rules and value > rules['max']:
                    errors[param] = [f"Must be at most {rules['max']}"]
                
                # Validar opciones
                if 'choices' in rules and value not in rules['choices']:
                    errors[param] = [f"Must be one of: {', '.join(map(str, rules['choices']))}"]
                
                # Validaciones custom
                if 'validate' in rules:
                    custom_error = rules['validate'](value)
                    if custom_error:
                        errors[param] = [custom_error]
            
            if errors:
                raise ValidationError(details=errors)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_latitude(value):
    try:
        lat = float(value)
        if -90 <= lat <= 90:
            return None
        return "Must be a valid latitude"
    except (ValueError, TypeError):
        return "Must be a valid latitude"


def validate_longitude(value):
    try:
        lng = float(value)
        if -180 <= lng <= 180:
            return None
        return "Must be a valid longitude"
    except (ValueError, TypeError):
        return "Must be a valid longitude"