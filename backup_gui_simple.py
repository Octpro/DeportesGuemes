"""
Simple Backup Management GUI for Deportes Güemes Desktop Application
Provides basic graphical interface for backup and recovery operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import datetime
import threading
import json
import math
from pathlib import Path
from backup_system import BackupSystem


class BackupManagerDialog(ctk.CTkToplevel):
    """Simple backup management dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.backup_system = BackupSystem()
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        """Setup the main window"""
        self.title("Gestión de Respaldos - Deportes Güemes")
        self.geometry("600x400")
        self.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Make modal
        self.transient(self.master)
        self.grab_set()
        self.lift()
        self.focus_force()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create the main UI widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Gestión de Respaldos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Stats display
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Estado del Sistema de Respaldos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(pady=10)
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Cargando estadísticas...")
        self.stats_label.pack(pady=10)
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        # Create backup buttons
        btn_full = ctk.CTkButton(
            buttons_frame,
            text="Crear Respaldo Completo",
            command=self.create_full_backup,
            width=200
        )
        btn_full.pack(side="left", padx=5, pady=10)
        
        btn_incremental = ctk.CTkButton(
            buttons_frame,
            text="Crear Respaldo Incremental",
            command=self.create_incremental_backup,
            width=200
        )
        btn_incremental.pack(side="left", padx=5, pady=10)
        
        # Status display
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Sistema de respaldos listo",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=(20, 0))
        
        # Load initial stats
        self.update_stats()

    def update_stats(self):
        """Update backup statistics display"""
        try:
            stats = self.backup_system.get_backup_stats()
            health = self.backup_system.get_backup_health_status()
            
            stats_text = f"""
Total de respaldos: {stats.get('total_backups', 0)}
Tamaño total: {self.format_file_size(stats.get('total_size', 0))}
Estado: {health['status'].upper()}
{health['message']}
            """
            
            self.stats_label.configure(text=stats_text.strip())
            
        except Exception as e:
            self.stats_label.configure(text=f"Error al cargar estadísticas: {str(e)}")

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"

    def create_full_backup(self):
        """Create a full backup"""
        self.status_label.configure(text="Creando respaldo completo...")
        self.update()
        
        def backup_thread():
            try:
                backup_info = self.backup_system.create_full_backup()
                self.after(0, lambda: self.on_backup_success(backup_info, "completo"))
            except Exception as e:
                self.after(0, lambda: self.on_backup_error(str(e)))
        
        threading.Thread(target=backup_thread, daemon=True).start()

    def create_incremental_backup(self):
        """Create an incremental backup"""
        self.status_label.configure(text="Creando respaldo incremental...")
        self.update()
        
        def backup_thread():
            try:
                backup_info = self.backup_system.create_incremental_backup()
                if backup_info:
                    self.after(0, lambda: self.on_backup_success(backup_info, "incremental"))
                else:
                    self.after(0, lambda: self.on_no_changes())
            except Exception as e:
                self.after(0, lambda: self.on_backup_error(str(e)))
        
        threading.Thread(target=backup_thread, daemon=True).start()

    def on_backup_success(self, backup_info, backup_type):
        """Handle successful backup creation"""
        self.status_label.configure(text=f"Respaldo {backup_type} creado exitosamente")
        messagebox.showinfo("Éxito", f"Respaldo {backup_type} creado exitosamente\nID: {backup_info['id']}")
        self.update_stats()

    def on_backup_error(self, error_message):
        """Handle backup creation error"""
        self.status_label.configure(text="Error al crear respaldo")
        messagebox.showerror("Error", f"Error al crear respaldo: {error_message}")

    def on_no_changes(self):
        """Handle no changes for incremental backup"""
        self.status_label.configure(text="No hay cambios para respaldar")
        messagebox.showinfo("Información", "No hay cambios para respaldar")


# Make the class available for import
__all__ = ['BackupManagerDialog']