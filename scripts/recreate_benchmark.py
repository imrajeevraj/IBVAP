import os
import cv2
import numpy as np

def recreate_benchmark():
    print("Recreating dummy Benchmark Directory...")
    
    img_dir = "benchmark/images/test"
    lbl_dir = "benchmark/labels/test"
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)
    
    # Create 200 frames
    for i in range(1, 201):
        filename = f"frame_{i:06d}"
        
        # Create a blank black image (640x480)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add a dummy white box for the model to detect (so it's not totally empty)
        # Random size and location
        x = np.random.randint(50, 500)
        y = np.random.randint(50, 300)
        w = np.random.randint(50, 100)
        h = np.random.randint(50, 150)
        
        # Draw a white rectangle
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), -1)
        
        cv2.imwrite(f"{img_dir}/{filename}.jpg", img)
        
        # Create dummy label: class cx cy w h (normalized)
        cls_id = np.random.choice([0, 1]) # person or vehicle
        cx = (x + w/2) / 640.0
        cy = (y + h/2) / 480.0
        nw = w / 640.0
        nh = h / 480.0
        
        with open(f"{lbl_dir}/{filename}.txt", "w") as f:
            f.write(f"{cls_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")
            
    print(f"Created 200 dummy frames in {img_dir} and {lbl_dir}.")

if __name__ == "__main__":
    recreate_benchmark()
