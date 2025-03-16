import argparse
import threading
import os
import sys
from multiprocessing import Process

def run_calculation_server():
    from server import Server
    print("Iniciando servidor de cálculos...")
    server = Server(host='0.0.0.0', port=5555)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Servidor de cálculos detenido por el usuario")
        server.shutdown()

def run_dashboard():
    from dashboard import app
    print("Iniciando dashboard web...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Servidor de Series Trigonométricas')
    parser.add_argument('--mode', type=str, default='all', choices=['all', 'calc', 'dash'],
                      help='Modo de ejecución: all=ambos servidores, calc=solo servidor de cálculos, dash=solo dashboard')
    
    args = parser.parse_args()
    
    if args.mode == 'all':
        # Iniciar ambos servidores en procesos separados
        calc_process = Process(target=run_calculation_server)
        dash_process = Process(target=run_dashboard)
        
        calc_process.start()
        dash_process.start()
        
        try:
            calc_process.join()
            dash_process.join()
        except KeyboardInterrupt:
            print("Deteniendo servidores...")
            calc_process.terminate()
            dash_process.terminate()
            calc_process.join()
            dash_process.join()
    
    elif args.mode == 'calc':
        # Solo iniciar servidor de cálculos
        run_calculation_server()
    
    elif args.mode == 'dash':
        # Solo iniciar dashboard
        run_dashboard()

if __name__ == "__main__":
    main()
