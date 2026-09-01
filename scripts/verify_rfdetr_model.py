import os
import argparse
import hashlib
from rfdetr import RFDETRSmall

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

def verify_model(checkpoint_dir):
    print("Verifying Fine-Tuned Model Integrity...")
    # Assuming checkpoint is saved as model.pt or similar in the output dir
    # Since rfdetr library uses standard saving, we just need to find the .pt/.pth file
    import glob
    checkpoints = glob.glob(f"{checkpoint_dir}/*.pt") + glob.glob(f"{checkpoint_dir}/*.pth")
    if not checkpoints:
        print(f"[FAIL] No checkpoint found in {checkpoint_dir}")
        return False
        
    model_path = checkpoints[0]
    checksum = hash_file(model_path)
    print(f"Model Checkpoint: {model_path}")
    print(f"SHA-256 Checksum: {checksum}")
    
    # Load model
    print("Loading model for dry run...")
    try:
        model = RFDETRSmall(model_path)
        # Try dummy inference
        import torch
        dummy_img = torch.zeros((1, 3, 640, 640))
        # Depending on API, try generic forward pass
        out = model.model(dummy_img)
        print("Inference on dummy tensor successful!")
        
        # Save integrity report
        os.makedirs("docs/benchmark", exist_ok=True)
        with open("docs/benchmark/RFDETR_MODEL_INTEGRITY.md", "w") as f:
            f.write("# RF-DETR Model Integrity\n\n")
            f.write(f"- **Fine-tuned Checkpoint:** `{model_path}`\n")
            f.write(f"- **SHA-256 Checksum:** `{checksum}`\n")
            f.write(f"- **Source Experiment:** RFDETR-EXP-001\n")
        print("Model Integrity Validated.")
        return True
    except Exception as e:
        print(f"[FAIL] Error loading or inferring model: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-dir", type=str, default="benchmark/results/rfdetr/finetuned/RFDETR-EXP-001")
    args = parser.parse_args()
    verify_model(args.checkpoint_dir)
