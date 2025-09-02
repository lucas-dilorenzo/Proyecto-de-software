import operaciones

def calcular(operacion, a, b):
    if operacion == 'suma':
        return operaciones.suma(a, b)
    elif operacion == 'resta':
        return operaciones.resta(a, b)
    elif operacion == 'multiplicacion':
        return operaciones.multiplicacion(a, b)
    elif operacion == 'division':
        return operaciones.division(a, b)
    else:
        return ("operación no válida")