#!/usr/bin/env python3
"""
Simple HTTP server to serve visualization data from the political strategy game backend.
This serves as a bridge between the Python visualization system and the HTML frontend.
"""

import json
import sys
import os
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from visualization.integrated_manager import IntegratedVisualizationManager
    from visualization.base import DataPoint
    BACKEND_AVAILABLE = True
except Exception as e:
    print(f"Backend visualization system not available: {e}")
    BACKEND_AVAILABLE = False

class VisualizationServer(BaseHTTPRequestHandler):
    """HTTP request handler for visualization data."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers to allow frontend access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if path == '/':
            self.serve_html_page()
        elif path == '/api/status':
            self.serve_status()
        elif path == '/api/network':
            self.serve_network_data()
        elif path == '/api/timeline':
            self.serve_timeline_data()
        elif path == '/api/dashboard':
            self.serve_dashboard_data()
        elif path == '/api/memory':
            self.serve_memory_data()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_html_page(self):
        """Serve the live visualization HTML page."""
        try:
            # Try multiple possible locations for the HTML file
            html_paths = [
                'live_visualization.html',
                '/home/macneib/political_strategy_game/political_strategy_game/live_visualization.html',
                os.path.join(os.path.dirname(__file__), 'live_visualization.html')
            ]
            
            content = None
            for path in html_paths:
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    break
                except FileNotFoundError:
                    continue
            
            if content is None:
                raise FileNotFoundError("Could not find live_visualization.html in any expected location")
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError as e:
            self.send_error(404, f"HTML file not found: {str(e)}")
    
    def serve_status(self):
        """Serve system status."""
        status = {
            'status': 'running' if BACKEND_AVAILABLE and hasattr(server_instance, 'visualization_manager') else 'simulation',
            'components': 4 if BACKEND_AVAILABLE else 0,
            'initialized': BACKEND_AVAILABLE and hasattr(server_instance, 'visualization_manager'),
            'backend_available': BACKEND_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json_response(status)
    
    def serve_network_data(self):
        """Serve network visualization data."""
        if BACKEND_AVAILABLE and hasattr(server_instance, 'network_data'):
            data = server_instance.network_data
        else:
            # Return sample data
            data = {
                'nodes': [
                    {'id': 'leader', 'name': 'Supreme Leader', 'type': 'leader'},
                    {'id': 'vex', 'name': 'Chancellor Vex', 'type': 'advisor'},
                    {'id': 'rex', 'name': 'Admiral Rex', 'type': 'advisor'},
                    {'id': 'kala', 'name': 'Minister Kala', 'type': 'advisor'}
                ],
                'links': [
                    {'source': 'leader', 'target': 'vex', 'type': 'trust', 'strength': 0.8},
                    {'source': 'leader', 'target': 'rex', 'type': 'trust', 'strength': 0.6},
                    {'source': 'leader', 'target': 'kala', 'type': 'influence', 'strength': 0.7}
                ]
            }
        
        self.send_json_response(data)
    
    def serve_timeline_data(self):
        """Serve timeline visualization data."""
        if BACKEND_AVAILABLE and hasattr(server_instance, 'timeline_data'):
            data = server_instance.timeline_data
        else:
            # Return sample data
            data = {
                'events': [
                    {
                        'id': 1,
                        'name': f'Political Event {int(time.time()) % 100}',
                        'type': 'political',
                        'time': (time.time() % 10) / 10,
                        'severity': 0.5 + (time.time() % 5) / 10
                    }
                ]
            }
        
        self.send_json_response(data)
    
    def serve_dashboard_data(self):
        """Serve dashboard visualization data."""
        if BACKEND_AVAILABLE and hasattr(server_instance, 'dashboard_data'):
            data = server_instance.dashboard_data
        else:
            # Return sample data with some variation
            current_time = time.time()
            data = {
                'coup_probability': 0.3 + 0.4 * abs(math.sin(current_time / 10)),
                'political_stability': 0.7 + 0.2 * abs(math.cos(current_time / 8)),
                'active_factions': 8 + int(current_time % 7),
                'alerts': ['⚠️ Monitoring political tensions', '🔄 Regular status update']
            }
        
        self.send_json_response(data)
    
    def serve_memory_data(self):
        """Serve memory browser visualization data."""
        if BACKEND_AVAILABLE and hasattr(server_instance, 'memory_data'):
            data = server_instance.memory_data
        else:
            # Return sample data
            advisors = ['Chancellor Vex', 'Admiral Rex', 'Minister Kala', 'General Thane']
            actions = ['reviewed budget proposal', 'discussed security concerns', 'analyzed trade data', 'proposed policy changes']
            
            data = {
                'memories': [
                    {
                        'id': i,
                        'advisor': advisors[i % len(advisors)],
                        'content': actions[i % len(actions)],
                        'timestamp': datetime.now().isoformat()
                    }
                    for i in range(5)
                ]
            }
        
        self.send_json_response(data)
    
    def send_json_response(self, data):
        """Send JSON response with proper headers."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, default=str)
        self.wfile.write(json_data.encode())

class VisualizationServerInstance:
    """Server instance to manage visualization backend."""
    
    def __init__(self):
        self.visualization_manager = None
        self.network_data = {}
        self.timeline_data = {}
        self.dashboard_data = {}
        self.memory_data = {}
        self.running = False
    
    async def initialize_backend(self):
        """Initialize the visualization backend."""
        if not BACKEND_AVAILABLE:
            print("❌ Backend visualization system not available")
            return False
        
        try:
            print("🔧 Initializing visualization backend...")
            self.visualization_manager = IntegratedVisualizationManager()
            success = await self.visualization_manager.initialize()
            
            if success:
                print("✅ Visualization manager initialized")
                
                # Create components
                await self.visualization_manager.create_component('advisor_network', 'api_network')
                await self.visualization_manager.create_component('event_timeline', 'api_timeline')
                await self.visualization_manager.create_component('political_dashboard', 'api_dashboard')
                await self.visualization_manager.create_component('memory_browser', 'api_memory')
                
                print("✅ All visualization components created")
                
                # Start data generation
                self.running = True
                asyncio.create_task(self.generate_data_updates())
                
                return True
            else:
                print("❌ Failed to initialize visualization manager")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing backend: {e}")
            return False
    
    async def generate_data_updates(self):
        """Generate sample data updates for the visualization system."""
        counter = 0
        advisor_names = ["Chancellor Vex", "Admiral Rex", "Minister Kala", "General Thane"]
        
        while self.running:
            try:
                # Generate sample data
                sample_data = [
                    DataPoint(
                        data_type='advisor_metrics',
                        value={
                            'advisor_id': f'adv_{counter % len(advisor_names)}',
                            'name': advisor_names[counter % len(advisor_names)],
                            'trust_level': 0.3 + (counter % 7) * 0.1,
                            'influence': 0.4 + (counter % 6) * 0.1,
                            'faction': ['loyalist', 'military', 'economic'][counter % 3]
                        },
                        timestamp=datetime.now()
                    )
                ]
                
                # Update components
                await self.visualization_manager.update_all_components(sample_data)
                
                # Fetch rendered data
                if 'api_network' in self.visualization_manager.components:
                    rendered = await self.visualization_manager.components['api_network'].render()
                    self.network_data = rendered.get('data', {})
                
                if 'api_timeline' in self.visualization_manager.components:
                    rendered = await self.visualization_manager.components['api_timeline'].render()
                    self.timeline_data = rendered.get('data', {})
                
                counter += 1
                await asyncio.sleep(3)  # Update every 3 seconds
                
            except Exception as e:
                print(f"Error generating data updates: {e}")
                await asyncio.sleep(5)
    
    async def shutdown(self):
        """Shutdown the backend."""
        self.running = False
        if self.visualization_manager:
            await self.visualization_manager.shutdown()

# Import math for dashboard calculations
import math

# Global server instance
server_instance = VisualizationServerInstance()

def run_server():
    """Run the HTTP server."""
    print("🏛️ Political Strategy Game Visualization Server")
    print("=" * 50)
    
    # Try to initialize backend
    if BACKEND_AVAILABLE:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize backend in background
            def init_backend():
                loop.run_until_complete(server_instance.initialize_backend())
            
            backend_thread = threading.Thread(target=init_backend)
            backend_thread.daemon = True
            backend_thread.start()
            
        except Exception as e:
            print(f"Could not initialize backend: {e}")
    
    # Start HTTP server
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, VisualizationServer)
    
    print("🌐 Server running on http://localhost:8000")
    print("📊 Live dashboard: http://localhost:8000")
    print("📋 API status: http://localhost:8000/api/status")
    print("🔌 API endpoints:")
    print("   - GET /api/network   (Advisor relationship data)")
    print("   - GET /api/timeline  (Political event data)")
    print("   - GET /api/dashboard (Political metrics)")
    print("   - GET /api/memory    (Memory browser data)")
    print("=" * 50)
    print("🚀 Server started! Open http://localhost:8000 in your browser")
    print("💡 Click 'Connect' in the dashboard to receive live updates")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        
        # Shutdown backend
        if BACKEND_AVAILABLE and server_instance.visualization_manager:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(server_instance.shutdown())
        
        httpd.server_close()
        print("✅ Server shut down cleanly")

if __name__ == "__main__":
    run_server()
