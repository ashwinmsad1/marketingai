#!/usr/bin/env python3
"""
Video validation script to check generated video files
"""
import os
import sys

def validate_video_file(video_path):
    """
    Comprehensive video file validation
    
    Args:
        video_path (str): Path to video file
    
    Returns:
        dict: Validation results
    """
    results = {
        'file_exists': False,
        'file_size': 0,
        'is_readable': False,
        'has_video_header': False,
        'header_info': '',
        'errors': []
    }
    
    try:
        # Check if file exists
        if not os.path.exists(video_path):
            results['errors'].append(f"File does not exist: {video_path}")
            return results
        
        results['file_exists'] = True
        
        # Check file size
        file_size = os.path.getsize(video_path)
        results['file_size'] = file_size
        
        if file_size == 0:
            results['errors'].append("File is empty (0 bytes)")
            return results
        
        if file_size < 1000:
            results['errors'].append(f"File is suspiciously small: {file_size} bytes")
        
        # Try to read file
        try:
            with open(video_path, "rb") as f:
                header = f.read(32)  # Read first 32 bytes for analysis
                results['is_readable'] = True
                results['header_info'] = header.hex()[:64]  # First 32 bytes in hex
                
                # Check for video file signatures
                if len(header) >= 8:
                    if header[4:8] == b'ftyp':
                        results['has_video_header'] = True
                        # Check specific MP4 subtypes
                        if len(header) >= 12:
                            subtype = header[8:12]
                            if subtype in [b'isom', b'mp41', b'mp42', b'avc1', b'dash']:
                                print(f"✅ Valid MP4 file detected (subtype: {subtype.decode('ascii', errors='ignore')})")
                            else:
                                print(f"⚠️  MP4 file with unknown subtype: {subtype}")
                    elif header[:4] == b'\x1a\x45\xdf\xa3':
                        results['has_video_header'] = True
                        print("✅ Matroska/WebM video detected")
                    elif header[:3] == b'FLV':
                        results['has_video_header'] = True  
                        print("✅ FLV video detected")
                    elif header[:4] == b'RIFF' and header[8:12] == b'AVI ':
                        results['has_video_header'] = True
                        print("✅ AVI video detected")
                    else:
                        print(f"⚠️  Unknown file format. Header: {header[:16].hex()}")
                        results['errors'].append("File does not have recognized video header")
                
        except IOError as e:
            results['errors'].append(f"Cannot read file: {e}")
        
        # Try using moviepy for deeper validation if available
        try:
            from moviepy import VideoFileClip
            try:
                clip = VideoFileClip(video_path)
                duration = clip.duration
                fps = clip.fps
                size = clip.size
                print(f"✅ MoviePy validation successful:")
                print(f"   Duration: {duration:.2f} seconds")
                print(f"   FPS: {fps}")
                print(f"   Resolution: {size[0]}x{size[1]}")
                clip.close()
            except Exception as moviepy_error:
                results['errors'].append(f"MoviePy validation failed: {moviepy_error}")
        except ImportError:
            print("📋 MoviePy not available for advanced validation")
    
    except Exception as e:
        results['errors'].append(f"Unexpected error: {e}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_video.py <video_file_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    print(f"🔍 Validating video file: {video_path}")
    print("=" * 50)
    
    results = validate_video_file(video_path)
    
    print(f"File exists: {results['file_exists']}")
    print(f"File size: {results['file_size']} bytes")
    print(f"Is readable: {results['is_readable']}")
    print(f"Has video header: {results['has_video_header']}")
    
    if results['header_info']:
        print(f"Header (hex): {results['header_info']}")
    
    if results['errors']:
        print("\n❌ Errors found:")
        for error in results['errors']:
            print(f"   - {error}")
    else:
        print("\n✅ Video file appears to be valid!")
    
    print(f"\nFull file path: {os.path.abspath(video_path)}")

if __name__ == "__main__":
    main()