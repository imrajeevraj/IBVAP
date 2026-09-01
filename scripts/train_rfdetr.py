import os
import argparse
from rfdetr import RFDETRSmall

def train(dataset_dir, output_dir, epochs, batch_size):
    print(f"Starting RF-DETR Fine-tuning...")
    print(f"Dataset: {dataset_dir}")
    print(f"Output: {output_dir}")
    print(f"Epochs: {epochs}, Batch Size: {batch_size}")
    
    # Initialize pretrained RF-DETR Small model
    model = RFDETRSmall()
    
    # Since we are on CPU and doing a mock fine-tune, we use a tiny LR
    # and minimal gradient accumulation steps.
    # We rely on the high-level API as requested by the prompt.
    try:
        model.train(
            dataset_dir=dataset_dir,
            output_dir=output_dir,
            epochs=epochs,
            batch_size=batch_size,
            grad_accum_steps=1,
            lr=1e-4,
            device='cpu' # Force CPU
        )
        print("Training completed successfully.")
    except Exception as e:
        print(f"Training failed: {e}")
        # If the API signature differs slightly in this version of rfdetr, fallback
        print("Attempting fallback training signature...")
        model.train(
            data=dataset_dir,
            epochs=epochs,
            batch=batch_size,
            project=output_dir,
            name="RFDETR-EXP-001",
            workers=0,
            val=False
        )
        print("Fallback training completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="benchmark/rfdetr_dataset")
    parser.add_argument("--output", type=str, default="benchmark/results/rfdetr/finetuned/RFDETR-EXP-001")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=1)
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    train(args.dataset, args.output, args.epochs, args.batch_size)
