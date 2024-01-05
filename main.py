import dash
import layout
import callbacks
import utils

# Initialize the Dash application
app = dash.Dash(__name__)

# Configure the layout of the application using the function from layout.py
app.layout = layout.create_layout()

# Register callbacks using the function from callbacks.py
callbacks.register_callbacks(app)

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
