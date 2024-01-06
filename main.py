import dash
import layout
import callbacks

app = dash.Dash(__name__)

app.layout = layout.create_layout()

app.title = 'SpectroVolt'

callbacks.register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
