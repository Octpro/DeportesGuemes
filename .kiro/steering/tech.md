# Technology Stack

## Desktop Application
- **Framework**: Python with CustomTkinter (modern UI library)
- **Image Processing**: PIL (Pillow) for image handling and color detection
- **Data Storage**: JSON files for product data and history
- **Version Control**: GitPython for automatic commits/pushes
- **UI Components**: Custom dialogs, scrollable frames, tabbed interfaces

## Web Application
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap Icons, Toastify for notifications, SweetAlert2 for modals
- **Data**: JSON-based product catalog
- **Responsive**: Mobile-first design with sidebar navigation

## Key Libraries & Dependencies
```python
# Python Dependencies
customtkinter  # Modern UI framework
PIL (Pillow)   # Image processing
gitpython      # Git integration
json           # Data serialization
tkinter        # Base GUI framework
unicodedata    # Text normalization
```

## File Structure
- **Python Files**: Main application logic in root and `Programa/` folder
- **Web Assets**: Complete web store in `html/` folder
- **Data**: JSON files in `html/JS/` for products and history
- **Images**: Product images stored in `html/img/`

## Common Commands
```bash
# Run desktop application
python customtk.py

# Run alternative main program
python Programa/main.py

# Serve web application (any HTTP server)
# Navigate to html/index.html
```

## Data Management
- Products stored in `html/JS/productos.json`
- History/logs in `html/JS/historial.json`
- Automatic Git commits on product changes
- Image files managed in `html/img/` directory