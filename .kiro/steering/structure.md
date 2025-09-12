# Project Structure

## Root Directory
```
├── customtk.py           # Main desktop application (CustomTkinter)
├── index.html            # Redirect to html/index.html
├── Programa/             # Alternative Python implementation
│   ├── main.py          # Alternative main application
│   └── img.py           # Image selection utility
└── html/                # Web application
    ├── index.html       # Main store page
    ├── carrito.html     # Shopping cart page
    ├── css/
    │   └── main.css     # Main stylesheet
    ├── img/             # Product images
    └── JS/              # JavaScript and data
        ├── main.js      # Main store functionality
        ├── carrito.js   # Cart functionality
        ├── menus.js     # Navigation menus
        ├── productos.json    # Product catalog (main data)
        └── historial.json    # Action history/logs
```

## Architecture Patterns

### Desktop Application
- **MVC Pattern**: Separation of UI (CustomTkinter) and data logic
- **Dialog-based UI**: Modal windows for different operations
- **Event-driven**: Button clicks and form submissions trigger actions
- **Data Manager Class**: Centralized JSON file handling

### Web Application
- **Static Site**: No backend server required
- **Component-based JS**: Modular JavaScript for different pages
- **JSON-driven**: Dynamic content loaded from productos.json
- **Responsive Design**: Mobile-first CSS with sidebar navigation

## Key Conventions

### File Naming
- Python files: lowercase with underscores (`customtk.py`, `main.py`)
- HTML files: lowercase (`index.html`, `carrito.html`)
- CSS/JS: lowercase (`main.css`, `main.js`)
- JSON data: lowercase (`productos.json`, `historial.json`)

### Code Organization
- **Main application**: `customtk.py` (primary) or `Programa/main.py` (alternative)
- **Shared utilities**: Image processing, data normalization functions
- **UI components**: Custom dialog classes for different operations
- **Data layer**: JSON file operations with error handling

### Data Flow
1. Desktop app modifies `productos.json`
2. Changes automatically committed to Git
3. Web app reads from same JSON file
4. Images stored in `html/img/` with relative paths in JSON