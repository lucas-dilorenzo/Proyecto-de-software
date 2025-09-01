def suma(a, b):
    return a + b
def calcular(operacion, a, b):
    if operacion == 'suma':
        return suma(a, b)
    else:
        raise ValueError("Operación no soportada")