
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import numpy as np

def crop_image(img):
    try:
        # Check if empty
        if img is None or img.size == 0:
            return img
            
        # Determine background color from corners (top-left)
        bg_color = img[0, 0]
        
        # Calculate difference from background
        diff = np.abs(img - bg_color)
        
        # If image has alpha, also separate mask
        if img.shape[2] == 4:
            # If alpha is 0, it is background
            alpha = img[:, :, 3]
            mask_content = alpha > 0
        else:
            # For RGB, check if pixel differs from bg_color significantly
            # Sum differences across channels
            mask_content = np.sum(diff, axis=2) > 0.05  # Tolerance
            
        # If the image is completely blank/background, return original
        if not np.any(mask_content):
            return img

        # Find coordinates of content
        coords = np.argwhere(mask_content)
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        
        # Add a tiny padding to not cut off text
        pad = 5
        y0 = max(0, y0 - pad)
        y1 = min(img.shape[0], y1 + pad)
        x0 = max(0, x0 - pad)
        x1 = min(img.shape[1], x1 + pad)
        
        cropped = img[y0:y1, x0:x1]
        print(f"Cropped image from {img.shape} to {cropped.shape}")
        return cropped
        
    except Exception as e:
        print(f"Error cropping image: {e}")
        return img

def combine_images():
    # Base path
    base_dir = r'd:\Users\HONOR\Desktop\base\2026\Results'
    
    # Image files
    img_files = [
        'Q4_Projection_Cost_Time.png',
        'Q4_Projection_Time_Env.png',
        'Q4_Projection_Cost_Env.png',
        'Q4_Projection_Combined_3D.png' 
    ]
    
    # Check if files exist
    images = []
    for f in img_files:
        path = os.path.join(base_dir, f)
        if os.path.exists(path):
            img = mpimg.imread(path)
            images.append(crop_image(img))
        else:
            print(f"File not found: {path} - Attempting to use Q4_LCA_3D_Pareto.png instead")
            alt_path = os.path.join(base_dir, 'Q4_LCA_3D_Pareto.png')
            if os.path.exists(alt_path):
                img = mpimg.imread(alt_path)
                images.append(crop_image(img))
            else:
                print(f"Alternative file not found: {alt_path}")
                images.append(None)

    # Create figure with adjustable whitespace
    # Increased size significantly to (24, 18)
    fig, axes = plt.subplots(2, 2, figsize=(24, 18), gridspec_kw={'wspace': 0.02, 'hspace': 0.05})
    
    # Flatten axes
    ax = axes.flatten()
    
    # Titles corresponding to typical axes
    # Increased font size for titles
    titles = [
        'Projection: Cost vs Time',
        'Projection: Time vs Environment',
        'Projection: Cost vs Environment',
        '3D Combined View'
    ]
    
    for i in range(4):
        if i < len(images) and images[i] is not None:
            ax[i].imshow(images[i])
            ax[i].axis('off') 
            ax[i].set_title(titles[i], fontsize=20, pad=10)
        else:
            ax[i].axis('off')
            ax[i].text(0.5, 0.5, 'Image Missing', ha='center', fontsize=20)

    # Use tight_layout with small padding
    plt.tight_layout(pad=0.5)
    output_path = os.path.join(base_dir, 'Q4_Projections_Synthesized.png')
    # Increased DPI to 600 for high quality
    plt.savefig(output_path, dpi=600, bbox_inches='tight')
    print(f"Saved synthesized image to {output_path}")

if __name__ == "__main__":
    combine_images()
