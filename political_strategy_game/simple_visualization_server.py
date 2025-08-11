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
        # Embedded HTML content instead of reading from file
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Political Strategy Game - Live Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; color: #4fc3f7; margin-bottom: 30px; }
        .status-bar { background: #16213e; border: 1px solid #4fc3f7; border-radius: 5px; padding: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .connection-status { display: flex; align-items: center; gap: 10px; }
        .status-indicator { width: 10px; height: 10px; border-radius: 50%; background: #ff6b6b; }
        .status-indicator.connected { background: #4ecdc4; }
        .btn { background: #4fc3f7; color: #1a1a2e; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; margin: 0 5px; }
        .btn:hover { background: #45a7d1; }
        .visualization-grid { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 20px; height: 75vh; }
        .viz-panel { background: #16213e; border: 2px solid #4fc3f7; border-radius: 10px; padding: 15px; position: relative; }
        .viz-title { color: #4fc3f7; font-size: 18px; font-weight: bold; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .last-update { font-size: 12px; color: #999; font-weight: normal; }
        .network-container { grid-column: 1 / 3; }
        .node { stroke: #4fc3f7; stroke-width: 2px; cursor: pointer; }
        .node.advisor { fill: #ff6b6b; }
        .node.leader { fill: #4ecdc4; }
        .link { stroke: #999; stroke-opacity: 0.6; }
        .link.trust { stroke: #4ecdc4; }
        .link.conflict { stroke: #ff6b6b; }
        .link.influence { stroke: #feca57; }
        .timeline-event { fill: #4fc3f7; stroke: #fff; stroke-width: 1px; cursor: pointer; }
        .timeline-event.political { fill: #ff6b6b; }
        .timeline-event.military { fill: #feca57; }
        .timeline-event.economic { fill: #4ecdc4; }
        .metric-box { background: #0f3460; border: 1px solid #4fc3f7; border-radius: 5px; padding: 10px; margin: 5px 0; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #4fc3f7; }
        .metric-label { font-size: 12px; color: #ccc; }
        .alert { background: #ff6b6b; color: white; padding: 5px 10px; border-radius: 3px; margin: 2px 0; font-size: 12px; }
        .memory-item { background: #0f3460; border-left: 3px solid #4fc3f7; padding: 8px; margin: 5px 0; border-radius: 3px; }
        .memory-timestamp { font-size: 10px; color: #999; }
        .demo-note { background: #2d1b69; border: 1px solid #6c5ce7; border-radius: 5px; padding: 10px; margin: 10px 0; font-size: 14px; color: #a29bfe; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ Political Strategy Game - Live Visualization Dashboard</h1>
        
        <div class="status-bar">
            <div class="connection-status">
                <div class="status-indicator" id="connection-indicator"></div>
                <span id="connection-text">Ready to connect...</span>
            </div>
            <div>
                <button class="btn" id="connect-btn" onclick="connectToBackend()">Connect</button>
                <button class="btn" onclick="simulateEvent()">Simulate Event</button>
                <button class="btn" onclick="clearData()">Clear Data</button>
            </div>
        </div>
        
        <div class="visualization-grid">
            <div class="viz-panel network-container">
                <div class="viz-title">🕸️ Advisor Relationship Network <span class="last-update" id="network-update">Never updated</span></div>
                <svg id="network-graph" width="100%" height="300"></svg>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">📅 Political Event Timeline <span class="last-update" id="timeline-update">Never updated</span></div>
                <svg id="timeline" width="100%" height="180"></svg>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">📊 Political Status Dashboard <span class="last-update" id="dashboard-update">Never updated</span></div>
                <div id="dashboard"></div>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">🧠 Memory System Browser <span class="last-update" id="memory-update">Never updated</span></div>
                <div id="memory-browser"></div>
            </div>
        </div>
        
        <div class="demo-note">
            <strong>🔄 Live Updates:</strong> Connected to real backend visualization system. Data updates every 2-3 seconds.
        </div>
    </div>

    <script>
        let isConnected = false;
        let networkData = { nodes: [], links: [] };
        let timelineData = [];
        let networkSvg, timelineSvg, simulation;
        
        function initializeVisualizations() {
            networkSvg = d3.select("#network-graph");
            timelineSvg = d3.select("#timeline");
            
            const width = networkSvg.node().getBoundingClientRect().width;
            simulation = d3.forceSimulation()
                .force("link", d3.forceLink().id(d => d.id).distance(80))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, 150));
            
            initializeDashboard();
            initializeMemoryBrowser();
        }
        
        function connectToBackend() {
            const indicator = document.getElementById('connection-indicator');
            const statusText = document.getElementById('connection-text');
            const connectBtn = document.getElementById('connect-btn');
            
            if (!isConnected) {
                isConnected = true;
                indicator.classList.add('connected');
                statusText.textContent = 'Connected to Backend';
                connectBtn.textContent = 'Disconnect';
                
                // Start polling for updates
                pollBackendData();
                setInterval(pollBackendData, 2000);
            } else {
                disconnect();
            }
        }
        
        function disconnect() {
            const indicator = document.getElementById('connection-indicator');
            const statusText = document.getElementById('connection-text');
            const connectBtn = document.getElementById('connect-btn');
            
            isConnected = false;
            indicator.classList.remove('connected');
            statusText.textContent = 'Disconnected';
            connectBtn.textContent = 'Connect';
        }
        
        async function pollBackendData() {
            if (!isConnected) return;
            
            try {
                const [networkResp, timelineResp, dashboardResp, memoryResp] = await Promise.all([
                    fetch('/api/network'),
                    fetch('/api/timeline'),
                    fetch('/api/dashboard'),
                    fetch('/api/memory')
                ]);
                
                const networkData = await networkResp.json();
                const timelineData = await timelineResp.json();
                const dashboardData = await dashboardResp.json();
                const memoryData = await memoryResp.json();
                
                updateNetwork(networkData);
                updateTimeline(timelineData.events);
                updateDashboard(dashboardData);
                updateMemoryBrowser(memoryData.memories);
                
            } catch (error) {
                console.log('Error polling backend:', error);
            }
        }
        
        function updateNetwork(data) {
            if (!data || !data.nodes) return;
            
            const width = networkSvg.node().getBoundingClientRect().width;
            networkSvg.selectAll("*").remove();
            
            const link = networkSvg.append("g").selectAll("line").data(data.links).enter().append("line")
                .attr("class", d => `link ${d.type}`).attr("stroke-width", d => Math.sqrt(d.strength * 5));
            
            const node = networkSvg.append("g").selectAll("circle").data(data.nodes).enter().append("circle")
                .attr("class", d => `node ${d.type}`).attr("r", d => d.type === "leader" ? 20 : 15);
            
            const labels = networkSvg.append("g").selectAll("text").data(data.nodes).enter().append("text")
                .text(d => d.name).attr("font-size", "12px").attr("fill", "#eee").attr("text-anchor", "middle").attr("dy", 30);
            
            simulation.nodes(data.nodes).force("link").links(data.links);
            simulation.restart();
            
            simulation.on("tick", () => {
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y).attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("cx", d => d.x).attr("cy", d => d.y);
                labels.attr("x", d => d.x).attr("y", d => d.y);
            });
            
            document.getElementById('network-update').textContent = new Date().toLocaleTimeString();
        }
        
        function updateTimeline(events) {
            if (!events) events = [];
            
            const width = timelineSvg.node().getBoundingClientRect().width;
            const height = 180;
            timelineSvg.selectAll("*").remove();
            
            timelineSvg.append("line").attr("x1", 20).attr("y1", height - 20).attr("x2", width - 20).attr("y2", height - 20)
                .attr("stroke", "#4fc3f7").attr("stroke-width", 2);
            
            timelineSvg.selectAll("circle").data(events).enter().append("circle")
                .attr("class", d => `timeline-event ${d.type}`)
                .attr("cx", d => d.time * (width - 40) + 20)
                .attr("cy", d => height - (d.severity * 80 + 40))
                .attr("r", d => d.severity * 8 + 4);
            
            document.getElementById('timeline-update').textContent = new Date().toLocaleTimeString();
        }
        
        function initializeDashboard() {
            updateDashboard({ coup_probability: 0.15, political_stability: 0.85, active_factions: 8, alerts: [] });
        }
        
        function updateDashboard(metrics) {
            const dashboard = d3.select("#dashboard");
            dashboard.selectAll("*").remove();
            
            [
                { key: 'coup_probability', label: 'Coup Probability', format: d => Math.round(d * 100) + '%' },
                { key: 'political_stability', label: 'Political Stability', format: d => Math.round(d * 100) + '%' },
                { key: 'active_factions', label: 'Active Factions', format: d => d.toString() }
            ].forEach(metric => {
                const box = dashboard.append("div").attr("class", "metric-box");
                box.append("div").attr("class", "metric-value").text(metric.format(metrics[metric.key] || 0));
                box.append("div").attr("class", "metric-label").text(metric.label);
            });
            
            if (metrics.alerts) {
                metrics.alerts.forEach(alert => {
                    dashboard.append("div").attr("class", "alert").text(alert);
                });
            }
            
            document.getElementById('dashboard-update').textContent = new Date().toLocaleTimeString();
        }
        
        function initializeMemoryBrowser() {
            updateMemoryBrowser([{ id: 1, advisor: "System", content: "Visualization system initialized", timestamp: new Date() }]);
        }
        
        function updateMemoryBrowser(memories) {
            if (!memories) memories = [];
            
            const memoryBrowser = d3.select("#memory-browser");
            memoryBrowser.selectAll("*").remove();
            
            memories.slice(-10).forEach(memory => {
                const item = memoryBrowser.append("div").attr("class", "memory-item");
                item.append("strong").text(memory.advisor + ": ");
                item.append("span").text(memory.content);
                item.append("div").attr("class", "memory-timestamp").text(formatTimeAgo(memory.timestamp));
            });
            
            document.getElementById('memory-update').textContent = new Date().toLocaleTimeString();
        }
        
        function formatTimeAgo(timestamp) {
            const now = new Date();
            const diff = Math.abs(now - new Date(timestamp)) / 1000;
            if (diff < 60) return `${Math.floor(diff)} seconds ago`;
            if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
            return `${Math.floor(diff / 3600)} hours ago`;
        }
        
        function simulateEvent() {
            // Trigger a manual update
            if (isConnected) pollBackendData();
        }
        
        function clearData() {
            networkSvg.selectAll("*").remove();
            timelineSvg.selectAll("*").remove();
            d3.select("#dashboard").selectAll("*").remove();
            d3.select("#memory-browser").selectAll("*").remove();
            
            initializeDashboard();
            initializeMemoryBrowser();
        }
        
        document.addEventListener('DOMContentLoaded', initializeVisualizations);
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
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
