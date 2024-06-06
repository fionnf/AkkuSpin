import dash
import layout
import callbacks
import socket

app = dash.Dash(__name__)

app.layout = layout.create_layout()

app.title = 'AkkuSpin'

callbacks.register_callbacks(app)
callbacks.register_integration_callback(app)

local_ip = socket.gethostbyname(socket.gethostname())
ascii_art = r"""
           _  ___  ___    _  _____ _____ _____ _   _ 
     /\   | |/ / |/ / |  | |/ ____|  __ \_   _| \ | |
    /  \  | ' /| ' /| |  | | (___ | |__) || | |  \| |
   / /\ \ |  < |  < | |  | |\___ \|  ___/ | | | . ` |
  / ____ \| . \| . \| |__| |____) | |    _| |_| |\  |
 /_/    \_\_|\_\_|\_\____/ |_____/|_|   |_____|_| \_|
"""

print("")
print(ascii_art)
print("")
print("Akkuspin has been developed by the Otten Group of the University of Groningen. ")
print("Major Contributors: Fionn Ferreira, Edwin Otten")
print("")
print(r"""Akkuspin is distributed under the MIT License. This permissive license allows users to freely use,
modify, and distribute the software. For more detailed information, refer to the LICENSE file included in
the project repository. If you use Akkuspin for generating plots, please acknowledge the software in
the captions of your figures. This can be done by including a statement such as "Plot generated using
Akkuspin software." Acknowledging the software helps support its development and allows others to
recognize the tools used in your research.""")
print("")
print("""Contributions to Akkuspin are welcome. If you wish to contribute, please fork the repository on GitHub,
make your changes, and submit a pull request. Ensure your code adheres to the project’s coding
standards and includes appropriate tests""")
print("")
print(f'Local address: http://127.0.0.1:8080/')
print(f'Network address (accessible within your LAN): http://{local_ip}:8080')

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)


