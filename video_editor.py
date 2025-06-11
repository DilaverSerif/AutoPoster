import subprocess
import os
import sys
import time
import json
import re
import random

def get_video_info(video_path):
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration',
        '-of', 'json',
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        return info['streams'][0]
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def edit_video(input_video="clip1.mp4", output_video="output.mp4", logo_path="logo.png", hipnoz_video="hipnoz.mp4"):
    # Check if all required files exist
    for file_path in [input_video, logo_path, hipnoz_video]:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found!")
            return False

    # Get video information
    main_info = get_video_info(input_video)
    hipnoz_info = get_video_info(hipnoz_video)
    if main_info is None or hipnoz_info is None:
        return False

    width = main_info['width']
    height = main_info['height']
    main_duration = float(main_info['duration'])
    hipnoz_duration = float(hipnoz_info['duration'])
    
    # Calculate random start time for hipnoz video
    max_start = max(0, hipnoz_duration - main_duration)
    random_start = random.uniform(0, max_start)
    
    # Calculate heights for split
    main_height = int(height * 0.7)  # 75% of original height
    hipnoz_height = int(height * 0.3)  # 25% of original height

    print(f"Original video resolution: {width}x{height}")
    print(f"Main video duration: {main_duration:.2f} seconds")
    print(f"Hipnoz video duration: {hipnoz_duration:.2f} seconds")
    print(f"Random start time for hipnoz: {random_start:.2f} seconds")
    print(f"Main video height: {main_height}")
    print(f"Hipnoz video height: {hipnoz_height}")

    # FFmpeg command - updated version
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-i', input_video,
        '-i', hipnoz_video,
        '-filter_complex',
        f'[0:v]setpts=PTS-STARTPTS,scale={width}:{main_height}[main];'  # Main video with original speed
        f'[1:v]trim=start={random_start}:duration={main_duration},setpts=PTS-STARTPTS,scale={width}:{hipnoz_height}[hipnoz];'  # Hipnoz video
        f'[main][hipnoz]vstack=inputs=2[out]',  # Stack videos vertically
        '-map', '[out]',
        '-map', '0:a?',  # Copy audio from main video if exists
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '28',
        '-c:a', 'aac',
        '-progress', 'pipe:1',
        output_video
    ]

    try:
        print(f"Starting video editing process...")
        print(f"Input video: {input_video}")
        print(f"Hipnoz video: {hipnoz_video}")
        print(f"Output video: {output_video}")
        print("\nProcessing video...")
        print("FFmpeg command:", " ".join(ffmpeg_cmd))
        
        # Run FFmpeg command with real-time output
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )

        # Monitor the process
        start_time = time.time()
        duration = None
        time_pattern = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})")
        
        while True:
            # Read both stdout and stderr
            stdout_line = process.stdout.readline() if process.stdout else None
            stderr_line = process.stderr.readline() if process.stderr else None
            
            # Get duration from stderr
            if stderr_line and duration is None:
                duration_match = time_pattern.search(stderr_line)
                if duration_match:
                    h, m, s, ms = map(int, duration_match.groups())
                    duration = h * 3600 + m * 60 + s + ms / 100
            
            # Print progress
            if stderr_line and "time=" in stderr_line:
                time_str = stderr_line.split("time=")[1].split()[0]
                h, m, s = map(float, time_str.split(":"))
                current_time = h * 3600 + m * 60 + s
                if duration:
                    progress = (current_time / duration) * 100
                    elapsed = time.time() - start_time
                    print(f"\rProgress: {progress:.1f}% (Time: {time_str}, Elapsed: {elapsed:.1f}s)", end="", flush=True)
            
            # Check if process is still running
            if process.poll() is not None:
                break
            
            # Small delay to prevent CPU overuse
            time.sleep(0.1)
        
        print("\n")  # New line after progress
        
        # Get the final status
        return_code = process.poll()
        
        if return_code == 0:
            print("Video editing completed successfully!")
            return True
        else:
            print("Error during video editing:")
            error_output = process.stderr.read() if process.stderr else "No error output available"
            print(error_output)
            return False
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return False

if __name__ == "__main__":
    edit_video() 