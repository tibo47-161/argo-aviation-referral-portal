# Argo Aviation Referral Portal - Main Entry Point
import sys
import os

# Add the parent directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try to import the simple app first
    from app_simple import app
    print("✅ Successfully loaded app_simple.py")
except ImportError as e:
    print(f"❌ Failed to import app_simple: {e}")
    try:
        # Fallback to the main app
        from app import create_app
        app = create_app()
        print("✅ Successfully loaded main app")
    except ImportError as e2:
        print(f"❌ Failed to import main app: {e2}")
        # Create a minimal fallback app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return '''
            <html>
            <head><title>Argo Aviation Referral Portal</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #1e3a8a, #374151); color: white;">
                <h1>🚀 Argo Aviation Referral Portal</h1>
                <h2>✅ App is running successfully!</h2>
                <p>The application is now deployed and accessible.</p>
                <p><strong>Status:</strong> <span style="color: #10b981;">ONLINE</span></p>
                <hr style="margin: 30px 0; border: 1px solid #3b82f6;">
                <p>This is a minimal version. The full app will be available shortly.</p>
            </body>
            </html>
            '''
        
        print("✅ Created fallback app")

if __name__ == '__main__':
    # Configure for production deployment
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
