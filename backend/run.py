"""
Run the Production-Grade Grievance System Flask Application
Entry point for the backend server
"""

import os
from app.main import app

if __name__ == '__main__':
    # Production settings
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print("\n" + "="*60)
    print("GRIEVANCE SYSTEM - PRODUCTION API")
    print("="*60)
    print(f"Environment: {'Development' if debug_mode else 'Production'}")
    print(f"Port: {port}")
    print(f"Debug: {debug_mode}")
    print("="*60 + "\n")
    
    # Start server
    app.run(
        debug=debug_mode,
        port=port,
        host='0.0.0.0',
        threaded=True
    )
