from app import create_app
import os

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port) 