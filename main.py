import os
import random
import subprocess
import time

def add_silence_and_combine(input_folder, min_silence, max_silence, output_file):
    audio_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".mp3")]
    audio_files.sort()  # Sort to maintain order
    
    temp_file_list = "file_list.txt"
    timestamp = int(time.time())
    with open(temp_file_list, "w") as f:
        for i, audio in enumerate(audio_files):
            f.write(f"file '{audio}'\n")
            silence_duration = random.randint(min_silence, max_silence)
            silence_file = f"silence_{timestamp}_{i}_{silence_duration}.mp3"
            
            # Generate silence file with -y flag to overwrite
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(silence_duration * 60), "-q:a", "9", silence_file
            ], check=True)
            
            f.write(f"file '{silence_file}'\n")
    
    # Combine files using ffmpeg with -y flag
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", temp_file_list, "-c", "copy", output_file
    ], check=True)
    
    # Cleanup
    os.remove(temp_file_list)
    for silence_file in os.listdir("."):
        if silence_file.startswith("silence_") and silence_file.endswith(".mp3"):
            os.remove(silence_file)

def get_audio_duration(audio_file):
    probe_cmd = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_file
    ], capture_output=True, text=True, check=True)
    return float(probe_cmd.stdout.strip())

def create_mega_video(input_video, input_audio, output_video):
    # Get audio duration
    duration = get_audio_duration(input_audio)
    print(f"Estimated video duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    
    print("Starting video creation...")
    start_time = time.time()
    
    # Create a video that loops the input video for the duration of the audio
    process = subprocess.Popen([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", input_video,
        "-i", input_audio, "-shortest", "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", output_video,
        "-progress", "pipe:1"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        if "out_time_ms" in line:
            current_time = int(line.split('=')[1]) / 1000000  # convert microseconds to seconds
            progress = (current_time / duration) * 100
            elapsed = time.time() - start_time
            eta = (elapsed / current_time) * (duration - current_time) if current_time > 0 else 0
            print(f"\rProgress: {progress:.1f}% | Time elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s", end="")
    
    process.wait()
    total_time = time.time() - start_time
    print(f"\nVideo creation completed in {total_time:.2f} seconds")

def create_mega_image_video(input_image, input_audio, output_video):
    # Get audio duration first
    duration = get_audio_duration(input_audio)
    print(f"Estimated video duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    
    print("Starting video creation...")
    start_time = time.time()
    
    # Create a video from the static image that matches the audio duration
    process = subprocess.Popen([
        "ffmpeg", "-y", "-loop", "1", "-framerate", "1", "-i", input_image,
        "-i", input_audio, "-c:v", "h264_amf", "-quality", "speed",
        "-rc", "cqp", "-qp_i", "51", "-qp_p", "51", "-vf", "scale=256:144",
        "-r", "1", "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "32k",
        "-max_muxing_queue_size", "1024", "-pix_fmt", "yuv420p", "-shortest",
        output_video
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    while True:
        output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    process.wait()
    total_time = time.time() - start_time
    print(f"\nVideo creation completed in {total_time:.2f} seconds")

# Usage
add_silence_and_combine("audios", 10, 30, "mega_audio.mp3")
# Choose either video or image as input
# create_mega_video("infinite_silence.mp4", "mega_audio.mp3", "mega_video.mp4")
create_mega_image_video("image.png", "mega_audio.mp3", "mega_image_video.mp4")
