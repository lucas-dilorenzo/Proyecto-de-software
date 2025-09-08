from src import calculadora

if __name__ == "__main__":
    numero = float(input("Ingrese un numero: "))
    otro_numero = float(input("Ingrese otro numero: "))
    operacion = input("Ingrese una operacion (+ , - , * , /): ")
    resultado = calculadora.calcular(operacion, numero, otro_numero)
    print(resultado) 