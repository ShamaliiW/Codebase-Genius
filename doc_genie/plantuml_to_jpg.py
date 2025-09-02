#!/usr/bin/env python3
"""
PlantUML to JPG Converter
=========================

Convert PlantUML files to JPG images using online PlantUML server.
"""

import os
import base64
import zlib
import requests
from pathlib import Path


def encode_plantuml(plantuml_text):
    """Encode PlantUML text for URL transmission"""
    # Remove @startuml and @enduml if present
    plantuml_text = plantuml_text.strip()
    if plantuml_text.startswith('@startuml'):
        lines = plantuml_text.split('\n')
        lines = lines[1:-1]  # Remove first and last line
        plantuml_text = '\n'.join(lines)
    
    # Compress and encode
    compressed = zlib.compress(plantuml_text.encode('utf-8'))
    
    # Custom base64 encoding for PlantUML
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    
    def encode_base64(data):
        result = ''
        for i in range(0, len(data), 3):
            chunk = data[i:i+3]
            while len(chunk) < 3:
                chunk += b'\x00'
            
            b1, b2, b3 = chunk[0], chunk[1], chunk[2]
            
            result += alphabet[(b1 >> 2) & 0x3F]
            result += alphabet[((b1 & 0x3) << 4) | ((b2 >> 4) & 0xF)]
            result += alphabet[((b2 & 0xF) << 2) | ((b3 >> 6) & 0x3)]
            result += alphabet[b3 & 0x3F]
        
        return result
    
    return encode_base64(compressed)


def convert_plantuml_to_jpg(puml_file, output_file):
    """Convert a PlantUML file to JPG"""
    try:
        # Read PlantUML content
        with open(puml_file, 'r', encoding='utf-8') as f:
            plantuml_content = f.read()
        
        # Encode for URL
        encoded = encode_plantuml(plantuml_content)
        
        # Try multiple PlantUML servers
        servers = [
            'http://www.plantuml.com/plantuml',
            'https://plantuml-server.kkeisuke.app',
            'http://plantuml.com:8080/plantuml'
        ]
        
        for server in servers:
            try:
                # Construct URL for JPG generation
                url = f"{server}/jpg/{encoded}"
                
                print(f"📡 Requesting JPG from {server}...")
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    # Save JPG file
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ Generated {output_file}")
                    return True
                else:
                    print(f"⚠️ Server {server} returned status {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ Failed with server {server}: {e}")
                continue
        
        print(f"❌ All servers failed for {puml_file}")
        return False
        
    except Exception as e:
        print(f"❌ Error processing {puml_file}: {e}")
        return False


def convert_all_plantuml_files(uml_dir):
    """Convert all PlantUML files in directory to JPG"""
    uml_path = Path(uml_dir)
    
    if not uml_path.exists():
        print(f"❌ Directory {uml_dir} does not exist")
        return
    
    puml_files = list(uml_path.glob("*.puml"))
    
    if not puml_files:
        print(f"❌ No .puml files found in {uml_dir}")
        return
    
    print(f"🔍 Found {len(puml_files)} PlantUML files")
    
    success_count = 0
    for puml_file in puml_files:
        jpg_file = puml_file.with_suffix('.jpg')
        if convert_plantuml_to_jpg(puml_file, jpg_file):
            success_count += 1
    
    print(f"\n📊 Summary: {success_count}/{len(puml_files)} diagrams converted to JPG")


if __name__ == "__main__":
    # Convert all PlantUML files in the output/uml directory
    uml_directory = "output/uml"
    convert_all_plantuml_files(uml_directory)
