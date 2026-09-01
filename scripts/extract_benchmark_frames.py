import cv2
import os
import glob
import shutil

def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def extract_frames(video_path, output_dir, target_count, prefix="frame"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Extracting {target_count} frames from {video_path} (Total frames: {total_frames})")
    
    if target_count >= total_frames:
        step = 1
    else:
        step = total_frames // target_count
        
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    for i in range(target_count):
        frame_idx = i * step
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret: break
        
        out_name = os.path.join(output_dir, f"{prefix}_{count+1:06d}.jpg")
        cv2.imwrite(out_name, frame)
        count += 1
            
    cap.release()
    print(f"Extracted {count} frames to {output_dir}")

def main():
    print("Rebuilding Dataset from Source Videos...")
    base_dir = "benchmark"
    clear_directory(base_dir)
    
    # Train: VIRAT_S_000001.mp4 (70 frames), VIRAT_S_000002.mp4 (30 frames)
    # Valid: VIRAT_S_000003.mp4 (30 frames)
    # Test: VIRAT_S_000004.mp4 (200 frames) - IBVAP-GT-v2.0
    
    extract_frames("data/videos/virat/VIRAT_S_000001.mp4", "benchmark/images/train", 70, "v1")
    extract_frames("data/videos/virat/VIRAT_S_000002.mp4", "benchmark/images/train", 30, "v2")
    extract_frames("data/videos/virat/VIRAT_S_000003.mp4", "benchmark/images/valid", 30, "v3")
    extract_frames("data/videos/virat/VIRAT_S_000004.mp4", "benchmark/images/test", 200, "test")

    # Create empty label directories
    os.makedirs("benchmark/labels/train", exist_ok=True)
    os.makedirs("benchmark/labels/valid", exist_ok=True)
    os.makedirs("benchmark/labels/test", exist_ok=True)
    os.makedirs("benchmark/annotations/prelabels", exist_ok=True)
    
    print("Extraction complete. Dataset structure established.")

if __name__ == "__main__":
    main()
