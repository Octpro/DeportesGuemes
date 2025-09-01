#!/usr/bin/env python3
"""
Deployment Script for Deportes Güemes
Handles deployment preparation, optimization, and deployment procedures
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.html_dir = self.project_root / 'html'
        self.dist_dir = self.project_root / 'dist'
        self.backup_dir = self.project_root / 'backups'
        self.config = self.load_config()
        
    def load_config(self):
        """Load deployment configuration"""
        config_file = self.project_root / 'deploy-config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default deployment configuration"""
        config = {
            "version": "1.0.0",
            "environments": {
                "development": {
                    "url": "http://localhost:8000",
                    "optimize": False,
                    "minify": False,
                    "compress": False
                },
                "staging": {
                    "url": "https://staging.deportesguemes.com",
                    "optimize": True,
                    "minify": True,
                    "compress": True
                },
                "production": {
                    "url": "https://deportesguemes.com",
                    "optimize": True,
                    "minify": True,
                    "compress": True,
                    "cdn": True
                }
            },
            "optimization": {
                "minify_js": True,
                "minify_css": True,
                "optimize_images": True,
                "generate_sourcemaps": False,
                "bundle_assets": True
            },
            "deployment": {
                "backup_before_deploy": True,
                "run_tests": True,
                "verify_deployment": True,
                "rollback_on_failure": True
            }
        }
        
        # Save default config
        config_file = self.project_root / 'deploy-config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config
    
    def prepare_deployment(self, environment='production'):
        """Prepare files for deployment"""
        print(f"🚀 Preparing deployment for {environment}...")
        
        env_config = self.config['environments'][environment]
        
        # Create dist directory
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Copy source files
        self.copy_source_files()
        
        # Apply optimizations
        if env_config.get('optimize', False):
            self.optimize_assets()
        
        if env_config.get('minify', False):
            self.minify_assets()
        
        if env_config.get('compress', False):
            self.compress_assets()
        
        # Generate service worker
        self.generate_service_worker()
        
        # Update configuration
        self.update_config_for_environment(environment)
        
        print("✅ Deployment preparation complete!")
        return self.dist_dir
    
    def copy_source_files(self):
        """Copy source files to dist directory"""
        print("📁 Copying source files...")
        
        # Copy HTML directory
        dist_html = self.dist_dir / 'html'
        shutil.copytree(self.html_dir, dist_html)
        
        # Copy documentation
        docs_src = self.project_root / 'docs'
        if docs_src.exists():
            docs_dst = self.dist_dir / 'docs'
            shutil.copytree(docs_src, docs_dst)
        
        # Copy Python files for desktop app
        python_files = [
            'customtk.py',
            'backup_system.py',
            'backup_gui.py',
            'modern_styles.py'
        ]
        
        for file_name in python_files:
            src_file = self.project_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, self.dist_dir / file_name)
        
        # Copy Programa directory
        programa_src = self.project_root / 'Programa'
        if programa_src.exists():
            programa_dst = self.dist_dir / 'Programa'
            shutil.copytree(programa_src, programa_dst)
    
    def optimize_assets(self):
        """Optimize assets for production"""
        print("⚡ Optimizing assets...")
        
        # Optimize images
        self.optimize_images()
        
        # Bundle JavaScript files
        self.bundle_javascript()
        
        # Optimize CSS
        self.optimize_css()
    
    def optimize_images(self):
        """Optimize images for web delivery"""
        print("🖼️ Optimizing images...")
        
        img_dir = self.dist_dir / 'html' / 'img'
        if not img_dir.exists():
            return
        
        # Simple image optimization (in production, use proper tools)
        for img_file in img_dir.glob('**/*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                # Placeholder for image optimization
                # In production, use tools like Pillow, ImageIO, or external tools
                pass
    
    def bundle_javascript(self):
        """Bundle JavaScript files"""
        print("📦 Bundling JavaScript...")
        
        js_dir = self.dist_dir / 'html' / 'JS'
        if not js_dir.exists():
            return
        
        # Define bundles
        bundles = {
            'core.bundle.js': [
                'cache-manager.js',
                'error-tracker.js',
                'performance-monitor.js'
            ],
            'store.bundle.js': [
                'main.js',
                'carrito.js',
                'menus.js'
            ],
            'features.bundle.js': [
                'advanced-search.js',
                'comprehensive-filters.js',
                'cart-persistence.js'
            ],
            'admin.bundle.js': [
                'backup-system.js',
                'data-synchronization.js',
                'data-validator.js'
            ]
        }
        
        # Create bundles
        for bundle_name, files in bundles.items():
            bundle_content = []
            
            for file_name in files:
                file_path = js_dir / file_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        bundle_content.append(f"// {file_name}\n{content}\n")
            
            if bundle_content:
                bundle_path = js_dir / bundle_name
                with open(bundle_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(bundle_content))
                
                print(f"  ✅ Created {bundle_name}")
    
    def optimize_css(self):
        """Optimize CSS files"""
        print("🎨 Optimizing CSS...")
        
        css_dir = self.dist_dir / 'html' / 'css'
        if not css_dir.exists():
            return
        
        # Combine CSS files
        css_files = list(css_dir.glob('*.css'))
        if css_files:
            combined_css = []
            
            for css_file in css_files:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_css.append(f"/* {css_file.name} */\n{content}\n")
            
            # Write combined CSS
            combined_path = css_dir / 'combined.css'
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(combined_css))
            
            print("  ✅ Combined CSS files")
    
    def minify_assets(self):
        """Minify JavaScript and CSS files"""
        print("🗜️ Minifying assets...")
        
        # Simple minification (remove comments and extra whitespace)
        self.minify_javascript()
        self.minify_css()
    
    def minify_javascript(self):
        """Minify JavaScript files"""
        js_dir = self.dist_dir / 'html' / 'JS'
        if not js_dir.exists():
            return
        
        for js_file in js_dir.glob('*.js'):
            if '.min.' in js_file.name:
                continue
            
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple minification
            minified = self.simple_js_minify(content)
            
            # Save minified version
            min_file = js_file.with_name(js_file.stem + '.min.js')
            with open(min_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            print(f"  ✅ Minified {js_file.name}")
    
    def minify_css(self):
        """Minify CSS files"""
        css_dir = self.dist_dir / 'html' / 'css'
        if not css_dir.exists():
            return
        
        for css_file in css_dir.glob('*.css'):
            if '.min.' in css_file.name:
                continue
            
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple minification
            minified = self.simple_css_minify(content)
            
            # Save minified version
            min_file = css_file.with_name(css_file.stem + '.min.css')
            with open(min_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            print(f"  ✅ Minified {css_file.name}")
    
    def simple_js_minify(self, content):
        """Simple JavaScript minification"""
        import re
        
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove whitespace around operators
        content = re.sub(r'\s*([{}();,])\s*', r'\1', content)
        
        return content.strip()
    
    def simple_css_minify(self, content):
        """Simple CSS minification"""
        import re
        
        # Remove comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove whitespace around CSS syntax
        content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
        
        return content.strip()
    
    def compress_assets(self):
        """Compress assets using gzip"""
        print("🗜️ Compressing assets...")
        
        import gzip
        
        # Compress JavaScript and CSS files
        for file_type in ['js', 'css']:
            file_dir = self.dist_dir / 'html' / ('JS' if file_type == 'js' else 'css')
            if not file_dir.exists():
                continue
            
            for file_path in file_dir.glob(f'*.{file_type}'):
                with open(file_path, 'rb') as f_in:
                    with gzip.open(f'{file_path}.gz', 'wb') as f_out:
                        f_out.writelines(f_in)
                
                print(f"  ✅ Compressed {file_path.name}")
    
    def generate_service_worker(self):
        """Generate service worker for caching"""
        print("⚙️ Generating service worker...")
        
        sw_content = '''
// Service Worker for Deportes Güemes
const CACHE_NAME = 'deportes-guemes-v1';
const urlsToCache = [
    '/',
    '/html/index.html',
    '/html/css/main.css',
    '/html/JS/main.js',
    '/html/JS/cache-manager.js',
    '/html/JS/performance-monitor.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});
'''
        
        sw_path = self.dist_dir / 'html' / 'sw.js'
        with open(sw_path, 'w', encoding='utf-8') as f:
            f.write(sw_content.strip())
        
        print("  ✅ Service worker generated")
    
    def update_config_for_environment(self, environment):
        """Update configuration files for specific environment"""
        print(f"⚙️ Updating configuration for {environment}...")
        
        env_config = self.config['environments'][environment]
        
        # Update HTML files to use minified assets if needed
        if env_config.get('minify', False):
            self.update_html_asset_references()
        
        # Create environment-specific config
        config_js = f'''
// Environment configuration
const CONFIG = {{
    ENVIRONMENT: '{environment}',
    BASE_URL: '{env_config["url"]}',
    OPTIMIZE: {str(env_config.get("optimize", False)).lower()},
    VERSION: '{self.config["version"]}',
    BUILD_TIME: '{datetime.now().isoformat()}'
}};
'''
        
        config_path = self.dist_dir / 'html' / 'JS' / 'config.js'
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_js)
    
    def update_html_asset_references(self):
        """Update HTML files to reference minified assets"""
        html_files = list((self.dist_dir / 'html').glob('*.html'))
        
        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace .js with .min.js
            content = content.replace('.js"', '.min.js"')
            content = content.replace('.css"', '.min.css"')
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def run_tests(self):
        """Run test suite before deployment"""
        print("🧪 Running tests...")
        
        # Run Python tests
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', '-v'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("  ✅ Python tests passed")
            else:
                print("  ❌ Python tests failed")
                print(result.stdout)
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("  ⚠️ pytest not found, skipping Python tests")
        
        # Run JavaScript tests (if test runner exists)
        test_html = self.dist_dir / 'html' / 'test-suite.html'
        if test_html.exists():
            print("  ✅ JavaScript test suite available")
        
        return True
    
    def create_backup(self):
        """Create backup before deployment"""
        print("💾 Creating backup...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'pre_deploy_backup_{timestamp}'
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup current files
        if self.html_dir.exists():
            shutil.copytree(self.html_dir, backup_path / 'html')
        
        # Backup Python files
        for py_file in self.project_root.glob('*.py'):
            shutil.copy2(py_file, backup_path)
        
        # Create backup info
        backup_info = {
            'timestamp': timestamp,
            'version': self.config['version'],
            'files_backed_up': len(list(backup_path.rglob('*'))),
            'backup_size': sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
        }
        
        with open(backup_path / 'backup_info.json', 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"  ✅ Backup created: {backup_name}")
        return backup_path
    
    def deploy(self, environment='production', target_path=None):
        """Deploy to specified environment"""
        print(f"🚀 Deploying to {environment}...")
        
        # Create backup if enabled
        if self.config['deployment'].get('backup_before_deploy', True):
            self.create_backup()
        
        # Run tests if enabled
        if self.config['deployment'].get('run_tests', True):
            if not self.run_tests():
                print("❌ Tests failed, aborting deployment")
                return False
        
        # Prepare deployment
        dist_path = self.prepare_deployment(environment)
        
        # Deploy files
        if target_path:
            target = Path(target_path)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(dist_path, target)
            print(f"  ✅ Files deployed to {target}")
        else:
            print(f"  ✅ Deployment files ready in {dist_path}")
        
        # Verify deployment if enabled
        if self.config['deployment'].get('verify_deployment', True):
            if self.verify_deployment(target_path or dist_path):
                print("✅ Deployment verification passed")
            else:
                print("❌ Deployment verification failed")
                return False
        
        print("🎉 Deployment completed successfully!")
        return True
    
    def verify_deployment(self, deployment_path):
        """Verify deployment integrity"""
        print("🔍 Verifying deployment...")
        
        deployment_path = Path(deployment_path)
        
        # Check required files exist
        required_files = [
            'html/index.html',
            'html/JS/main.js',
            'html/css/main.css'
        ]
        
        for file_path in required_files:
            full_path = deployment_path / file_path
            if not full_path.exists():
                print(f"  ❌ Missing required file: {file_path}")
                return False
        
        # Check file sizes are reasonable
        html_index = deployment_path / 'html' / 'index.html'
        if html_index.stat().st_size < 1000:  # Less than 1KB
            print("  ❌ index.html seems too small")
            return False
        
        print("  ✅ All verification checks passed")
        return True
    
    def rollback(self, backup_name=None):
        """Rollback to previous version"""
        print("🔄 Rolling back deployment...")
        
        if not backup_name:
            # Find latest backup
            backups = list(self.backup_dir.glob('pre_deploy_backup_*'))
            if not backups:
                print("❌ No backups found for rollback")
                return False
            
            backup_path = max(backups, key=lambda p: p.stat().st_mtime)
        else:
            backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False
        
        # Restore files
        if (backup_path / 'html').exists():
            if self.html_dir.exists():
                shutil.rmtree(self.html_dir)
            shutil.copytree(backup_path / 'html', self.html_dir)
        
        # Restore Python files
        for py_file in backup_path.glob('*.py'):
            shutil.copy2(py_file, self.project_root)
        
        print(f"✅ Rollback completed from {backup_path.name}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Deportes Güemes Deployment Manager')
    parser.add_argument('action', choices=['prepare', 'deploy', 'rollback', 'test'],
                       help='Action to perform')
    parser.add_argument('--environment', '-e', default='production',
                       choices=['development', 'staging', 'production'],
                       help='Target environment')
    parser.add_argument('--target', '-t', help='Target deployment path')
    parser.add_argument('--backup', '-b', help='Backup name for rollback')
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    try:
        if args.action == 'prepare':
            dist_path = manager.prepare_deployment(args.environment)
            print(f"Deployment files prepared in: {dist_path}")
        
        elif args.action == 'deploy':
            success = manager.deploy(args.environment, args.target)
            sys.exit(0 if success else 1)
        
        elif args.action == 'rollback':
            success = manager.rollback(args.backup)
            sys.exit(0 if success else 1)
        
        elif args.action == 'test':
            success = manager.run_tests()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()