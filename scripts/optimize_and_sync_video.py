import os
import shutil
import subprocess
import imageio_ffmpeg

def optimize_video():
    src = "marketing/don_aurelius_tutorial.mp4"
    temp_opt = "marketing/don_aurelius_tutorial_optimized.mp4"
    dest = "docs/assets/don_aurelius_tutorial.mp4"

    if not os.path.exists(src):
        print(f"Error: {src} not found!")
        return False

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg: {ffmpeg_exe}")
    print(f"Optimizing {src} with +faststart for zero-lag web and mobile streaming...")

    cmd = [
        ffmpeg_exe, "-y",
        "-i", src,
        "-movflags", "+faststart",
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-preset", "faster",
        "-c:a", "aac",
        "-b:a", "192k",
        temp_opt
    ]
    
    subprocess.run(cmd, check=True)

    orig_size = os.path.getsize(src) / (1024 * 1024)
    opt_size = os.path.getsize(temp_opt) / (1024 * 1024)
    print(f"Original size: {orig_size:.2f} MB -> Optimized size: {opt_size:.2f} MB")

    # Replace original and update docs
    shutil.move(temp_opt, src)
    shutil.copy2(src, dest)
    print(f"Successfully copied stream-optimized 16:9 widescreen video to {dest}")
    return True

if __name__ == "__main__":
    optimize_video()
