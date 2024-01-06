import dash
import layout
import callbacks

app = dash.Dash(__name__)

app.layout = layout.create_layout()

app.title = 'SpectroVolt'

callbacks.register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1', port=8080)
