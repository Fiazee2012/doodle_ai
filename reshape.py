import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import cv2

def mnist_preprocess(input_data, canvas_size=280, target_size=(28, 28)):
    """
    Improved preprocessing to capture fast drawing with better line continuity

    Args:
    - input_data: List of drawing paths from frontend
    - canvas_size: Original canvas dimension
    - target_size: Final image size (default MNIST 28x28)

    Returns:
    - Preprocessed numpy array
    """
    # Create a PIL Image for more robust drawing
    canvas = Image.new('L', (canvas_size, 410), color=0)
    draw = ImageDraw.Draw(canvas)

    # Increase line thickness and use smoother drawing
    line_thickness = 20  # Adjustable thickness

    # Draw each path
    print("x" *20)
    print(input_data)
    for path in input_data:
        # If path has only one point, draw a small circle
        if len(path) == 1:
            x, y = path[0]
            draw.ellipse([x-line_thickness, y-line_thickness,
                          x+line_thickness, y+line_thickness], fill=255)
        else:
            # Draw connected lines with thickness
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i+1]

                # Draw thick line
                draw.line([x1, y1, x2, y2], fill=255, width=line_thickness)

    # Resize to target size using high-quality resampling
    pil_image = canvas.resize(target_size, Image.LANCZOS)

    # Convert to numpy array and normalize
    processed_array = np.array(pil_image).astype(np.float32) / 255.0

    # Optional: Threshold to create more defined image
    processed_array = (processed_array > 0.3).astype(np.float32)
    binary_image = (processed_array > 0.3).astype(np.float32)
    moments = cv2.moments(binary_image)


    if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Center the image
            rows, cols = binary_image.shape
            shift_x = cols/2 - cx
            shift_y = rows/2 - cy

            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            processed_array = cv2.warpAffine(binary_image, M, (cols, rows))

    # Save debug image
    plt.imsave("processed_debug.png", processed_array, cmap='gray')

    return processed_array

# Optional: Add a debugging function to visualize paths
def debug_paths(input_data, canvas_size=280):
    """
    Visualize the drawing paths for debugging
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 10))
    plt.xlim(0, canvas_size)
    plt.ylim(canvas_size, 0)  # Invert y-axis to match canvas coordinates

    for path in input_data:
        # Extract x and y coordinates
        xs = [point[0] for point in path]
        ys = [point[1] for point in path]

        # Plot the path
        plt.plot(xs, ys, '-o')

    plt.title('Drawing Paths')
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.savefig('path_debug.png')
    plt.close()