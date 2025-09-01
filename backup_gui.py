"""
Backup Management GUI for Deportes Güemes Desktop Application
Provides graphical interface for backup and recovery operations
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
    def __init__(self, parent):
        super().__init__(parent)
        
        self.backup_system = BackupSystem()
        self.setup_window()
        self.create_widgets()
        self.refresh_backup_list()
        self.update_stats()

    def setup_window(self):
        """Setup the main window"""
        self.title("Gestión de Respaldos - Deportes Güemes")
        self.geometry("900x700")
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
        
        # Stats frame
        self.create_stats_frame(main_frame)
        
        # Actions frame
        self.create_actions_frame(main_frame)
        
        # Backup list frame
        self.create_backup_list_frame(main_frame)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=(20, 0))

    def create_stats_frame(self, parent):
        """Create backup statistics frame"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="Estadísticas de Respaldos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(pady=(10, 5))
        
        # Stats container
        stats_container = ctk.CTkFrame(stats_frame)
        stats_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Create stats labels
        self.stats_labels = {}
        stats_info = [
            ("total_backups", "Total de Respaldos"),
            ("total_size", "Tamaño Total"),
            ("last_backup", "Último Respaldo"),
            ("next_backup", "Próximo Respaldo")
        ]
        
        for i, (key, label) in enumerate(stats_info):
            row = i // 2
            col = i % 2
            
            stat_frame = ctk.CTkFrame(stats_container)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(pady=(5, 0))
            
            self.stats_labels[key] = ctk.CTkLabel(
                stat_frame,
                text="Cargando...",
                font=ctk.CTkFont(size=14)
            )
            self.stats_labels[key].pack(pady=(0, 5))
        
        # Configure grid weights
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_columnconfigure(1, weight=1)

    def create_actions_frame(self, parent):
        """Create backup actions frame"""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Acciones de Respaldo",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_title.pack(pady=(10, 5))
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(actions_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Action buttons
        btn_full_backup = ctk.CTkButton(
            buttons_frame,
            text="Respaldo Completo",
            command=self.create_full_backup,
            width=150
        )
        btn_full_backup.pack(side="left", padx=5, pady=10)
        
        btn_incremental_backup = ctk.CTkButton(
            buttons_frame,
            text="Respaldo Incremental",
            command=self.create_incremental_backup,
            width=150
        )
        btn_incremental_backup.pack(side="left", padx=5, pady=10)
        
        btn_import_backup = ctk.CTkButton(
            buttons_frame,
            text="Importar Respaldo",
            command=self.import_backup,
            width=150
        )
        btn_import_backup.pack(side="left", padx=5, pady=10)
        
        btn_configure = ctk.CTkButton(
            buttons_frame,
            text="Configurar",
            command=self.show_configuration,
            width=150
        )
        btn_configure.pack(side="left", padx=5, pady=10)

    def create_backup_list_frame(self, parent):
        """Create backup list frame"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True)
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="Lista de Respaldos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(pady=(10, 5))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            list_frame,
            text="Actualizar",
            command=self.refresh_backup_list,
            width=100
        )
        refresh_btn.pack(pady=(0, 10))
        
        # Backup list (using Treeview for better display)
        columns = ("ID", "Fecha", "Tipo", "Tamaño", "Estado")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.backup_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Context menu for backup items
        self.backup_tree.bind("<Button-3>", self.show_context_menu)
        self.backup_tree.bind("<Double-1>", self.preview_restore)

    def refresh_backup_list(self):
        """Refresh the backup list"""
        try:
            # Clear existing items
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)
            
            # Get all backups
            backups = self.backup_system.get_all_backups()
            
            for backup in backups:
                # Format backup info for display
                backup_id = backup["id"][:16] + "..." if len(backup["id"]) > 16 else backup["id"]
                date_str = datetime.fromisoformat(backup["timestamp"]).strftime("%Y-%m-%d %H:%M")
                backup_type = backup.get("type", "unknown").title()
                size_str = self.format_file_size(backup.get("size", 0))
                
                # Verify integrity
                is_valid = self.backup_system.verify_backup_integrity(backup["id"])
                status = "Válido" if is_valid else "Corrupto"
                
                # Insert into tree
                self.backup_tree.insert("", "end", values=(
                    backup_id, date_str, backup_type, size_str, status
                ), tags=(backup["id"],))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar lista de respaldos: {str(e)}")

    def update_stats(self):
        """Update backup statistics"""
        try:
            stats = self.backup_system.get_backup_stats()
            
            self.stats_labels["total_backups"].configure(text=str(stats.get("total_backups", 0)))
            self.stats_labels["total_size"].configure(text=self.format_file_size(stats.get("total_size", 0)))
            
            last_backup = stats.get("last_backup")
            if last_backup:
                last_date = datetime.fromisoformat(last_backup["timestamp"])
                self.stats_labels["last_backup"].configure(text=last_date.strftime("%Y-%m-%d %H:%M"))
            else:
                self.stats_labels["last_backup"].configure(text="Nunca")
            
            # Calculate next backup time (simplified)
            self.stats_labels["next_backup"].configure(text="Automático")
            
        except Exception as e:
            print(f"Error updating stats: {e}")

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
        try:
            # Show progress
            progress_dialog = self.show_progress_dialog("Creando respaldo completo...")
            
            # Create backup in separate thread
            def backup_thread():
                try:
                    backup_info = self.backup_system.create_full_backup()
                    self.after(0, lambda: self.on_backup_complete(progress_dialog, backup_info, "completo"))
                except Exception as e:
                    self.after(0, lambda: self.on_backup_error(progress_dialog, str(e)))
            
            threading.Thread(target=backup_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")

    def create_incremental_backup(self):
        """Create an incremental backup"""
        try:
            # Show progress
            progress_dialog = self.show_progress_dialog("Creando respaldo incremental...")
            
            # Create backup in separate thread
            def backup_thread():
                try:
                    backup_info = self.backup_system.create_incremental_backup()
                    if backup_info:
                        self.after(0, lambda: self.on_backup_complete(progress_dialog, backup_info, "incremental"))
                    else:
                        self.after(0, lambda: self.on_backup_no_changes(progress_dialog))
                except Exception as e:
                    self.after(0, lambda: self.on_backup_error(progress_dialog, str(e)))
            
            threading.Thread(target=backup_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")

    def import_backup(self):
        """Import backup from file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de respaldo",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                count = self.backup_system.import_backup(file_path)
                if count > 0:
                    messagebox.showinfo("Éxito", f"Se importaron {count} respaldos exitosamente")
                    self.refresh_backup_list()
                    self.update_stats()
                else:
                    messagebox.showwarning("Advertencia", "No se encontraron respaldos válidos para importar")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar respaldo: {str(e)}")

    def show_configuration(self):
        """Show backup configuration dialog"""
        ConfigurationDialog(self, self.backup_system)

    def show_progress_dialog(self, message):
        """Show progress dialog"""
        progress = ctk.CTkToplevel(self)
        progress.title("Procesando...")
        progress.geometry("300x100")
        progress.transient(self)
        progress.grab_set()
        
        # Center the dialog
        progress.update_idletasks()
        x = (progress.winfo_screenwidth() // 2) - (150)
        y = (progress.winfo_screenheight() // 2) - (50)
        progress.geometry(f"300x100+{x}+{y}")
        
        ctk.CTkLabel(progress, text=message).pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(progress)
        progress_bar.pack(pady=10)
        progress_bar.set(0.5)  # Indeterminate progress
        
        return progress

    def on_backup_complete(self, progress_dialog, backup_info, backup_type):
        """Handle backup completion"""
        progress_dialog.destroy()
        messagebox.showinfo("Éxito", f"Respaldo {backup_type} creado exitosamente\nID: {backup_info['id']}")
        self.refresh_backup_list()
        self.update_stats()

    def on_backup_no_changes(self, progress_dialog):
        """Handle backup with no changes"""
        progress_dialog.destroy()
        messagebox.showinfo("Información", "No hay cambios para respaldar")

    def on_backup_error(self, progress_dialog, error_message):
        """Handle backup error"""
        progress_dialog.destroy()
        messagebox.showerror("Error", f"Error al crear respaldo: {error_message}")

    def show_context_menu(self, event):
        """Show context menu for backup items"""
        item = self.backup_tree.selection()[0] if self.backup_tree.selection() else None
        if not item:
            return
        
        # Get backup ID from tags
        backup_id = self.backup_tree.item(item)["tags"][0]
        
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Vista Previa", command=lambda: self.preview_restore(backup_id=backup_id))
        context_menu.add_command(label="Restaurar", command=lambda: self.restore_backup(backup_id))
        context_menu.add_command(label="Exportar", command=lambda: self.export_backup(backup_id))
        context_menu.add_separator()
        context_menu.add_command(label="Eliminar", command=lambda: self.delete_backup(backup_id))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def preview_restore(self, event=None, backup_id=None):
        """Preview restore operation"""
        if not backup_id:
            item = self.backup_tree.selection()[0] if self.backup_tree.selection() else None
            if not item:
                return
            backup_id = self.backup_tree.item(item)["tags"][0]
        
        try:
            result = self.backup_system.restore_from_backup(backup_id, preview=True)
            if result["success"]:
                PreviewDialog(self, result["data"], result["backup_info"])
            else:
                messagebox.showerror("Error", f"Error en vista previa: {result['error']}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en vista previa: {str(e)}")

    def restore_backup(self, backup_id):
        """Restore from backup"""
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea restaurar este respaldo?\nEsta acción sobrescribirá los datos actuales."):
            return
        
        try:
            # Show progress
            progress_dialog = self.show_progress_dialog("Restaurando respaldo...")
            
            def restore_thread():
                try:
                    result = self.backup_system.restore_from_backup(backup_id)
                    self.after(0, lambda: self.on_restore_complete(progress_dialog, result))
                except Exception as e:
                    self.after(0, lambda: self.on_restore_error(progress_dialog, str(e)))
            
            threading.Thread(target=restore_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar: {str(e)}")

    def on_restore_complete(self, progress_dialog, result):
        """Handle restore completion"""
        progress_dialog.destroy()
        if result["success"]:
            messagebox.showinfo("Éxito", f"Respaldo restaurado exitosamente\n{result['message']}")
        else:
            messagebox.showerror("Error", f"Error al restaurar: {result['error']}")

    def on_restore_error(self, progress_dialog, error_message):
        """Handle restore error"""
        progress_dialog.destroy()
        messagebox.showerror("Error", f"Error al restaurar: {error_message}")

    def export_backup(self, backup_id):
        """Export backup to file"""
        try:
            export_path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if export_path:
                success = self.backup_system.export_backup(backup_id, export_path)
                if success:
                    messagebox.showinfo("Éxito", f"Respaldo exportado exitosamente a {export_path}")
                else:
                    messagebox.showerror("Error", "Error al exportar respaldo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def delete_backup(self, backup_id):
        """Delete backup"""
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este respaldo?"):
            return
        
        try:
            # Remove backup files
            backup_file = self.backup_system.backup_directory / f"{backup_id}.json"
            info_file = self.backup_system.backup_directory / f"{backup_id}_info.json"
            
            if backup_file.exists():
                backup_file.unlink()
            if info_file.exists():
                info_file.unlink()
            
            messagebox.showinfo("Éxito", "Respaldo eliminado exitosamente")
            self.refresh_backup_list()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar respaldo: {str(e)}")


class ConfigurationDialog(ctk.CTkToplevel):
    """Backup configuration dialog"""
    
    def __init__(self, parent, backup_system):
        super().__init__(parent)
        self.backup_system = backup_system
        
        self.title("Configuración de Respaldos")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (200)
        y = (self.winfo_screenheight() // 2) - (150)
        self.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
        self.load_current_config()

    def create_widgets(self):
        """Create configuration widgets"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Configuración de Respaldos",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Interval setting
        interval_frame = ctk.CTkFrame(main_frame)
        interval_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(interval_frame, text="Intervalo de respaldo (horas):").pack(pady=5)
        self.interval_var = ctk.StringVar(value="24")
        self.interval_entry = ctk.CTkEntry(interval_frame, textvariable=self.interval_var)
        self.interval_entry.pack(pady=5)
        
        # Max backups setting
        max_backups_frame = ctk.CTkFrame(main_frame)
        max_backups_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(max_backups_frame, text="Máximo número de respaldos:").pack(pady=5)
        self.max_backups_var = ctk.StringVar(value="30")
        self.max_backups_entry = ctk.CTkEntry(max_backups_frame, textvariable=self.max_backups_var)
        self.max_backups_entry.pack(pady=5)
        
        # Compression setting
        self.compression_var = ctk.BooleanVar(value=True)
        compression_check = ctk.CTkCheckBox(
            main_frame,
            text="Habilitar compresión",
            variable=self.compression_var
        )
        compression_check.pack(pady=10)
        
        # Incremental setting
        self.incremental_var = ctk.BooleanVar(value=True)
        incremental_check = ctk.CTkCheckBox(
            main_frame,
            text="Habilitar respaldos incrementales",
            variable=self.incremental_var
        )
        incremental_check.pack(pady=5)
        
        # Auto backup setting
        self.auto_backup_var = ctk.BooleanVar(value=True)
        auto_backup_check = ctk.CTkCheckBox(
            main_frame,
            text="Habilitar respaldos automáticos",
            variable=self.auto_backup_var
        )
        auto_backup_check.pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.save_config,
            width=100
        )
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            width=100
        )
        cancel_btn.pack(side="right", padx=5)

    def load_current_config(self):
        """Load current configuration"""
        try:
            config = self.backup_system.config
            self.interval_var.set(str(config.get("interval_hours", 24)))
            self.max_backups_var.set(str(config.get("max_backups", 30)))
            self.compression_var.set(config.get("compression_enabled", True))
            self.incremental_var.set(config.get("incremental_enabled", True))
            self.auto_backup_var.set(config.get("auto_backup_enabled", True))
        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        """Save configuration"""
        try:
            new_config = {
                "interval_hours": int(self.interval_var.get()),
                "max_backups": int(self.max_backups_var.get()),
                "compression_enabled": self.compression_var.get(),
                "incremental_enabled": self.incremental_var.get(),
                "auto_backup_enabled": self.auto_backup_var.get()
            }
            
            self.backup_system.update_config(new_config)
            messagebox.showinfo("Éxito", "Configuración guardada exitosamente")
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")


class PreviewDialog(ctk.CTkToplevel):
    """Preview dialog for restore operations"""
    
    def __init__(self, parent, restore_data, backup_info):
        super().__init__(parent)
        self.restore_data = restore_data
        self.backup_info = backup_info
        
        self.title("Vista Previa de Restauración")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300)
        y = (self.winfo_screenheight() // 2) - (200)
        self.geometry(f"600x400+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        """Create preview widgets"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Vista Previa de Restauración",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Backup info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_text = f"""
Información del Respaldo:
ID: {self.backup_info['id']}
Fecha: {datetime.fromisoformat(self.backup_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
Tipo: {self.backup_info.get('type', 'unknown').title()}
Tamaño: {self.format_file_size(self.backup_info.get('size', 0))}
        """
        
        info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left")
        info_label.pack(pady=10)
        
        # Data preview
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True)
        
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="Contenido a Restaurar:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_title.pack(pady=(10, 5))
        
        # Create preview text
        preview_text = self.generate_preview_text()
        
        text_widget = ctk.CTkTextbox(preview_frame)
        text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        text_widget.insert("1.0", preview_text)
        text_widget.configure(state="disabled")
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=(10, 0))

    def generate_preview_text(self):
        """Generate preview text"""
        preview_lines = []
        
        if "files" in self.restore_data:
            files_data = self.restore_data["files"]
            if "productos.json" in files_data and files_data["productos.json"]:
                productos_count = len(files_data["productos.json"])
                preview_lines.append(f"Productos: {productos_count} elementos")
            
            if "historial.json" in files_data and files_data["historial.json"]:
                historial_count = len(files_data["historial.json"])
                preview_lines.append(f"Historial: {historial_count} entradas")
        
        if "directories" in self.restore_data:
            dirs_data = self.restore_data["directories"]
            for dir_name, dir_info in dirs_data.items():
                if isinstance(dir_info, dict):
                    file_count = len([f for f in dir_info.values() if isinstance(f, dict) and f.get("type") == "file"])
                    preview_lines.append(f"Directorio {dir_name}: {file_count} archivos")
        
        if "metadata" in self.restore_data:
            metadata = self.restore_data["metadata"]
            if "timestamp" in metadata:
                preview_lines.append(f"Fecha de creación: {metadata['timestamp']}")
        
        return "\n".join(preview_lines) if preview_lines else "No hay información de vista previa disponible"

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
# Make sure the classes are available for import
__all__ = ['BackupManagerDialog', 'ConfigurationDialog', 'PreviewDialog']