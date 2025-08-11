"""
FastAPI server to provide real-time visualization data for the political strategy game.
This server bridges the backend visualization system with the frontend HTML dashboard.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from visualization.integrated_manager import IntegratedVisualizationManager
from visualization.base import DataPoint

app = FastAPI(title="Political Strategy Game Visualization Server")

# Global state
visualization_manager = None
connected_clients: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the visualization system on startup."""
    global visualization_manager
    
    print("🚀 Starting Political Strategy Game Visualization Server...")
    
    # Initialize the integrated visualization manager
    visualization_manager = IntegratedVisualizationManager()
    success = await visualization_manager.initialize()
    
    if success:
        print("✅ Visualization manager initialized successfully")
        
        # Create all visualization components
        await visualization_manager.create_component('advisor_network', 'main_network')
        await visualization_manager.create_component('event_timeline', 'main_timeline')
        await visualization_manager.create_component('political_dashboard', 'main_dashboard')
        await visualization_manager.create_component('memory_browser', 'main_memory')
        
        print("✅ All visualization components created")
        
        # Start background task to generate sample data
        asyncio.create_task(generate_sample_data())
        
    else:
        print("❌ Failed to initialize visualization manager")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of visualization system."""
    global visualization_manager
    
    if visualization_manager:
        await visualization_manager.shutdown()
        print("✅ Visualization manager shut down cleanly")

async def generate_sample_data():
    """Generate sample political data and broadcast updates."""
    await asyncio.sleep(2)  # Wait for everything to initialize
    
    advisor_names = ["Chancellor Vex", "Admiral Rex", "Minister Kala", "General Thane", "Diplomat Zara"]
    event_types = ["political", "military", "economic", "diplomatic"]
    
    counter = 0
    
    while True:
        try:
            # Generate advisor relationship data
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
                ),
                DataPoint(
                    data_type='political_events',
                    value=[{
                        'event_id': f'event_{counter}',
                        'timestamp': datetime.now().isoformat(),
                        'title': f'Political Event {counter}',
                        'category': event_types[counter % len(event_types)],
                        'severity': 0.3 + (counter % 7) * 0.1,
                        'participants': [advisor_names[counter % len(advisor_names)]],
                        'description': f'Sample political event number {counter}',
                        'consequences': [],
                        'metadata': {}
                    }],
                    timestamp=datetime.now()
                )
            ]
            
            # Update visualization components
            if visualization_manager:
                await visualization_manager.update_all_components(sample_data)
                
                # Get rendered data from components
                network_data = await get_network_data()
                timeline_data = await get_timeline_data()
                dashboard_data = await get_dashboard_data()
                memory_data = await get_memory_data()
                
                # Broadcast to all connected clients
                update_message = {
                    'type': 'visualization_update',
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'network': network_data,
                        'timeline': timeline_data,
                        'dashboard': dashboard_data,
                        'memory': memory_data
                    }
                }
                
                await manager.broadcast(json.dumps(update_message))
            
            counter += 1
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            await asyncio.sleep(5)

async def get_network_data():
    """Get network visualization data."""
    try:
        if 'main_network' in visualization_manager.components:
            component = visualization_manager.components['main_network']
            rendered = await component.render()
            return rendered.get('data', {})
    except Exception as e:
        print(f"Error getting network data: {e}")
    return {}

async def get_timeline_data():
    """Get timeline visualization data."""
    try:
        if 'main_timeline' in visualization_manager.components:
            component = visualization_manager.components['main_timeline']
            rendered = await component.render()
            return rendered.get('data', {})
    except Exception as e:
        print(f"Error getting timeline data: {e}")
    return {}

async def get_dashboard_data():
    """Get dashboard visualization data."""
    try:
        if 'main_dashboard' in visualization_manager.components:
            component = visualization_manager.components['main_dashboard']
            rendered = await component.render()
            return rendered.get('data', {})
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
    return {}

async def get_memory_data():
    """Get memory browser visualization data."""
    try:
        if 'main_memory' in visualization_manager.components:
            component = visualization_manager.components['main_memory']
            rendered = await component.render()
            return rendered.get('data', {})
    except Exception as e:
        print(f"Error getting memory data: {e}")
    return {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time visualization updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial data
        initial_message = {
            'type': 'connection_established',
            'timestamp': datetime.now().isoformat(),
            'message': 'Connected to Political Strategy Game Visualization Server'
        }
        await websocket.send_text(json.dumps(initial_message))
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'request_update':
                # Send current visualization state
                network_data = await get_network_data()
                timeline_data = await get_timeline_data()
                dashboard_data = await get_dashboard_data()
                memory_data = await get_memory_data()
                
                response = {
                    'type': 'visualization_update',
                    'timestamp': datetime.now().isoformat(),
                    'data': {
                        'network': network_data,
                        'timeline': timeline_data,
                        'dashboard': dashboard_data,
                        'memory': memory_data
                    }
                }
                
                await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket")

@app.get("/")
async def get_visualization_page():
    """Serve the live visualization HTML page."""
    with open('live_visualization.html', 'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/status")
async def get_status():
    """Get current system status."""
    if visualization_manager:
        status = await visualization_manager.get_system_status()
        return {
            'status': 'running',
            'components': status.get('active_components', 0),
            'initialized': status.get('initialized', False),
            'connected_clients': len(manager.active_connections),
            'timestamp': datetime.now().isoformat()
        }
    else:
        return {
            'status': 'not_initialized',
            'components': 0,
            'initialized': False,
            'connected_clients': 0,
            'timestamp': datetime.now().isoformat()
        }

@app.get("/api/network")
async def get_network_api():
    """Get current network visualization data."""
    return await get_network_data()

@app.get("/api/timeline")
async def get_timeline_api():
    """Get current timeline visualization data."""
    return await get_timeline_data()

@app.get("/api/dashboard")
async def get_dashboard_api():
    """Get current dashboard visualization data."""
    return await get_dashboard_data()

@app.get("/api/memory")
async def get_memory_api():
    """Get current memory browser visualization data."""
    return await get_memory_data()

if __name__ == "__main__":
    import uvicorn
    
    print("🏛️ Political Strategy Game Visualization Server")
    print("=" * 50)
    print("🌐 Starting server on http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("📊 Live dashboard: http://localhost:8000")
    print("📋 API status: http://localhost:8000/api/status")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
