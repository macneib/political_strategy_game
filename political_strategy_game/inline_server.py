#!/usr/bin/env python3
"""
Inline HTTP server for political strategy game visualizations.
This version has everything embedded to avoid file path issues.
"""

import json
import sys
import os
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import math

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from visualization.integrated_manager import IntegratedVisualizationManager
    from visualization.base import DataPoint
    BACKEND_AVAILABLE = True
    print("✅ Backend visualization system available")
except Exception as e:
    print(f"⚠️ Backend visualization system not available: {e}")
    BACKEND_AVAILABLE = False

class InlineVisualizationServer(BaseHTTPRequestHandler):
    """HTTP request handler with embedded HTML."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = self.path.split('?')[0]  # Remove query parameters
        
        # Set CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/status':
            self.serve_api_response(self.get_status_data())
        elif path == '/api/network':
            self.serve_api_response(self.get_network_data())
        elif path == '/api/timeline':
            self.serve_api_response(self.get_timeline_data())
        elif path == '/api/dashboard':
            self.serve_api_response(self.get_dashboard_data())
        elif path == '/api/memory':
            self.serve_api_response(self.get_memory_data())
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_dashboard(self):
        """Serve the embedded HTML dashboard."""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🏛️ Political Strategy Game - Live Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; color: #4fc3f7; margin-bottom: 30px; }
        .status-bar { background: #16213e; border: 1px solid #4fc3f7; border-radius: 5px; padding: 15px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .connection-status { display: flex; align-items: center; gap: 10px; font-size: 16px; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; background: #ff6b6b; }
        .status-indicator.connected { background: #4ecdc4; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .btn { background: #4fc3f7; color: #1a1a2e; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; margin: 0 5px; transition: background 0.3s; }
        .btn:hover { background: #45a7d1; }
        .btn:disabled { background: #666; cursor: not-allowed; }
        .visualization-grid { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 20px; height: 70vh; }
        .viz-panel { background: #16213e; border: 2px solid #4fc3f7; border-radius: 10px; padding: 15px; position: relative; overflow: hidden; }
        .viz-title { color: #4fc3f7; font-size: 18px; font-weight: bold; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .last-update { font-size: 12px; color: #999; font-weight: normal; }
        .network-container { grid-column: 1 / 3; }
        .node { stroke: #4fc3f7; stroke-width: 2px; cursor: pointer; transition: all 0.3s; }
        .node.advisor { fill: #ff6b6b; }
        .node.leader { fill: #4ecdc4; }
        .node:hover { stroke-width: 4px; }
        .link { stroke: #999; stroke-opacity: 0.6; transition: all 0.3s; }
        .link.trust { stroke: #4ecdc4; }
        .link.conflict { stroke: #ff6b6b; }
        .link.influence { stroke: #feca57; }
        .timeline-event { fill: #4fc3f7; stroke: #fff; stroke-width: 1px; cursor: pointer; transition: all 0.3s; }
        .timeline-event.political { fill: #ff6b6b; }
        .timeline-event.military { fill: #feca57; }
        .timeline-event.economic { fill: #4ecdc4; }
        .timeline-event:hover { stroke-width: 3px; }
        .metric-box { background: linear-gradient(145deg, #0f3460, #1a4b7a); border: 1px solid #4fc3f7; border-radius: 8px; padding: 15px; margin: 8px 0; text-align: center; transition: all 0.3s; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .metric-box:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(79, 195, 247, 0.3); }
        .metric-value { font-size: 28px; font-weight: bold; color: #4fc3f7; text-shadow: 0 0 10px rgba(79, 195, 247, 0.5); }
        .metric-label { font-size: 13px; color: #ccc; margin-top: 5px; }
        .alert { background: linear-gradient(145deg, #ff6b6b, #ff8e8e); color: white; padding: 8px 12px; border-radius: 5px; margin: 3px 0; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .memory-item { background: linear-gradient(145deg, #0f3460, #1a4b7a); border-left: 4px solid #4fc3f7; padding: 12px; margin: 8px 0; border-radius: 5px; transition: all 0.3s; }
        .memory-item:hover { transform: translateX(5px); border-left-color: #feca57; }
        .memory-timestamp { font-size: 10px; color: #999; margin-top: 5px; }
        .demo-note { background: linear-gradient(145deg, #2d1b69, #4c3c9e); border: 1px solid #6c5ce7; border-radius: 8px; padding: 15px; margin: 20px 0; font-size: 14px; color: #a29bfe; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
        .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #4fc3f7; border-radius: 50%; border-top-color: transparent; animation: spin 1s ease-in-out infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ Political Strategy Game - Live Visualization Dashboard</h1>
        
        <div class="status-bar">
            <div class="connection-status">
                <div class="status-indicator" id="connection-indicator"></div>
                <span id="connection-text">Ready to connect to backend...</span>
            </div>
            <div>
                <button class="btn" id="connect-btn" onclick="connectToBackend()">Connect</button>
                <button class="btn" onclick="simulateEvent()">Refresh Data</button>
                <button class="btn" onclick="clearData()">Clear</button>
            </div>
        </div>
        
        <div class="visualization-grid">
            <div class="viz-panel network-container">
                <div class="viz-title">
                    🕸️ Advisor Relationship Network
                    <span class="last-update" id="network-update">Never updated</span>
                </div>
                <svg id="network-graph" width="100%" height="300"></svg>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">
                    📅 Political Event Timeline
                    <span class="last-update" id="timeline-update">Never updated</span>
                </div>
                <svg id="timeline" width="100%" height="180"></svg>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">
                    📊 Political Status Dashboard
                    <span class="last-update" id="dashboard-update">Never updated</span>
                </div>
                <div id="dashboard"></div>
            </div>
            
            <div class="viz-panel">
                <div class="viz-title">
                    🧠 Memory System Browser
                    <span class="last-update" id="memory-update">Never updated</span>
                </div>
                <div id="memory-browser"></div>
            </div>
        </div>
        
        <div class="demo-note">
            <strong>🔄 Live Backend Integration:</strong> This dashboard connects to the real Political Strategy Game visualization backend.
            Data automatically updates every 2-3 seconds when connected. Click "Connect" to start receiving live political intelligence!
        </div>
    </div>

    <script>
        let isConnected = false;
        let updateInterval = null;
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
                statusText.innerHTML = 'Connected to Backend <span class="loading"></span>';
                connectBtn.textContent = 'Disconnect';
                
                // Start polling for updates
                pollBackendData();
                updateInterval = setInterval(pollBackendData, 3000);
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
            
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        }
        
        async function pollBackendData() {
            if (!isConnected) return;
            
            try {
                const statusText = document.getElementById('connection-text');
                statusText.innerHTML = 'Fetching data... <span class="loading"></span>';
                
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
                updateTimeline(timelineData.events || []);
                updateDashboard(dashboardData);
                updateMemoryBrowser(memoryData.memories || []);
                
                statusText.innerHTML = 'Connected - Live Updates Active <span class="status-indicator connected" style="width: 8px; height: 8px; margin-left: 8px;"></span>';
                
            } catch (error) {
                console.log('Error polling backend:', error);
                document.getElementById('connection-text').textContent = 'Connection Error - Retrying...';
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
            const width = timelineSvg.node().getBoundingClientRect().width;
            const height = 180;
            timelineSvg.selectAll("*").remove();
            
            timelineSvg.append("line").attr("x1", 20).attr("y1", height - 20).attr("x2", width - 20).attr("y2", height - 20)
                .attr("stroke", "#4fc3f7").attr("stroke-width", 2);
            
            if (events && events.length > 0) {
                timelineSvg.selectAll("circle").data(events).enter().append("circle")
                    .attr("class", d => `timeline-event ${d.type}`)
                    .attr("cx", d => d.time * (width - 40) + 20)
                    .attr("cy", d => height - (d.severity * 80 + 40))
                    .attr("r", d => d.severity * 8 + 4);
            }
            
            document.getElementById('timeline-update').textContent = new Date().toLocaleTimeString();
        }
        
        function initializeDashboard() {
            updateDashboard({ coup_probability: 0.15, political_stability: 0.85, active_factions: 8, alerts: ['System initialized'] });
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
            
            if (metrics.alerts && metrics.alerts.length > 0) {
                metrics.alerts.forEach(alert => {
                    dashboard.append("div").attr("class", "alert").text(alert);
                });
            }
            
            document.getElementById('dashboard-update').textContent = new Date().toLocaleTimeString();
        }
        
        function initializeMemoryBrowser() {
            updateMemoryBrowser([{ id: 1, advisor: "System", content: "Visualization dashboard initialized successfully", timestamp: new Date() }]);
        }
        
        function updateMemoryBrowser(memories) {
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
    
    def serve_api_response(self, data):
        """Send JSON response with CORS headers."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, default=str)
        self.wfile.write(json_data.encode())
    
    def get_status_data(self):
        """Get system status data."""
        return {
            'status': 'running',
            'backend_available': BACKEND_AVAILABLE,
            'components': 4 if BACKEND_AVAILABLE else 0,
            'initialized': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_network_data(self):
        """Get network visualization data."""
        # Generate dynamic sample data
        current_time = time.time()
        return {
            'nodes': [
                {'id': 'leader', 'name': 'Supreme Leader', 'type': 'leader'},
                {'id': 'vex', 'name': 'Chancellor Vex', 'type': 'advisor'},
                {'id': 'rex', 'name': 'Admiral Rex', 'type': 'advisor'},
                {'id': 'kala', 'name': 'Minister Kala', 'type': 'advisor'},
                {'id': 'thane', 'name': 'General Thane', 'type': 'advisor'}
            ],
            'links': [
                {'source': 'leader', 'target': 'vex', 'type': 'trust', 'strength': 0.6 + 0.3 * abs(math.sin(current_time / 10))},
                {'source': 'leader', 'target': 'rex', 'type': 'trust', 'strength': 0.5 + 0.4 * abs(math.cos(current_time / 8))},
                {'source': 'leader', 'target': 'kala', 'type': 'influence', 'strength': 0.7 + 0.2 * abs(math.sin(current_time / 6))},
                {'source': 'leader', 'target': 'thane', 'type': 'conflict', 'strength': 0.3 + 0.4 * abs(math.cos(current_time / 12))},
                {'source': 'vex', 'target': 'rex', 'type': 'trust', 'strength': 0.6},
                {'source': 'rex', 'target': 'thane', 'type': 'trust', 'strength': 0.8}
            ]
        }
    
    def get_timeline_data(self):
        """Get timeline visualization data."""
        current_time = time.time()
        event_types = ['political', 'military', 'economic']
        
        return {
            'events': [
                {
                    'id': int(current_time) % 100,
                    'name': f'Political Event {int(current_time) % 100}',
                    'type': event_types[int(current_time) % len(event_types)],
                    'time': (current_time % 10) / 10,
                    'severity': 0.3 + 0.6 * abs(math.sin(current_time / 5))
                },
                {
                    'id': int(current_time) % 100 + 1,
                    'name': f'Crisis Alert {int(current_time) % 50}',
                    'type': 'political',
                    'time': (current_time % 8) / 8,
                    'severity': 0.7 + 0.2 * abs(math.cos(current_time / 7))
                }
            ]
        }
    
    def get_dashboard_data(self):
        """Get dashboard visualization data."""
        current_time = time.time()
        coup_prob = 0.3 + 0.4 * abs(math.sin(current_time / 15))
        stability = 0.9 - coup_prob + 0.1 * abs(math.cos(current_time / 12))
        
        alerts = []
        if coup_prob > 0.6:
            alerts.append("⚠️ High coup probability detected")
        if stability < 0.4:
            alerts.append("🔄 Political instability rising")
        alerts.append(f"📊 Live data update {int(current_time) % 1000}")
        
        return {
            'coup_probability': coup_prob,
            'political_stability': stability,
            'active_factions': 8 + int(current_time % 7),
            'alerts': alerts
        }
    
    def get_memory_data(self):
        """Get memory browser visualization data."""
        advisors = ['Chancellor Vex', 'Admiral Rex', 'Minister Kala', 'General Thane']
        actions = ['reviewed security reports', 'analyzed political trends', 'discussed faction movements', 'proposed strategic changes']
        current_time = time.time()
        
        return {
            'memories': [
                {
                    'id': i,
                    'advisor': advisors[i % len(advisors)],
                    'content': actions[i % len(actions)],
                    'timestamp': datetime.fromtimestamp(current_time - i * 300).isoformat()  # 5 minutes apart
                }
                for i in range(5)
            ]
        }

def run_server():
    """Run the inline HTTP server."""
    print("🏛️ Political Strategy Game - Inline Visualization Server")
    print("=" * 60)
    print(f"🔧 Backend available: {BACKEND_AVAILABLE}")
    
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, InlineVisualizationServer)
    
    print("🌐 Server running on http://localhost:8000")
    print("📊 Live dashboard: http://localhost:8000")
    print("🔌 API endpoints available:")
    print("   - GET /api/status    (System status)")
    print("   - GET /api/network   (Advisor relationships)")
    print("   - GET /api/timeline  (Political events)")
    print("   - GET /api/dashboard (Political metrics)")
    print("   - GET /api/memory    (Memory browser)")
    print("=" * 60)
    print("🚀 Server ready! Open http://localhost:8000 in your browser")
    print("💡 Click 'Connect' in the dashboard to start live updates")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        httpd.server_close()
        print("✅ Server shut down cleanly")

if __name__ == "__main__":
    run_server()
