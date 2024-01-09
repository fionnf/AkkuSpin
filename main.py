import dash
import layout
import callbacks
import socket

app = dash.Dash(__name__)

app.layout = layout.create_layout()

app.title = 'AkkuSpin'

callbacks.register_callbacks(app)

# Get the machine's local IP address
local_ip = socket.gethostbyname(socket.gethostname())

print(f'Server starting, Local address: http://127.0.0.1:8080/')
print(f'Network address (accessible within your LAN): http://{local_ip}:8080')

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
