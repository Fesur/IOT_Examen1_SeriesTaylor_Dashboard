import socket
import json
import sys

class Client:
    def __init__(self, server_host='localhost', server_port=5555):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.user_id = None
        self.username = None
        
    def connect(self):
        """Establece conexión con el servidor."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            print(f"Conectado al servidor {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            return False
    
    def register(self, username):
        """Registra un usuario en el servidor."""
        if not self.sock:
            if not self.connect():
                return False
        
        message = {
            'action': 'register',
            'username': username
        }
        
        try:
            self.sock.send(json.dumps(message).encode('utf-8'))
            response = json.loads(self.sock.recv(4096).decode('utf-8'))
            
            if response['status'] == 'success':
                self.user_id = response['user_id']
                self.username = username
                print(f"Usuario registrado con ID: {self.user_id}")
                return True
            else:
                print(f"Error al registrar usuario: {response.get('message')}")
                return False
        except Exception as e:
            print(f"Error en la comunicación: {e}")
            return False
    
    def calculate_series(self, series_type, x_value, n_terms):
        """Solicita al servidor el cálculo de una serie."""
        if not self.user_id:
            print("Debe registrarse primero.")
            return None
        
        message = {
            'action': 'calculate',
            'user_id': self.user_id,
            'series_type': series_type,
            'x_value': x_value,
            'n_terms': n_terms
        }
        
        try:
            self.sock.send(json.dumps(message).encode('utf-8'))
            response = json.loads(self.sock.recv(4096).decode('utf-8'))
            
            if response['status'] == 'success':
                return response
            else:
                print(f"Error al calcular serie: {response.get('message')}")
                return None
        except Exception as e:
            print(f"Error en la comunicación: {e}")
            return None
    
    def get_user_calculations(self):
        """Obtiene los cálculos realizados por el usuario."""
        if not self.user_id:
            print("Debe registrarse primero.")
            return None
        
        message = {
            'action': 'get_user_calculations',
            'user_id': self.user_id
        }
        
        try:
            self.sock.send(json.dumps(message).encode('utf-8'))
            response = json.loads(self.sock.recv(4096).decode('utf-8'))
            
            if response['status'] == 'success':
                return response['calculations']
            else:
                print(f"Error al obtener cálculos: {response.get('message')}")
                return None
        except Exception as e:
            print(f"Error en la comunicación: {e}")
            return None
    
    def close(self):
        """Cierra la conexión con el servidor."""
        if self.sock:
            self.sock.close()
            print("Conexión cerrada")

def main():
    client = Client()
    
    if not client.connect():
        sys.exit(1)
    
    # Solicitar nombre de usuario
    username = input("Ingrese su nombre de usuario: ")
    if not client.register(username):
        client.close()
        sys.exit(1)
    
    while True:
        print("\n--- Menú ---")
        print("1. Calcular serie trigonométrica")
        print("2. Ver mis cálculos anteriores")
        print("3. Salir")
        
        option = input("Seleccione una opción: ")
        
        if option == '1':
            print("\nTipos de series disponibles:")
            print("1. Seno (sin)")
            print("2. Coseno (cos)")
            print("3. Tangente (tan)")
            
            series_option = input("Seleccione el tipo de serie: ")
            
            series_types = {
                '1': 'sin',
                '2': 'cos',
                '3': 'tan'
            }
            
            if series_option not in series_types:
                print("Opción no válida")
                continue
            
            series_type = series_types[series_option]
            
            try:
                x_value = float(input("Ingrese el valor de x (en radianes): "))
                n_terms = int(input("Ingrese el número de términos para la aproximación: "))
                
                if n_terms <= 0:
                    print("El número de términos debe ser positivo")
                    continue
                
                result = client.calculate_series(series_type, x_value, n_terms)
                
                if result:
                    print("\n--- Resultado ---")
                    print(f"Valor aproximado de {series_type}({x_value}): {result['result']}")
                    print(f"Valor exacto: {result['exact_value']}")
                    print(f"Error de aproximación: {result['error']}")
            
            except ValueError:
                print("Error: Ingrese números válidos")
        
        elif option == '2':
            calculations = client.get_user_calculations()
            
            if calculations:
                print("\n--- Mis Cálculos ---")
                for i, calc in enumerate(calculations, 1):
                    series_type, x, n, result, exact, error, time = calc
                    print(f"{i}. {series_type}({x}) con {n} términos = {result} (Error: {error})")
            else:
                print("No se encontraron cálculos o hubo un error")
        
        elif option == '3':
            client.close()
            break
        
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()
