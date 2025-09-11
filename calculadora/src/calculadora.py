from src import operaciones

def calcular(operacion, a, b):
    if operacion == '+':
        return operaciones.suma(a, b)
    elif operacion == '-':
        return operaciones.resta(a, b)
    elif operacion == '*':
        return operaciones.multiplicacion(a, b)
    elif operacion == '/':
        return operaciones.division(a, b)
    else:
        return ("operación no válida")