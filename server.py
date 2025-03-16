import socket
import threading
import json
import time
from database import Database  # Corregido: importación directa
from series_calculator import SeriesCalculator

class Server:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.db = Database()
        
    def start(self):
        """Inicia el servidor y espera por conexiones."""
        self.sock.listen(5)
        print(f"Servidor iniciado en {self.host}:{self.port}")
        
        while True:
            try:
                client, address = self.sock.accept()
                print(f"Conexión establecida con {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client,))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"Error en la conexión: {e}")
                break
        
        self.shutdown()
    
    def handle_client(self, client_socket):
        """Maneja la comunicación con un cliente."""
        user_id = None
        
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    action = message.get('action')
                    
                    if action == 'register':
                        username = message.get('username')
                        user_id = self.db.add_user(username)
                        response = {'status': 'success', 'user_id': user_id}
                    
                    elif action == 'calculate':
                        user_id = message.get('user_id')
                        series_type = message.get('series_type')
                        x_value = message.get('x_value')
                        n_terms = message.get('n_terms')
                        
                        result, exact_value, error = SeriesCalculator.calculate_series(
                            series_type, x_value, n_terms)
                        
                        calc_id = self.db.save_calculation(
                            user_id, series_type, x_value, n_terms, result, exact_value, error)
                        
                        response = {
                            'status': 'success',
                            'calculation_id': calc_id,
                            'result': result,
                            'exact_value': exact_value,
                            'error': error
                        }
                    
                    elif action == 'get_user_calculations':
                        user_id = message.get('user_id')
                        calculations = self.db.get_user_calculations(user_id)
                        response = {
                            'status': 'success',
                            'calculations': calculations
                        }
                    
                    else:
                        response = {'status': 'error', 'message': 'Acción desconocida'}
                
                except Exception as e:
                    response = {'status': 'error', 'message': str(e)}
                
                client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            print(f"Error al manejar cliente: {e}")
        
        finally:
            client_socket.close()
    
    def shutdown(self):
        """Cierra el servidor y libera recursos."""
        print("Cerrando el servidor...")
        self.db.close()
        self.sock.close()

if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")
        server.shutdown()
