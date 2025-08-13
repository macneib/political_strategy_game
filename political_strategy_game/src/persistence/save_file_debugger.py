#!/usr/bin/env python3
"""
Save File Debugging Tools and Utilities for Task 7.2

This module provides comprehensive debugging and analysis tools for save files:
- Save file inspection and analysis
- Data structure validation
- Performance profiling
- Corruption detection and repair
- Save file comparison and diff tools
"""

import json
import gzip
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import pickle
import sys
from collections import defaultdict

from src.persistence.save_game_manager import (
    SaveGameManager, SaveGameData, SaveGameMetadata, 
    SaveFileFormat, SaveFileVersion, IntegrityValidator
)


class AnalysisLevel(str, Enum):
    """Analysis depth levels."""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class SaveFileAnalysis:
    """Results of save file analysis."""
    file_path: Path
    file_size: int
    format: SaveFileFormat
    version: SaveFileVersion
    compression_ratio: float
    metadata: SaveGameMetadata
    structure_stats: Dict[str, Any]
    validation_errors: List[str]
    warnings: List[str]
    performance_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            'file_path': str(self.file_path),
            'file_size': self.file_size,
            'format': self.format.value,
            'version': self.version.value,
            'compression_ratio': self.compression_ratio,
            'metadata': self.metadata.to_dict(),
            'structure_stats': self.structure_stats,
            'validation_errors': self.validation_errors,
            'warnings': self.warnings,
            'performance_metrics': self.performance_metrics
        }


@dataclass
class SaveFileComparison:
    """Results of comparing two save files."""
    file_a: Path
    file_b: Path
    differences: List[Dict[str, Any]]
    similarity_score: float
    metadata_changes: Dict[str, Any]
    structure_changes: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            'file_a': str(self.file_a),
            'file_b': str(self.file_b),
            'differences': self.differences,
            'similarity_score': self.similarity_score,
            'metadata_changes': self.metadata_changes,
            'structure_changes': self.structure_changes
        }


class SaveFileDebugger:
    """Comprehensive save file debugging and analysis tool."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integrity_validator = IntegrityValidator()
    
    def analyze_save_file(self, save_path: Path, 
                         analysis_level: AnalysisLevel = AnalysisLevel.DETAILED) -> SaveFileAnalysis:
        """
        Perform comprehensive analysis of a save file.
        
        Args:
            save_path: Path to save file
            analysis_level: Depth of analysis to perform
            
        Returns:
            Detailed analysis results
        """
        try:
            self.logger.info(f"Analyzing save file: {save_path}")
            
            # Basic file info
            file_size = save_path.stat().st_size
            
            # Performance timing
            start_time = datetime.now()
            
            # Read and parse save file
            save_data = self._load_save_file_raw(save_path)
            load_time = (datetime.now() - start_time).total_seconds()
            
            # Determine format and compression
            format_info = self._detect_save_format(save_path)
            
            # Analyze structure
            structure_stats = self._analyze_structure(save_data, analysis_level)
            
            # Validate integrity
            validation_errors = []
            warnings = []
            
            if analysis_level in [AnalysisLevel.DETAILED, AnalysisLevel.COMPREHENSIVE]:
                validation_errors = self.integrity_validator.validate_save_file(save_data)
                warnings = self._detect_warnings(save_data)
            
            # Performance metrics
            performance_metrics = {
                'load_time_seconds': load_time,
                'parse_time_seconds': 0.0,  # Would measure parsing time separately
                'validation_time_seconds': 0.0,  # Would measure validation time
                'memory_usage_mb': self._estimate_memory_usage(save_data)
            }
            
            return SaveFileAnalysis(
                file_path=save_path,
                file_size=file_size,
                format=format_info['format'],
                version=SaveFileVersion(save_data.metadata.version),
                compression_ratio=format_info['compression_ratio'],
                metadata=save_data.metadata,
                structure_stats=structure_stats,
                validation_errors=validation_errors,
                warnings=warnings,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise
    
    def compare_save_files(self, file_a: Path, file_b: Path) -> SaveFileComparison:
        """
        Compare two save files and identify differences.
        
        Args:
            file_a: First save file
            file_b: Second save file
            
        Returns:
            Detailed comparison results
        """
        try:
            self.logger.info(f"Comparing save files: {file_a} vs {file_b}")
            
            # Load both save files
            save_data_a = self._load_save_file_raw(file_a)
            save_data_b = self._load_save_file_raw(file_b)
            
            # Convert to dictionaries for comparison
            dict_a = save_data_a.to_dict()
            dict_b = save_data_b.to_dict()
            
            # Find differences
            differences = self._find_differences(dict_a, dict_b)
            
            # Calculate similarity score
            similarity_score = self._calculate_similarity(dict_a, dict_b)
            
            # Analyze metadata changes
            metadata_changes = self._compare_metadata(save_data_a.metadata, save_data_b.metadata)
            
            # Analyze structure changes
            structure_changes = self._compare_structures(dict_a, dict_b)
            
            return SaveFileComparison(
                file_a=file_a,
                file_b=file_b,
                differences=differences,
                similarity_score=similarity_score,
                metadata_changes=metadata_changes,
                structure_changes=structure_changes
            )
            
        except Exception as e:
            self.logger.error(f"Comparison failed: {e}")
            raise
    
    def repair_save_file(self, corrupted_path: Path, output_path: Path) -> bool:
        """
        Attempt to repair a corrupted save file.
        
        Args:
            corrupted_path: Path to corrupted save file
            output_path: Path for repaired save file
            
        Returns:
            True if repair was successful
        """
        try:
            self.logger.info(f"Attempting to repair save file: {corrupted_path}")
            
            # Try to load corrupted file with error tolerance
            save_data = self._load_save_file_tolerant(corrupted_path)
            
            if save_data is None:
                self.logger.error("Unable to recover any data from corrupted file")
                return False
            
            # Attempt repairs
            repaired_data = self._attempt_repairs(save_data)
            
            # Validate repaired data
            validation_errors = self.integrity_validator.validate_save_file(repaired_data)
            
            if validation_errors:
                self.logger.warning(f"Repaired file still has {len(validation_errors)} validation errors")
            
            # Save repaired file
            save_manager = SaveGameManager(output_path.parent)
            save_manager._write_save_file(repaired_data, output_path, SaveFileFormat.JSON_COMPRESSED)
            
            self.logger.info(f"Repaired save file written to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Repair failed: {e}")
            return False
    
    def extract_save_data(self, save_path: Path, output_dir: Path, 
                         extract_format: str = "json") -> bool:
        """
        Extract save file data to human-readable format.
        
        Args:
            save_path: Path to save file
            output_dir: Directory for extracted data
            extract_format: Format for extracted data (json, csv, etc.)
            
        Returns:
            True if extraction was successful
        """
        try:
            self.logger.info(f"Extracting save file: {save_path}")
            
            save_data = self._load_save_file_raw(save_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if extract_format == "json":
                # Extract metadata
                metadata_path = output_dir / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(save_data.metadata.to_dict(), f, indent=2, default=str)
                
                # Extract game state
                game_state_path = output_dir / "game_state.json"
                with open(game_state_path, 'w') as f:
                    json.dump(save_data.game_state.to_dict(), f, indent=2, default=str)
                
                # Extract memory banks
                memory_dir = output_dir / "memory_banks"
                memory_dir.mkdir(exist_ok=True)
                
                for civ_id, memory_bank in save_data.memory_banks.items():
                    memory_path = memory_dir / f"{civ_id}.json"
                    with open(memory_path, 'w') as f:
                        json.dump(memory_bank.model_dump(), f, indent=2, default=str)
                
                # Extract civilizations
                civ_dir = output_dir / "civilizations"
                civ_dir.mkdir(exist_ok=True)
                
                for civ_id, civ_data in save_data.civilizations.items():
                    civ_path = civ_dir / f"{civ_id}.json"
                    with open(civ_path, 'w') as f:
                        json.dump(civ_data, f, indent=2, default=str)
            
            self.logger.info(f"Extraction completed: {output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return False
    
    def generate_save_report(self, save_path: Path, output_path: Path) -> bool:
        """
        Generate a comprehensive analysis report for a save file.
        
        Args:
            save_path: Path to save file
            output_path: Path for output report
            
        Returns:
            True if report was generated successfully
        """
        try:
            # Perform comprehensive analysis
            analysis = self.analyze_save_file(save_path, AnalysisLevel.COMPREHENSIVE)
            
            # Generate HTML report
            html_content = self._generate_html_report(analysis)
            
            with open(output_path, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"Report generated: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return False
    
    def _load_save_file_raw(self, save_path: Path) -> SaveGameData:
        """Load save file using SaveGameManager."""
        save_manager = SaveGameManager(save_path.parent)
        return save_manager.load_game(save_path)
    
    def _load_save_file_tolerant(self, save_path: Path) -> Optional[SaveGameData]:
        """Attempt to load a corrupted save file with error tolerance."""
        try:
            # Try normal loading first
            return self._load_save_file_raw(save_path)
        except:
            pass
        
        # Try different approaches for corrupted files
        try:
            # Try reading as raw JSON
            with open(save_path, 'rb') as f:
                data = f.read()
            
            # Try decompression
            try:
                import gzip
                data = gzip.decompress(data)
            except:
                pass
            
            # Parse JSON with error tolerance
            json_str = data.decode('utf-8', errors='ignore')
            save_dict = json.loads(json_str)
            
            # Reconstruct SaveGameData with default values for missing fields
            return self._reconstruct_save_data(save_dict)
            
        except Exception as e:
            self.logger.error(f"Tolerant loading failed: {e}")
            return None
    
    def _detect_save_format(self, save_path: Path) -> Dict[str, Any]:
        """Detect save file format and compression info."""
        with open(save_path, 'rb') as f:
            data = f.read()
        
        original_size = len(data)
        format_type = SaveFileFormat.BINARY
        compression_ratio = 0.0
        
        # Try to decompress
        try:
            decompressed = gzip.decompress(data)
            compression_ratio = (original_size - len(decompressed)) / original_size if original_size > 0 else 0
            data = decompressed
        except:
            pass
        
        # Check if it's JSON
        try:
            json.loads(data.decode('utf-8'))
            format_type = SaveFileFormat.JSON_COMPRESSED if compression_ratio > 0 else SaveFileFormat.JSON
        except:
            format_type = SaveFileFormat.BINARY_COMPRESSED if compression_ratio > 0 else SaveFileFormat.BINARY
        
        return {
            'format': format_type,
            'compression_ratio': compression_ratio,
            'original_size': original_size,
            'decompressed_size': len(data)
        }
    
    def _analyze_structure(self, save_data: SaveGameData, level: AnalysisLevel) -> Dict[str, Any]:
        """Analyze save file structure and generate statistics."""
        stats = {
            'total_size_estimate': 0,
            'civilization_count': len(save_data.civilizations),
            'advisor_count': len(save_data.game_state.advisors),
            'memory_bank_count': len(save_data.memory_banks),
            'total_memories': 0,
            'game_turn': save_data.game_state.turn_state.turn_number
        }
        
        # Count memories
        for memory_bank in save_data.memory_banks.values():
            for advisor_memory in memory_bank.advisor_memories.values():
                stats['total_memories'] += len(advisor_memory.memories)
            stats['total_memories'] += len(memory_bank.shared_memories)
        
        if level in [AnalysisLevel.DETAILED, AnalysisLevel.COMPREHENSIVE]:
            # Detailed structure analysis
            stats['advisor_details'] = {}
            for advisor in save_data.game_state.advisors:
                stats['advisor_details'][advisor.advisor_id] = {
                    'name': advisor.name,
                    'role': advisor.role,
                    'loyalty': advisor.loyalty,
                    'influence': advisor.influence,
                    'relationship_count': len(advisor.relationships)
                }
            
            # Memory analysis by civilization
            stats['memory_details'] = {}
            for civ_id, memory_bank in save_data.memory_banks.items():
                stats['memory_details'][civ_id] = {
                    'advisor_memory_count': len(memory_bank.advisor_memories),
                    'shared_memory_count': len(memory_bank.shared_memories),
                    'total_advisor_memories': sum(len(am.memories) for am in memory_bank.advisor_memories.values())
                }
        
        return stats
    
    def _detect_warnings(self, save_data: SaveGameData) -> List[str]:
        """Detect potential issues that aren't critical errors."""
        warnings = []
        
        # Check for suspicious values
        for advisor in save_data.game_state.advisors:
            if advisor.loyalty < 0.1:
                warnings.append(f"Very low loyalty for advisor {advisor.name}: {advisor.loyalty:.2f}")
            
            if advisor.stress_level > 0.9:
                warnings.append(f"Very high stress for advisor {advisor.name}: {advisor.stress_level:.2f}")
        
        # Check for old memories
        current_turn = save_data.game_state.turn_state.turn_number
        old_memory_threshold = current_turn - 100  # Memories older than 100 turns
        
        for civ_id, memory_bank in save_data.memory_banks.items():
            for advisor_id, advisor_memory in memory_bank.advisor_memories.items():
                old_memories = [m for m in advisor_memory.memories if m.created_turn < old_memory_threshold]
                if len(old_memories) > 50:
                    warnings.append(f"Advisor {advisor_id} has {len(old_memories)} very old memories")
        
        # Check file size concerns
        estimated_size = len(json.dumps(save_data.to_dict(), default=str))
        if estimated_size > 10 * 1024 * 1024:  # 10MB
            warnings.append(f"Save file is very large: {estimated_size / 1024 / 1024:.1f}MB")
        
        return warnings
    
    def _estimate_memory_usage(self, save_data: SaveGameData) -> float:
        """Estimate memory usage of save data in MB."""
        # Rough estimation based on JSON size
        json_size = len(json.dumps(save_data.to_dict(), default=str))
        return json_size / 1024 / 1024
    
    def _find_differences(self, dict_a: Dict, dict_b: Dict, path: str = "") -> List[Dict[str, Any]]:
        """Find differences between two dictionaries."""
        differences = []
        
        # Check for added/removed keys
        keys_a = set(dict_a.keys()) if isinstance(dict_a, dict) else set()
        keys_b = set(dict_b.keys()) if isinstance(dict_b, dict) else set()
        
        for key in keys_a - keys_b:
            differences.append({
                'type': 'removed',
                'path': f"{path}.{key}" if path else key,
                'value_a': dict_a[key],
                'value_b': None
            })
        
        for key in keys_b - keys_a:
            differences.append({
                'type': 'added',
                'path': f"{path}.{key}" if path else key,
                'value_a': None,
                'value_b': dict_b[key]
            })
        
        # Check for modified values
        for key in keys_a & keys_b:
            current_path = f"{path}.{key}" if path else key
            value_a = dict_a[key]
            value_b = dict_b[key]
            
            if isinstance(value_a, dict) and isinstance(value_b, dict):
                differences.extend(self._find_differences(value_a, value_b, current_path))
            elif value_a != value_b:
                differences.append({
                    'type': 'modified',
                    'path': current_path,
                    'value_a': value_a,
                    'value_b': value_b
                })
        
        return differences
    
    def _calculate_similarity(self, dict_a: Dict, dict_b: Dict) -> float:
        """Calculate similarity score between two dictionaries."""
        # Convert to flat key-value pairs
        flat_a = self._flatten_dict(dict_a)
        flat_b = self._flatten_dict(dict_b)
        
        all_keys = set(flat_a.keys()) | set(flat_b.keys())
        if not all_keys:
            return 1.0
        
        matching_keys = 0
        for key in all_keys:
            if key in flat_a and key in flat_b and flat_a[key] == flat_b[key]:
                matching_keys += 1
        
        return matching_keys / len(all_keys)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _compare_metadata(self, meta_a: SaveGameMetadata, meta_b: SaveGameMetadata) -> Dict[str, Any]:
        """Compare two metadata objects."""
        changes = {}
        
        for field in ['game_turn', 'civilization_count', 'advisor_count', 'memory_count']:
            value_a = getattr(meta_a, field)
            value_b = getattr(meta_b, field)
            if value_a != value_b:
                changes[field] = {'from': value_a, 'to': value_b}
        
        # Time difference
        time_diff = meta_b.timestamp - meta_a.timestamp
        changes['time_difference'] = time_diff.total_seconds()
        
        return changes
    
    def _compare_structures(self, dict_a: Dict, dict_b: Dict) -> Dict[str, Any]:
        """Compare the structures of two save files."""
        changes = {}
        
        # Compare top-level structure
        keys_a = set(dict_a.keys())
        keys_b = set(dict_b.keys())
        
        changes['added_sections'] = list(keys_b - keys_a)
        changes['removed_sections'] = list(keys_a - keys_b)
        
        # Compare sizes of major sections
        for section in keys_a & keys_b:
            if isinstance(dict_a[section], (list, dict)):
                size_a = len(dict_a[section])
                size_b = len(dict_b[section])
                if size_a != size_b:
                    changes[f'{section}_size_change'] = {'from': size_a, 'to': size_b}
        
        return changes
    
    def _attempt_repairs(self, save_data: SaveGameData) -> SaveGameData:
        """Attempt to repair corrupted save data."""
        # This is a simplified repair implementation
        # In a real implementation, this would be much more sophisticated
        
        # Ensure basic structure integrity
        if not save_data.metadata:
            # Create minimal metadata
            save_data.metadata = SaveGameMetadata(
                save_id="repaired",
                game_name="Repaired Save",
                timestamp=datetime.now(),
                version=SaveFileVersion.CURRENT,
                format=SaveFileFormat.JSON,
                compression_level=6,
                game_turn=0,
                civilization_count=0,
                advisor_count=0,
                memory_count=0,
                file_size=0,
                checksum=""
            )
        
        # Ensure game state exists
        if not save_data.game_state:
            from src.bridge import GameState, TurnState
            save_data.game_state = GameState(
                turn_state=TurnState(turn_number=0, civilization_id="repaired", phase="planning"),
                civilizations=[],
                advisors=[],
                global_events=[],
                metadata={}
            )
        
        # Ensure memory banks exist
        if not save_data.memory_banks:
            save_data.memory_banks = {}
        
        return save_data
    
    def _reconstruct_save_data(self, save_dict: Dict[str, Any]) -> SaveGameData:
        """Reconstruct SaveGameData from dictionary with error tolerance."""
        # This is a simplified reconstruction
        # In practice, this would handle many more edge cases
        
        try:
            metadata = SaveGameMetadata.from_dict(save_dict.get('metadata', {}))
        except:
            metadata = SaveGameMetadata(
                save_id="unknown",
                game_name="Reconstructed Save",
                timestamp=datetime.now(),
                version=SaveFileVersion.CURRENT,
                format=SaveFileFormat.JSON,
                compression_level=6,
                game_turn=0,
                civilization_count=0,
                advisor_count=0,
                memory_count=0,
                file_size=0,
                checksum=""
            )
        
        # Reconstruct other components with defaults
        from src.bridge import GameState, TurnState
        
        try:
            game_state_dict = save_dict.get('game_state', {})
            turn_state = TurnState(**game_state_dict.get('turn_state', {
                'turn_number': 0, 'civilization_id': 'unknown', 'phase': 'planning'
            }))
            game_state = GameState(
                turn_state=turn_state,
                civilizations=[],
                advisors=[],
                global_events=[],
                metadata={}
            )
        except:
            game_state = GameState(
                turn_state=TurnState(turn_number=0, civilization_id="reconstructed", phase="planning"),
                civilizations=[],
                advisors=[],
                global_events=[],
                metadata={}
            )
        
        return SaveGameData(
            metadata=metadata,
            game_state=game_state,
            memory_banks=save_dict.get('memory_banks', {}),
            civilizations=save_dict.get('civilizations', {}),
            custom_data=save_dict.get('custom_data', {})
        )
    
    def _generate_html_report(self, analysis: SaveFileAnalysis) -> str:
        """Generate HTML report from analysis results."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Save File Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        .success {{ color: green; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Save File Analysis Report</h1>
        <p><strong>File:</strong> {analysis.file_path}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>File Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>File Size</td><td>{analysis.file_size:,} bytes</td></tr>
            <tr><td>Format</td><td>{analysis.format.value}</td></tr>
            <tr><td>Version</td><td>{analysis.version.value}</td></tr>
            <tr><td>Compression Ratio</td><td>{analysis.compression_ratio:.1%}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Game Information</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Game Name</td><td>{analysis.metadata.game_name}</td></tr>
            <tr><td>Game Turn</td><td>{analysis.metadata.game_turn}</td></tr>
            <tr><td>Civilizations</td><td>{analysis.metadata.civilization_count}</td></tr>
            <tr><td>Advisors</td><td>{analysis.metadata.advisor_count}</td></tr>
            <tr><td>Memories</td><td>{analysis.metadata.memory_count}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Performance Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Load Time</td><td>{analysis.performance_metrics.get('load_time_seconds', 0):.3f} seconds</td></tr>
            <tr><td>Memory Usage</td><td>{analysis.performance_metrics.get('memory_usage_mb', 0):.2f} MB</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Validation Results</h2>
        {"<p class='success'>No validation errors found!</p>" if not analysis.validation_errors else ""}
        {self._format_issues_html(analysis.validation_errors, "error")}
        {self._format_issues_html(analysis.warnings, "warning")}
    </div>
    
</body>
</html>
        """
        return html
    
    def _format_issues_html(self, issues: List[str], issue_type: str) -> str:
        """Format issues list as HTML."""
        if not issues:
            return ""
        
        html = f"<h3>{issue_type.title()}s ({len(issues)})</h3><ul>"
        for issue in issues:
            html += f'<li class="{issue_type}">{issue}</li>'
        html += "</ul>"
        return html


# CLI Interface for debugging tools
def main():
    """Command-line interface for save file debugging tools."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Save File Debugging Tools")
    parser.add_argument("command", choices=["analyze", "compare", "repair", "extract", "report"])
    parser.add_argument("save_file", help="Path to save file")
    parser.add_argument("--second-file", help="Second save file for comparison")
    parser.add_argument("--output", help="Output path for results")
    parser.add_argument("--level", choices=["basic", "detailed", "comprehensive"], 
                       default="detailed", help="Analysis level")
    
    args = parser.parse_args()
    
    debugger = SaveFileDebugger()
    
    try:
        if args.command == "analyze":
            analysis = debugger.analyze_save_file(Path(args.save_file), AnalysisLevel(args.level))
            print(json.dumps(analysis.to_dict(), indent=2, default=str))
        
        elif args.command == "compare":
            if not args.second_file:
                print("Error: --second-file required for comparison")
                sys.exit(1)
            comparison = debugger.compare_save_files(Path(args.save_file), Path(args.second_file))
            print(json.dumps(comparison.to_dict(), indent=2, default=str))
        
        elif args.command == "repair":
            if not args.output:
                args.output = args.save_file + ".repaired"
            success = debugger.repair_save_file(Path(args.save_file), Path(args.output))
            print(f"Repair {'successful' if success else 'failed'}")
        
        elif args.command == "extract":
            if not args.output:
                args.output = args.save_file + "_extracted"
            success = debugger.extract_save_data(Path(args.save_file), Path(args.output))
            print(f"Extraction {'successful' if success else 'failed'}")
        
        elif args.command == "report":
            if not args.output:
                args.output = args.save_file + "_report.html"
            success = debugger.generate_save_report(Path(args.save_file), Path(args.output))
            print(f"Report generation {'successful' if success else 'failed'}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
