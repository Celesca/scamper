#!/usr/bin/env python3
"""
WATCHTOWER API - Real-time WebSocket API for Watchtower Dashboard
==================================================================
Provides REST endpoints and WebSocket events for the frontend dashboard.
"""

import threading
import time
import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit

# Import from watchtower
from watchtower import (
    DomainFuzzer, TargetConfig, PermutationDatabase, 
    Detection, LiveStats, Watchtower
)

# Create Blueprint for API routes
watchtower_bp = Blueprint('watchtower', __name__, url_prefix='/api/watchtower')

# Global state
_watchtower_instance: Optional['WatchtowerService'] = None
_socketio: Optional[SocketIO] = None


class WatchtowerService:
    """
    Service wrapper for Watchtower that integrates with Flask-SocketIO.
    Runs monitoring in a background thread and emits events to connected clients.
    """
    
    def __init__(self, socketio: SocketIO, output_file: str = "detections.csv"):
        self.socketio = socketio
        self.config = TargetConfig()
        self.db = PermutationDatabase(self.config)
        self.stats = WatchtowerStats()
        self.output_file = output_file
        self.detections: List[Detection] = []
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Load existing detections from CSV
        self._load_existing_detections()
    
    def _load_existing_detections(self):
        """Load existing detections from CSV file."""
        if not os.path.exists(self.output_file):
            return
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('domain'):
                        detection = Detection(
                            domain=row.get('domain', ''),
                            target=row.get('target', ''),
                            fuzzer_type=row.get('fuzzer_type', ''),
                            risk_score=int(row.get('risk_score', 0)),
                            risk_factors=row.get('risk_factors', '').split('; '),
                            detection_time=row.get('timestamp', ''),
                            certificate_issuer=row.get('issuer', '')
                        )
                        self.detections.append(detection)
                        self.stats.record_detection(detection)
        except Exception as e:
            print(f"Error loading detections: {e}")
    
    def start(self):
        """Start the monitoring service in a background thread."""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        self.stats.start_time = datetime.now()
        
        self._thread = threading.Thread(target=self._run_monitor, daemon=True)
        self._thread.start()
        
        return {"status": "started"}
    
    def stop(self):
        """Stop the monitoring service."""
        self.is_running = False
        return {"status": "stopped"}
    
    def _run_monitor(self):
        """Run the CT log monitor (called in background thread)."""
        import certstream
        
        try:
            certstream.listen_for_events(
                self._on_cert_event,
                url='wss://certstream.calidog.io/'
            )
        except Exception as e:
            self.socketio.emit('watchtower_error', {'error': str(e)})
            self.is_running = False
    
    def _on_cert_event(self, message: dict, context):
        """Handle incoming certificate events."""
        if not self.is_running:
            return
        
        if message.get('message_type') == 'heartbeat':
            return
        
        if message.get('message_type') != 'certificate_update':
            return
        
        self.stats.record_cert()
        
        try:
            cert_data = message.get('data', {})
            leaf_cert = cert_data.get('leaf_cert', {})
            all_domains = leaf_cert.get('all_domains', [])
            
            for domain in all_domains:
                self.stats.record_domain()
                
                # Skip wildcards
                if domain.startswith('*.'):
                    domain = domain[2:]
                
                # Analyze domain
                detection = self._analyze_domain(domain, cert_data)
                
                if detection:
                    with self._lock:
                        self.detections.append(detection)
                        self.stats.record_detection(detection)
                    
                    self._save_detection(detection)
                    
                    # Emit to all connected clients
                    self.socketio.emit('new_detection', detection.to_dict())
            
            # Emit stats update every 100 certs
            if self.stats.certs_processed % 100 == 0:
                self.socketio.emit('stats_update', self.stats.to_dict())
                
        except Exception as e:
            print(f"Error processing cert: {e}")
    
    def _is_whitelisted(self, domain: str) -> bool:
        """Check if domain is whitelisted."""
        domain_lower = domain.lower()
        for safe in self.config.whitelist:
            if domain_lower == safe or domain_lower.endswith('.' + safe):
                return True
        return False
    
    def _analyze_domain(self, domain: str, cert_data: dict) -> Optional[Detection]:
        """Analyze a domain for phishing indicators."""
        if self._is_whitelisted(domain):
            return None
        
        # Check exact keyword match
        target = self.db.contains_target_keyword(domain)
        fuzzer_type = "keyword-match"
        
        if not target:
            # Check fuzzer database
            result = self.db.lookup(domain)
            if not result:
                return None
            target, fuzzer_type = result
        
        # Calculate risk score
        score, factors = self._calculate_risk(domain, target, fuzzer_type)
        if target and fuzzer_type == "keyword-match":
            factors.insert(0, f"Contains target keyword: {target}")
            score = min(score + 20, 100)
        
        # Extract certificate info
        issuer = ""
        try:
            issuer = cert_data.get('leaf_cert', {}).get('issuer', {}).get('O', '')
        except:
            pass
        
        return Detection(
            domain=domain,
            target=target,
            fuzzer_type=fuzzer_type,
            risk_score=score,
            risk_factors=factors,
            detection_time=datetime.now().isoformat(),
            certificate_issuer=issuer,
            all_domains=cert_data.get('leaf_cert', {}).get('all_domains', [])
        )
    
    def _calculate_risk(self, domain: str, target: str, fuzzer_type: str):
        """Calculate risk score and factors."""
        score = 0
        factors = []
        domain_lower = domain.lower()
        
        # Base score from detection type
        if fuzzer_type in ['homoglyph', 'bitsquatting']:
            score += 40
            factors.append(f"High-risk fuzzer: {fuzzer_type}")
        elif fuzzer_type in ['addition', 'hyphenation']:
            score += 30
            factors.append(f"Medium-risk fuzzer: {fuzzer_type}")
        else:
            score += 25
            factors.append(f"Typosquatting: {fuzzer_type}")
        
        # TLD analysis
        for tld in self.config.suspicious_tlds:
            if domain_lower.endswith(tld):
                score += 25
                factors.append(f"Suspicious TLD: {tld}")
                break
        
        # Multiple hyphens
        if domain_lower.count('-') >= 2:
            score += 15
            factors.append("Multiple hyphens in domain")
        
        # Long domain
        if len(domain_lower) > 30:
            score += 10
            factors.append("Unusually long domain")
        
        # Security keywords
        security_words = ['secure', 'verify', 'login', 'update', 'confirm', 'auth']
        for word in security_words:
            if word in domain_lower:
                score += 15
                factors.append(f"Security keyword: {word}")
                break
        
        return min(score, 100), factors
    
    def _save_detection(self, detection: Detection):
        """Save detection to CSV file."""
        try:
            file_exists = os.path.exists(self.output_file)
            with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'domain', 'target', 'fuzzer_type', 
                                   'risk_score', 'risk_factors', 'issuer'])
                writer.writerow([
                    detection.detection_time,
                    detection.domain,
                    detection.target,
                    detection.fuzzer_type,
                    detection.risk_score,
                    '; '.join(detection.risk_factors),
                    detection.certificate_issuer
                ])
        except Exception as e:
            print(f"Error saving detection: {e}")
    
    def get_status(self) -> dict:
        """Get current status."""
        return {
            "is_running": self.is_running,
            "stats": self.stats.to_dict(),
            "targets_count": len(self.db.targets_generated),
            "permutations_count": len(self.db.permutations)
        }
    
    def get_detections(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get paginated detections."""
        with self._lock:
            sorted_detections = sorted(
                self.detections, 
                key=lambda d: d.detection_time, 
                reverse=True
            )
            return [d.to_dict() for d in sorted_detections[offset:offset+limit]]
    
    def get_stats(self) -> dict:
        """Get aggregated statistics."""
        return self.stats.to_dict()


class WatchtowerStats:
    """Statistics tracker for Watchtower."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.certs_processed = 0
        self.domains_checked = 0
        self.detections_count = 0
        self.high_risk_count = 0
        self.by_target: Dict[str, int] = defaultdict(int)
        self.by_fuzzer: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_cert(self):
        with self._lock:
            self.certs_processed += 1
    
    def record_domain(self):
        with self._lock:
            self.domains_checked += 1
    
    def record_detection(self, detection: Detection):
        with self._lock:
            self.detections_count += 1
            if detection.risk_score >= 70:
                self.high_risk_count += 1
            self.by_target[detection.target] += 1
            self.by_fuzzer[detection.fuzzer_type] += 1
    
    def to_dict(self) -> dict:
        runtime = (datetime.now() - self.start_time).total_seconds()
        return {
            "runtime_seconds": runtime,
            "certs_processed": self.certs_processed,
            "domains_checked": self.domains_checked,
            "detections_count": self.detections_count,
            "high_risk_count": self.high_risk_count,
            "processing_rate": self.certs_processed / max(runtime, 1),
            "by_target": dict(self.by_target),
            "by_fuzzer": dict(self.by_fuzzer)
        }


def init_watchtower_api(socketio: SocketIO):
    """Initialize the Watchtower API with SocketIO instance."""
    global _watchtower_instance, _socketio
    _socketio = socketio
    _watchtower_instance = WatchtowerService(socketio)
    return _watchtower_instance


def get_watchtower_service() -> Optional[WatchtowerService]:
    """Get the Watchtower service instance."""
    return _watchtower_instance


# ============================================================================
# REST API ROUTES
# ============================================================================

@watchtower_bp.route('/status', methods=['GET'])
def get_status():
    """Get Watchtower status."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    return jsonify(service.get_status())


@watchtower_bp.route('/start', methods=['POST'])
def start_monitoring():
    """Start Watchtower monitoring."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    result = service.start()
    return jsonify(result)


@watchtower_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """Stop Watchtower monitoring."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    result = service.stop()
    return jsonify(result)


@watchtower_bp.route('/detections', methods=['GET'])
def get_detections():
    """Get recent detections."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    detections = service.get_detections(limit, offset)
    return jsonify({
        "detections": detections,
        "total": service.stats.detections_count
    })


@watchtower_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get aggregated statistics."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    return jsonify(service.get_stats())


@watchtower_bp.route('/targets', methods=['GET'])
def get_targets():
    """Get list of monitored targets."""
    service = get_watchtower_service()
    if not service:
        return jsonify({"error": "Service not initialized"}), 500
    
    config = service.config
    return jsonify({
        "thai_banks": config.thai_banks,
        "thai_gov": config.thai_gov,
        "thai_ewallet": config.thai_ewallet,
        "total_targets": len(config.get_all_targets()),
        "total_permutations": len(service.db.permutations)
    })
