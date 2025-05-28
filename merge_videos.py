import os
import subprocess

def merge_videos(output_file="output.mp4"):
    # Get all .mp4 and .mkv files in the current directory
    videos = sorted([f for f in os.listdir() if f.endswith(('.mp4', '.mkv'))])
    
    if not videos:
        print("No videos found in the current directory.")
        return
    
    # Create a temporary file list
    with open("file_list.txt", "w") as f:
        for video in videos:
            f.write(f"file '{video}'\n")
    
    # Run ffmpeg command to concatenate videos
    command = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt",
        "-c", "copy", output_file
    ]
    
    subprocess.run(command, check=True)
    
    # Clean up temporary file
    os.remove("file_list.txt")
    
    print(f"Videos merged successfully into {output_file}")

if __name__ == "__main__":
    merge_videos()
