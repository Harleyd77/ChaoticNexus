#!/usr/bin/env python3
"""
Codemod to convert Flask/Jinja templates to extend base.html
and remove Tailwind CDN and legacy CSS links.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

# Patterns to remove
PATTERNS_TO_REMOVE = [
    r'<script[^>]*src=["\']https://cdn\.tailwindcss\.com[^"\']*["\'][^>]*></script>',
    r'<link[^>]*href=["\'][^"\']*static/css/theme\.css[^"\']*["\'][^>]*>',
    r'<link[^>]*href=["\'][^"\']*static/css/components\.css[^"\']*["\'][^>]*>',
]


class TemplateConverter:
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.changed_files = []
        self.special_handling = []
        self.backup_suffix = '.bak'
        
    def is_full_html_template(self, content: str) -> bool:
        """Check if template has full HTML structure."""
        return bool(re.search(r'<html[^>]*>', content, re.IGNORECASE))
    
    def has_extends(self, content: str) -> bool:
        """Check if template already extends something."""
        return bool(re.search(r'{%\s*extends\s+', content))
    
    def extract_head_content(self, content: str) -> Tuple[str, str]:
        """Extract content from <head> that should go to extra_head block."""
        head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.DOTALL | re.IGNORECASE)
        if not head_match:
            return '', content
        
        head_content = head_match.group(1)
        
        # Extract custom styles and meta tags (skip standard ones)
        extra_head_parts = []
        
        # Extract <style> tags
        for style_match in re.finditer(r'<style[^>]*>.*?</style>', head_content, re.DOTALL):
            extra_head_parts.append(style_match.group(0))
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', head_content, re.DOTALL)
        if title_match:
            title_content = title_match.group(1).strip()
            # Extract just the page-specific part if it follows a pattern
            if ' &middot; ' in title_content:
                page_title = title_content.split(' &middot; ')[0].strip()
            elif ' - ' in title_content:
                page_title = title_content.split(' - ')[0].strip()
            else:
                page_title = title_content
            
            if page_title and page_title != 'Victoria Powder Coating':
                extra_head_parts.append(f'  <title>{{{{ super() }}}} | {page_title}</title>')
        
        # Extract custom scripts in head (not the CDN ones we're removing)
        for script_match in re.finditer(r'<script[^>]*>.*?</script>', head_content, re.DOTALL):
            script_tag = script_match.group(0)
            # Skip if it's one we want to remove
            skip = False
            for pattern in PATTERNS_TO_REMOVE:
                if re.search(pattern, script_tag):
                    skip = True
                    break
            if not skip and 'cdn.tailwindcss.com' not in script_tag:
                extra_head_parts.append(script_tag)
        
        extra_head = '\n'.join(extra_head_parts) if extra_head_parts else ''
        
        return extra_head, content
    
    def extract_body_content(self, content: str) -> str:
        """Extract content from <body>."""
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            return body_match.group(1).strip()
        return content
    
    def extract_scripts_from_body(self, content: str) -> Tuple[str, str]:
        """Extract scripts from end of body content."""
        scripts = []
        remaining_content = content
        
        # Find all script tags at the end of the content
        script_pattern = r'(<script[^>]*>.*?</script>)\s*$'
        while True:
            match = re.search(script_pattern, remaining_content, re.DOTALL)
            if not match:
                break
            scripts.insert(0, match.group(1))
            remaining_content = remaining_content[:match.start()].rstrip()
        
        return '\n  '.join(scripts) if scripts else '', remaining_content
    
    def remove_unwanted_patterns(self, content: str) -> str:
        """Remove Tailwind CDN and legacy CSS links."""
        for pattern in PATTERNS_TO_REMOVE:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        return content
    
    def convert_template(self, file_path: Path) -> bool:
        """Convert a single template file."""
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip if empty
            if not original_content.strip():
                return False
            
            # Skip if already extends base.html
            if re.search(r'{%\s*extends\s+["\']base\.html["\']', original_content):
                print(f"  ⏭️  Skipping {file_path.relative_to(self.templates_dir)} (already extends base.html)")
                return False
            
            # Backup original
            backup_path = file_path.with_suffix(file_path.suffix + self.backup_suffix)
            if not backup_path.exists():
                shutil.copy2(file_path, backup_path)
            
            content = original_content
            
            # Remove unwanted patterns
            content = self.remove_unwanted_patterns(content)
            
            # Check if this is a full HTML template
            if self.is_full_html_template(content):
                # Extract extra head content
                extra_head, content = self.extract_head_content(content)
                
                # Extract body content
                body_content = self.extract_body_content(content)
                
                # Extract scripts from body
                scripts, body_content = self.extract_scripts_from_body(body_content)
                
                # Build new template
                new_content = '{% extends "base.html" %}\n\n'
                
                if extra_head:
                    new_content += '{% block extra_head %}\n'
                    new_content += extra_head + '\n'
                    new_content += '{% endblock %}\n\n'
                
                new_content += '{% block content %}\n'
                new_content += body_content + '\n'
                new_content += '{% endblock %}\n'
                
                if scripts:
                    new_content += '\n{% block scripts %}\n'
                    new_content += '  ' + scripts + '\n'
                    new_content += '{% endblock %}\n'
                
                content = new_content
                self.special_handling.append(str(file_path.relative_to(self.templates_dir)))
            
            else:
                # For partial templates, just remove unwanted patterns
                # and add block wrappers if they don't have any
                if not re.search(r'{%\s*block\s+', content) and not self.has_extends(content):
                    # Check if it's a substantial template that should be wrapped
                    if len(content.strip()) > 100 and ('<div' in content or '<section' in content):
                        content = '{% extends "base.html" %}\n\n{% block content %}\n' + content + '\n{% endblock %}\n'
                        self.special_handling.append(f"{file_path.relative_to(self.templates_dir)} (partial converted)")
            
            # Write converted content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Only mark as changed if content actually changed
            if content != original_content:
                self.changed_files.append(str(file_path.relative_to(self.templates_dir)))
                return True
            
            return False
            
        except Exception as e:
            print(f"  ❌ Error converting {file_path}: {e}")
            return False
    
    def convert_all(self):
        """Convert all template files."""
        print("🔄 Converting templates to use base.html...\n")
        
        # Find all HTML template files
        template_files = list(self.templates_dir.rglob('*.html'))
        
        # Special files to handle explicitly
        special_files = [
            'customer_portal/base.html',
            'auth/login_base.html',
        ]
        
        converted_count = 0
        
        for template_file in template_files:
            # Skip the new base.html we just created
            if template_file.name == 'base.html' and template_file.parent == self.templates_dir:
                continue
            
            rel_path = str(template_file.relative_to(self.templates_dir))
            print(f"  📄 Processing: {rel_path}")
            
            if self.convert_template(template_file):
                converted_count += 1
        
        print(f"\n✅ Conversion complete!")
        print(f"   Converted: {converted_count} files")
        print(f"   Total processed: {len(template_files)}")
        
        return converted_count


def main():
    """Main entry point."""
    # Find templates directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    templates_dir = project_root / 'src' / 'powder_app' / 'templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return 1
    
    print(f"📁 Templates directory: {templates_dir}\n")
    
    converter = TemplateConverter(str(templates_dir))
    converter.convert_all()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CONVERSION SUMMARY")
    print("=" * 60)
    
    if converter.changed_files:
        print(f"\n✅ Changed files ({len(converter.changed_files)}):")
        for f in sorted(converter.changed_files):
            print(f"   - {f}")
    
    if converter.special_handling:
        print(f"\n⚠️  Special handling ({len(converter.special_handling)}):")
        for f in sorted(converter.special_handling):
            print(f"   - {f}")
    
    print("\n💾 Backups saved with .bak extension")
    print("✅ You can now remove .bak files if everything looks good")
    
    return 0


if __name__ == '__main__':
    exit(main())

