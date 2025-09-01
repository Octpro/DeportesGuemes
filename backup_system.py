"""
Backup and Recovery System for Deportes Güemes Desktop Application
Provides automated backup scheduling, integrity checking, and restore functionality
"""

import json
import os
import shutil
import hashlib
import gzip
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
try:
    from git import Repo
except ImportError:
    print("GitPython not available - Git integration disabled")
    Repo = None


class BackupSystem:
    def __init__(self, data_directory="html/JS", backup_directory="backups"):
        self.data_directory = Path(data_directory)
        self.backup_directory = Path(backup_directory)
        self.config_file = self.backup_directory / "backup_config.json"
        
        # Default configuration
        self.config = {
            "interval_hours": 24,
            "max_backups": 30,
            "compression_enabled": True,
            "incremental_enabled": True,
            "auto_backup_enabled": True
        }
        
        # Files to backup
        self.backup_files = [
            "productos.json",
            "historial.json"
        ]
        
        # Additional directories to backup
        self.backup_directories = [
            "../img"  # Product images
        ]
        
        self.backup_thread = None
        self.stop_backup_thread = False
        
        self.init_backup_system()

    def init_backup_system(self):
        """Initialize the backup system"""
        try:
            # Create backup directory if it doesn't exist
            self.backup_directory.mkdir(parents=True, exist_ok=True)
            
            # Load configuration
            self.load_config()
            
            # Start automatic backup thread if enabled
            if self.config.get("auto_backup_enabled", True):
                self.start_backup_thread()
                
            print("Backup system initialized successfully")
        except Exception as e:
            print(f"Failed to initialize backup system: {e}")

    def load_config(self):
        """Load backup configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception as e:
            print(f"Failed to load backup config: {e}")

    def save_config(self):
        """Save backup configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save backup config: {e}")

    def update_config(self, new_config):
        """Update backup configuration"""
        self.config.update(new_config)
        self.save_config()
        
        # Restart backup thread if auto backup settings changed
        if "auto_backup_enabled" in new_config or "interval_hours" in new_config:
            self.restart_backup_thread()

    def generate_backup_id(self):
        """Generate unique backup ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}"

    def calculate_checksum(self, data):
        """Calculate MD5 checksum for data integrity"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.md5(data).hexdigest()

    def compress_data(self, data):
        """Compress data using gzip"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            
            compressed = gzip.compress(data.encode('utf-8'))
            return compressed
        except Exception as e:
            print(f"Compression failed: {e}")
            return data

    def decompress_data(self, compressed_data):
        """Decompress gzip data"""
        try:
            if isinstance(compressed_data, bytes):
                decompressed = gzip.decompress(compressed_data)
                return decompressed.decode('utf-8')
            return compressed_data
        except Exception as e:
            print(f"Decompression failed: {e}")
            return compressed_data

    def gather_backup_data(self):
        """Gather all data that needs to be backed up"""
        backup_data = {
            "files": {},
            "directories": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "system_info": {
                    "os": os.name,
                    "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}"
                }
            }
        }

        # Backup JSON files
        for filename in self.backup_files:
            file_path = self.data_directory / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        backup_data["files"][filename] = json.load(f)
                except Exception as e:
                    print(f"Failed to backup {filename}: {e}")
                    backup_data["files"][filename] = None

        # Backup image directory structure (metadata only, not actual images)
        for dir_name in self.backup_directories:
            dir_path = self.data_directory / dir_name
            if dir_path.exists():
                try:
                    backup_data["directories"][dir_name] = self.get_directory_structure(dir_path)
                except Exception as e:
                    print(f"Failed to backup directory {dir_name}: {e}")
                    backup_data["directories"][dir_name] = {}

        return backup_data

    def get_directory_structure(self, directory):
        """Get directory structure with file metadata"""
        structure = {}
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    stat = item.stat()
                    structure[item.name] = {
                        "type": "file",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "checksum": self.calculate_file_checksum(item)
                    }
                elif item.is_dir():
                    structure[item.name] = {
                        "type": "directory",
                        "contents": self.get_directory_structure(item)
                    }
        except Exception as e:
            print(f"Error reading directory structure: {e}")
        
        return structure

    def calculate_file_checksum(self, file_path):
        """Calculate checksum for a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Failed to calculate checksum for {file_path}: {e}")
            return None

    def detect_changes(self, old_data, new_data):
        """Detect changes between two data sets"""
        changes = {}
        
        # Compare files
        if old_data.get("files") != new_data.get("files"):
            changes["files"] = {}
            for filename, content in new_data.get("files", {}).items():
                if old_data.get("files", {}).get(filename) != content:
                    changes["files"][filename] = content
        
        # Compare directories
        if old_data.get("directories") != new_data.get("directories"):
            changes["directories"] = new_data.get("directories", {})
        
        return changes

    def create_full_backup(self):
        """Create a full backup of all system data"""
        try:
            backup_id = self.generate_backup_id()
            backup_data = self.gather_backup_data()
            
            backup_info = {
                "id": backup_id,
                "timestamp": datetime.now().isoformat(),
                "type": "full",
                "version": "1.0",
                "checksum": self.calculate_checksum(backup_data),
                "compressed": self.config.get("compression_enabled", True),
                "size": len(json.dumps(backup_data))
            }

            # Save backup data
            backup_file = self.backup_directory / f"{backup_id}.json"
            
            if backup_info["compressed"]:
                compressed_data = self.compress_data(backup_data)
                with open(backup_file, 'wb') as f:
                    f.write(compressed_data)
            else:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)

            # Save backup info
            info_file = self.backup_directory / f"{backup_id}_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)

            print(f"Full backup created: {backup_id}")
            self.cleanup_old_backups()
            return backup_info

        except Exception as e:
            print(f"Failed to create full backup: {e}")
            raise

    def create_incremental_backup(self):
        """Create an incremental backup (only changed data)"""
        try:
            last_backup = self.get_last_backup()
            if not last_backup:
                return self.create_full_backup()

            current_data = self.gather_backup_data()
            last_backup_data = self.load_backup_data(last_backup["id"])
            
            changes = self.detect_changes(last_backup_data, current_data)
            
            if not any(changes.values()):
                print("No changes detected, skipping incremental backup")
                return None

            backup_id = self.generate_backup_id()
            
            backup_info = {
                "id": backup_id,
                "timestamp": datetime.now().isoformat(),
                "type": "incremental",
                "version": "1.0",
                "base_backup_id": last_backup["id"],
                "checksum": self.calculate_checksum(changes),
                "compressed": self.config.get("compression_enabled", True),
                "size": len(json.dumps(changes))
            }

            # Save incremental backup data
            backup_file = self.backup_directory / f"{backup_id}.json"
            
            if backup_info["compressed"]:
                compressed_data = self.compress_data(changes)
                with open(backup_file, 'wb') as f:
                    f.write(compressed_data)
            else:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(changes, f, indent=2, ensure_ascii=False)

            # Save backup info
            info_file = self.backup_directory / f"{backup_id}_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)

            print(f"Incremental backup created: {backup_id}")
            self.cleanup_old_backups()
            return backup_info

        except Exception as e:
            print(f"Failed to create incremental backup: {e}")
            raise

    def load_backup_data(self, backup_id):
        """Load backup data from file"""
        try:
            backup_file = self.backup_directory / f"{backup_id}.json"
            info_file = self.backup_directory / f"{backup_id}_info.json"
            
            if not backup_file.exists() or not info_file.exists():
                raise FileNotFoundError(f"Backup {backup_id} not found")

            # Load backup info
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)

            # Load backup data
            if backup_info.get("compressed", False):
                with open(backup_file, 'rb') as f:
                    compressed_data = f.read()
                    decompressed = self.decompress_data(compressed_data)
                    backup_data = json.loads(decompressed)
            else:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)

            return backup_data

        except Exception as e:
            print(f"Failed to load backup data: {e}")
            raise

    def get_all_backups(self):
        """Get list of all available backups"""
        backups = []
        
        try:
            for info_file in self.backup_directory.glob("*_info.json"):
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                        backups.append(backup_info)
                except Exception as e:
                    print(f"Failed to read backup info {info_file}: {e}")
        except Exception as e:
            print(f"Failed to list backups: {e}")

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups

    def get_last_backup(self):
        """Get the most recent backup"""
        backups = self.get_all_backups()
        return backups[0] if backups else None

    def verify_backup_integrity(self, backup_id):
        """Verify backup integrity using checksum"""
        try:
            backup_data = self.load_backup_data(backup_id)
            info_file = self.backup_directory / f"{backup_id}_info.json"
            
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)

            calculated_checksum = self.calculate_checksum(backup_data)
            stored_checksum = backup_info.get("checksum")

            return calculated_checksum == stored_checksum

        except Exception as e:
            print(f"Integrity verification failed for {backup_id}: {e}")
            return False

    def restore_from_backup(self, backup_id, preview=False):
        """Restore from a specific backup"""
        try:
            # Verify backup integrity
            if not self.verify_backup_integrity(backup_id):
                raise ValueError(f"Backup {backup_id} failed integrity check")

            backup_data = self.load_backup_data(backup_id)
            info_file = self.backup_directory / f"{backup_id}_info.json"
            
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)

            # If incremental backup, reconstruct full data
            if backup_info.get("type") == "incremental":
                backup_data = self.reconstruct_from_incremental(backup_id)

            if preview:
                return {
                    "success": True,
                    "data": backup_data,
                    "backup_info": backup_info,
                    "preview": True
                }

            # Perform actual restore
            self.perform_restore(backup_data)
            
            return {
                "success": True,
                "message": f"Successfully restored from backup {backup_id}",
                "timestamp": backup_info["timestamp"]
            }

        except Exception as e:
            print(f"Restore failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def reconstruct_from_incremental(self, incremental_backup_id):
        """Reconstruct full data from incremental backup"""
        info_file = self.backup_directory / f"{incremental_backup_id}_info.json"
        
        with open(info_file, 'r', encoding='utf-8') as f:
            incremental_info = json.load(f)

        base_backup_id = incremental_info.get("base_backup_id")
        if not base_backup_id:
            raise ValueError("Base backup ID not found for incremental backup")

        base_data = self.load_backup_data(base_backup_id)
        incremental_data = self.load_backup_data(incremental_backup_id)

        # Merge incremental changes with base data
        merged_data = base_data.copy()
        
        if "files" in incremental_data:
            if "files" not in merged_data:
                merged_data["files"] = {}
            merged_data["files"].update(incremental_data["files"])
        
        if "directories" in incremental_data:
            merged_data["directories"] = incremental_data["directories"]

        return merged_data

    def perform_restore(self, restore_data):
        """Perform the actual restore operation with conflict resolution"""
        try:
            # Create backup of current data before restore
            current_backup = self.create_full_backup()
            print(f"Current data backed up as: {current_backup['id']}")

            # Check for conflicts before restore
            conflicts = self.detect_restore_conflicts(restore_data)
            if conflicts:
                print(f"Detected {len(conflicts)} potential conflicts")
                resolved_data = self.resolve_conflicts(restore_data, conflicts)
            else:
                resolved_data = restore_data

            # Restore JSON files with conflict resolution
            if "files" in resolved_data:
                for filename, content in resolved_data["files"].items():
                    if content is not None:
                        file_path = self.data_directory / filename
                        
                        # Create atomic write operation
                        temp_file = file_path.with_suffix('.tmp')
                        try:
                            with open(temp_file, 'w', encoding='utf-8') as f:
                                json.dump(content, f, indent=2, ensure_ascii=False)
                            
                            # Atomic move
                            temp_file.replace(file_path)
                            print(f"Restored {filename}")
                        except Exception as e:
                            if temp_file.exists():
                                temp_file.unlink()
                            raise e

            # Update Git repository if available
            self.update_git_after_restore()
            
            print("Restore completed successfully")

        except Exception as e:
            print(f"Restore operation failed: {e}")
            raise

    def detect_restore_conflicts(self, restore_data):
        """Detect potential conflicts during restore"""
        conflicts = []
        
        try:
            if "files" in restore_data:
                for filename, restore_content in restore_data["files"].items():
                    file_path = self.data_directory / filename
                    
                    if file_path.exists():
                        # Load current file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            current_content = json.load(f)
                        
                        # Compare timestamps and detect conflicts
                        if self.has_content_conflicts(current_content, restore_content, filename):
                            conflicts.append({
                                "file": filename,
                                "type": "content_conflict",
                                "current": current_content,
                                "restore": restore_content
                            })
        except Exception as e:
            print(f"Error detecting conflicts: {e}")
        
        return conflicts

    def has_content_conflicts(self, current_content, restore_content, filename):
        """Check if there are content conflicts between current and restore data"""
        if filename == "productos.json":
            return self.detect_product_conflicts(current_content, restore_content)
        elif filename == "historial.json":
            return self.detect_history_conflicts(current_content, restore_content)
        
        # Generic conflict detection
        return json.dumps(current_content, sort_keys=True) != json.dumps(restore_content, sort_keys=True)

    def detect_product_conflicts(self, current_products, restore_products):
        """Detect conflicts in product data"""
        if not isinstance(current_products, list) or not isinstance(restore_products, list):
            return True
        
        # Create lookup dictionaries
        current_dict = {p.get("id", ""): p for p in current_products if isinstance(p, dict)}
        restore_dict = {p.get("id", ""): p for p in restore_products if isinstance(p, dict)}
        
        # Check for conflicts in common products
        for product_id in set(current_dict.keys()) & set(restore_dict.keys()):
            current_product = current_dict[product_id]
            restore_product = restore_dict[product_id]
            
            # Check if products have different content (excluding timestamps)
            current_clean = {k: v for k, v in current_product.items() if k not in ['last_modified', 'updated_at']}
            restore_clean = {k: v for k, v in restore_product.items() if k not in ['last_modified', 'updated_at']}
            
            if current_clean != restore_clean:
                return True
        
        return False

    def detect_history_conflicts(self, current_history, restore_history):
        """Detect conflicts in history data"""
        if not isinstance(current_history, list) or not isinstance(restore_history, list):
            return True
        
        # History conflicts are less critical - we can usually merge them
        return len(current_history) > len(restore_history)

    def resolve_conflicts(self, restore_data, conflicts):
        """Resolve conflicts using various strategies"""
        resolved_data = restore_data.copy()
        
        for conflict in conflicts:
            filename = conflict["file"]
            conflict_type = conflict["type"]
            
            if conflict_type == "content_conflict":
                if filename == "productos.json":
                    resolved_content = self.resolve_product_conflicts(
                        conflict["current"], 
                        conflict["restore"]
                    )
                elif filename == "historial.json":
                    resolved_content = self.resolve_history_conflicts(
                        conflict["current"], 
                        conflict["restore"]
                    )
                else:
                    # Default: prefer restore data but log the conflict
                    resolved_content = conflict["restore"]
                    print(f"Conflict in {filename}: Using restore data")
                
                resolved_data["files"][filename] = resolved_content
        
        return resolved_data

    def resolve_product_conflicts(self, current_products, restore_products):
        """Resolve product conflicts by merging data intelligently"""
        if not isinstance(current_products, list):
            current_products = []
        if not isinstance(restore_products, list):
            restore_products = []
        
        # Create lookup dictionaries
        current_dict = {p.get("id", ""): p for p in current_products if isinstance(p, dict)}
        restore_dict = {p.get("id", ""): p for p in restore_products if isinstance(p, dict)}
        
        merged_products = []
        processed_ids = set()
        
        # Process products from restore data first
        for product in restore_products:
            if not isinstance(product, dict):
                continue
                
            product_id = product.get("id", "")
            if not product_id:
                continue
            
            processed_ids.add(product_id)
            
            if product_id in current_dict:
                # Merge conflicting products
                current_product = current_dict[product_id]
                merged_product = self.merge_product_data(current_product, product)
                merged_products.append(merged_product)
                print(f"Merged conflicting product: {product_id}")
            else:
                # Add new product from restore
                merged_products.append(product)
        
        # Add remaining current products that weren't in restore
        for product_id, product in current_dict.items():
            if product_id not in processed_ids:
                merged_products.append(product)
                print(f"Kept current product: {product_id}")
        
        return merged_products

    def merge_product_data(self, current_product, restore_product):
        """Merge two conflicting product records"""
        merged = restore_product.copy()
        
        # Preserve current stock levels (they're more likely to be accurate)
        if "stock" in current_product:
            merged["stock"] = current_product["stock"]
        
        # Preserve current pricing if it's newer
        current_price = current_product.get("precio", "0")
        restore_price = restore_product.get("precio", "0")
        
        try:
            if float(current_price) != float(restore_price):
                # Keep current price and add a note
                merged["precio"] = current_price
                merged["_conflict_note"] = f"Price conflict resolved: kept current {current_price} over restore {restore_price}"
        except (ValueError, TypeError):
            pass
        
        # Add merge timestamp
        merged["_last_merged"] = datetime.now().isoformat()
        
        return merged

    def resolve_history_conflicts(self, current_history, restore_history):
        """Resolve history conflicts by merging entries"""
        if not isinstance(current_history, list):
            current_history = []
        if not isinstance(restore_history, list):
            restore_history = []
        
        # Merge histories by combining unique entries
        merged_history = []
        seen_entries = set()
        
        # Add all entries, avoiding duplicates
        for history_list in [current_history, restore_history]:
            for entry in history_list:
                if isinstance(entry, dict):
                    # Create a signature for the entry
                    entry_sig = f"{entry.get('fecha', '')}-{entry.get('accion', '')}-{entry.get('producto', '')}"
                    if entry_sig not in seen_entries:
                        merged_history.append(entry)
                        seen_entries.add(entry_sig)
        
        # Sort by date
        try:
            merged_history.sort(key=lambda x: x.get('fecha', ''), reverse=True)
        except Exception:
            pass
        
        return merged_history

    def update_git_after_restore(self):
        """Update Git repository after restore operation"""
        try:
            if Repo is None:
                print("Git integration not available")
                return
                
            repo_path = Path.cwd()
            if (repo_path / '.git').exists():
                repo = Repo(repo_path)
                
                # Add changed files
                repo.index.add(['html/JS/productos.json', 'html/JS/historial.json'])
                
                # Commit changes
                commit_message = f"Restore from backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                repo.index.commit(commit_message)
                
                print("Git repository updated after restore")
        except Exception as e:
            print(f"Failed to update Git after restore: {e}")

    def create_scheduled_backup(self):
        """Create a scheduled backup (called by the automatic backup system)"""
        try:
            if self.config.get("incremental_enabled", True):
                return self.create_incremental_backup()
            else:
                return self.create_full_backup()
        except Exception as e:
            print(f"Scheduled backup failed: {e}")
            return None

    def get_backup_health_status(self):
        """Get the health status of the backup system"""
        try:
            backups = self.get_all_backups()
            if not backups:
                return {
                    "status": "warning",
                    "message": "No backups found",
                    "recommendations": ["Create your first backup"]
                }
            
            # Check last backup age
            last_backup = backups[0]
            last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
            hours_since_last = (datetime.now() - last_backup_time).total_seconds() / 3600
            
            max_hours = self.config.get("interval_hours", 24) * 2  # Allow 2x the interval
            
            if hours_since_last > max_hours:
                return {
                    "status": "error",
                    "message": f"Last backup was {int(hours_since_last)} hours ago",
                    "recommendations": ["Create a new backup", "Check automatic backup settings"]
                }
            
            # Check backup integrity
            corrupted_backups = []
            for backup in backups[:5]:  # Check last 5 backups
                if not self.verify_backup_integrity(backup["id"]):
                    corrupted_backups.append(backup["id"])
            
            if corrupted_backups:
                return {
                    "status": "warning",
                    "message": f"{len(corrupted_backups)} corrupted backups found",
                    "recommendations": ["Create a new full backup", "Remove corrupted backups"]
                }
            
            return {
                "status": "healthy",
                "message": "Backup system is working properly",
                "recommendations": []
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "recommendations": ["Check backup system configuration"]
            }

    def cleanup_old_backups(self):
        """Remove old backups to save storage space"""
        try:
            backups = self.get_all_backups()
            max_backups = self.config.get("max_backups", 30)
            
            if len(backups) <= max_backups:
                return

            # Remove oldest backups
            backups_to_remove = backups[max_backups:]
            
            for backup in backups_to_remove:
                backup_id = backup["id"]
                backup_file = self.backup_directory / f"{backup_id}.json"
                info_file = self.backup_directory / f"{backup_id}_info.json"
                
                if backup_file.exists():
                    backup_file.unlink()
                if info_file.exists():
                    info_file.unlink()
                
                print(f"Removed old backup: {backup_id}")

        except Exception as e:
            print(f"Cleanup failed: {e}")

    def export_backup(self, backup_id, export_path):
        """Export backup to external location"""
        try:
            backup_file = self.backup_directory / f"{backup_id}.json"
            info_file = self.backup_directory / f"{backup_id}_info.json"
            
            if not backup_file.exists() or not info_file.exists():
                raise FileNotFoundError(f"Backup {backup_id} not found")

            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy backup files
            shutil.copy2(backup_file, export_dir / f"{backup_id}.json")
            shutil.copy2(info_file, export_dir / f"{backup_id}_info.json")
            
            print(f"Backup {backup_id} exported to {export_path}")
            return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def import_backup(self, import_path):
        """Import backup from external location"""
        try:
            import_dir = Path(import_path)
            
            # Find backup files in import directory
            backup_files = list(import_dir.glob("backup_*_info.json"))
            
            if not backup_files:
                raise FileNotFoundError("No backup files found in import directory")

            imported_count = 0
            for info_file in backup_files:
                backup_id = info_file.stem.replace("_info", "")
                backup_file = import_dir / f"{backup_id}.json"
                
                if backup_file.exists():
                    # Copy to backup directory
                    shutil.copy2(backup_file, self.backup_directory / f"{backup_id}.json")
                    shutil.copy2(info_file, self.backup_directory / f"{backup_id}_info.json")
                    imported_count += 1
                    print(f"Imported backup: {backup_id}")

            print(f"Successfully imported {imported_count} backups")
            return imported_count

        except Exception as e:
            print(f"Import failed: {e}")
            return 0

    def get_backup_stats(self):
        """Get backup statistics"""
        try:
            backups = self.get_all_backups()
            
            total_size = 0
            for backup in backups:
                backup_file = self.backup_directory / f"{backup['id']}.json"
                if backup_file.exists():
                    total_size += backup_file.stat().st_size

            stats = {
                "total_backups": len(backups),
                "total_size": total_size,
                "last_backup": backups[0] if backups else None,
                "full_backups": len([b for b in backups if b.get("type") == "full"]),
                "incremental_backups": len([b for b in backups if b.get("type") == "incremental"]),
                "oldest_backup": backups[-1] if backups else None
            }

            return stats

        except Exception as e:
            print(f"Failed to get backup stats: {e}")
            return {}

    def start_backup_thread(self):
        """Start automatic backup thread"""
        if self.backup_thread and self.backup_thread.is_alive():
            return

        self.stop_backup_thread = False
        self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.backup_thread.start()
        print("Automatic backup thread started")

    def stop_backup_thread_func(self):
        """Stop automatic backup thread"""
        self.stop_backup_thread = True
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        print("Automatic backup thread stopped")

    def restart_backup_thread(self):
        """Restart automatic backup thread"""
        self.stop_backup_thread_func()
        if self.config.get("auto_backup_enabled", True):
            self.start_backup_thread()

    def _backup_loop(self):
        """Main backup loop running in separate thread"""
        while not self.stop_backup_thread:
            try:
                interval_seconds = self.config.get("interval_hours", 24) * 3600
                
                # Wait for the specified interval
                for _ in range(interval_seconds):
                    if self.stop_backup_thread:
                        return
                    time.sleep(1)

                # Create backup
                if self.config.get("incremental_enabled", True):
                    self.create_incremental_backup()
                else:
                    self.create_full_backup()

            except Exception as e:
                print(f"Automatic backup failed: {e}")
                # Wait 1 hour before retrying
                time.sleep(3600)


# Example usage and testing
if __name__ == "__main__":
    # Initialize backup system
    backup_system = BackupSystem()
    
    # Create a test backup
    try:
        backup_info = backup_system.create_full_backup()
        print(f"Test backup created: {backup_info}")
        
        # Get backup stats
        stats = backup_system.get_backup_stats()
        print(f"Backup stats: {stats}")
        
        # List all backups
        backups = backup_system.get_all_backups()
        print(f"Available backups: {len(backups)}")
        
    except Exception as e:
        print(f"Test failed: {e}")