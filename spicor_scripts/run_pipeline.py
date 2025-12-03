#!/usr/bin/env python3
"""
SPICOR Audio Processing Pipeline
Main orchestration script that:
1. Copies spicor_samples_original to spicor_samples_processed (preserves original)
2. Processes audio files (resample, convert, rename)
3. Organizes output in wavs/ folder
4. Creates a zip archive of the processed folder
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)


def copy_original_to_processed(original_dir, processed_dir):
    """
    Copy original samples to processed directory.
    
    Args:
        original_dir: Path to spicor_samples_original
        processed_dir: Path to spicor_samples_processed
    """
    print_header("📁 STEP 1: Copying Original Files")
    
    original_dir = Path(original_dir)
    processed_dir = Path(processed_dir)
    
    if not original_dir.exists():
        print(f"❌ Error: Original directory not found: {original_dir}")
        return False
    
    # Remove processed directory if it exists
    if processed_dir.exists():
        print(f"🗑️  Removing existing processed directory...")
        shutil.rmtree(processed_dir)
    
    # Copy original to processed
    print(f"📋 Copying from: {original_dir.name}")
    print(f"📋 Copying to: {processed_dir.name}")
    
    shutil.copytree(original_dir, processed_dir)
    
    # Count files copied
    wav_files = list(processed_dir.glob('*.wav'))
    json_files = list(processed_dir.glob('*.json'))
    
    print(f"\n✅ Copy complete!")
    print(f"   • WAV files: {len(wav_files)}")
    print(f"   • JSON files: {len(json_files)}")
    
    return True


def process_audio_files(processed_dir):
    """
    Run the audio processing script.
    
    Args:
        processed_dir: Path to spicor_samples_processed
    """
    print_header("🎵 STEP 2: Processing Audio Files")
    
    processed_dir = Path(processed_dir)
    script_path = Path(__file__).parent / 'process_audio_resample.py'
    
    if not script_path.exists():
        print(f"❌ Error: Processing script not found: {script_path}")
        return False
    
    print(f"📝 Running: {script_path.name}")
    print(f"📁 Working directory: {processed_dir}")
    
    # Import and run the processing script
    sys.path.insert(0, str(script_path.parent))
    
    try:
        # Change to processed directory
        original_cwd = os.getcwd()
        os.chdir(processed_dir)
        
        # Import the processing module
        import process_audio_resample
        
        # Run the main processing function
        success = process_audio_resample.process_audio_files(
            input_dir=processed_dir,
            output_dir=processed_dir / 'wavs',
            target_sr=22050
        )
        
        # Return to original directory
        os.chdir(original_cwd)
        
        if not success:
            print(f"\n❌ Audio processing failed!")
            return False
        
        return True
        
    except Exception as e:
        os.chdir(original_cwd)
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_zip_archive(processed_dir):
    """
    Create a zip archive of the processed folder.
    
    Args:
        processed_dir: Path to spicor_samples_processed
    """
    print_header("📦 STEP 3: Creating ZIP Archive")
    
    processed_dir = Path(processed_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"spicor_samples_processed_{timestamp}.zip"
    zip_path = processed_dir.parent / zip_filename
    
    print(f"📦 Creating archive: {zip_filename}")
    print(f"📁 Source: {processed_dir.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from processed directory
        for file_path in processed_dir.rglob('*'):
            if file_path.is_file():
                # Skip hidden files and cache
                if file_path.name.startswith('.') or '__pycache__' in str(file_path):
                    continue
                
                arcname = file_path.relative_to(processed_dir.parent)
                zipf.write(file_path, arcname)
                print(f"   ✓ Added: {arcname}")
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # Convert to MB
    
    print(f"\n✅ Archive created successfully!")
    print(f"   • File: {zip_filename}")
    print(f"   • Size: {zip_size:.2f} MB")
    print(f"   • Location: {zip_path}")
    
    return True


def main():
    """Main pipeline orchestration."""
    print("\n" + "="*70)
    print("🎵 SPICOR Audio Processing Pipeline")
    print("="*70)
    print("This pipeline will:")
    print("  1. Copy spicor_samples_original → spicor_samples_processed")
    print("  2. Process audio files (resample, convert, rename)")
    print("  3. Organize outputs in wavs/ folder")
    print("  4. Create ZIP archive")
    print("="*70)
    
    # Get directories
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    original_dir = project_root / 'spicor_samples_original'
    processed_dir = project_root / 'spicor_samples_processed'
    
    # Confirm action
    print(f"\n📁 Project root: {project_root}")
    print(f"📁 Original dir: {original_dir.name}")
    print(f"📁 Processed dir: {processed_dir.name}")
    
    response = input("\n▶️  Start processing? (y/n): ").strip().lower()
    if response not in ['y', 'yes']:
        print("\n❌ Processing cancelled.")
        return
    
    start_time = datetime.now()
    
    # Step 1: Copy original to processed
    if not copy_original_to_processed(original_dir, processed_dir):
        print("\n❌ Pipeline failed at Step 1!")
        sys.exit(1)
    
    # Step 2: Process audio files
    if not process_audio_files(processed_dir):
        print("\n❌ Pipeline failed at Step 2!")
        sys.exit(1)
    
    # Step 3: Create ZIP archive
    if not create_zip_archive(processed_dir):
        print("\n❌ Pipeline failed at Step 3!")
        sys.exit(1)
    
    # Final summary
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    print_header("✅ PIPELINE COMPLETE!")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"📁 Processed folder: {processed_dir}")
    print(f"📁 Output files: {processed_dir / 'wavs'}")
    print(f"📦 ZIP archive: {processed_dir.parent}")
    print("\n🎉 Your audio files are ready for training!")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
