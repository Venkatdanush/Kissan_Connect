# Plant Disease Detection Model Integration Guide

## Overview
This guide explains how to integrate your trained `plant_disease_model.h5` with the Kissan Connect disease detection system.

## Current Implementation
The current system uses mock predictions for demonstration. To integrate your actual model, follow these steps:

## Step 1: Install Required Dependencies

Add these to your requirements.txt or install manually:

```bash
pip install tensorflow
pip install pillow
pip install numpy
```

## Step 2: Place Your Model File

1. Create a `models` directory in your `main` app:
   ```
   main/
   ├── models/
   │   └── plant_disease_model.h5
   ├── templates/
   ├── static/
   └── ...
   ```

2. Copy your `plant_disease_model.h5` file to `main/models/`

## Step 3: Update views.py

Replace the mock prediction functions in `main/views.py` with the actual model code:

### 3.1 Add model loading function

```python
# Add to the top of views.py after other imports
from django.conf import settings
import tensorflow as tf
import numpy as np
from PIL import Image
import os

# Global model variable
disease_model = None

def load_disease_model():
    """Load the trained plant disease detection model"""
    global disease_model
    
    if disease_model is None:
        try:
            model_path = os.path.join(settings.BASE_DIR, 'main', 'models', 'plant_disease_model.h5')
            print(f"Loading model from: {model_path}")
            disease_model = tf.keras.models.load_model(model_path)
            print("✅ Disease detection model loaded successfully")
            return disease_model
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return None
    
    return disease_model
```

### 3.2 Replace the process_plant_image function

```python
def process_plant_image(image_file):
    """Process uploaded plant image using the trained model"""
    
    try:
        # Load the model
        model = load_disease_model()
        if model is None:
            return {
                'success': False,
                'error': 'Disease detection model could not be loaded.'
            }
        
        # Load and preprocess the image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image to model input size (adjust based on your model requirements)
        # Common sizes: 224x224, 256x256, 299x299
        target_size = (224, 224)  # Adjust this to match your model's input size
        image = image.resize(target_size)
        
        # Convert to numpy array and normalize
        img_array = np.array(image)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize pixel values to [0, 1]
        
        # Make prediction
        predictions = model.predict(img_array)
        
        # Define your disease classes (ADJUST THESE TO MATCH YOUR MODEL)
        disease_classes = [
            'Apple___Apple_scab',
            'Apple___Black_rot',
            'Apple___Cedar_apple_rust',
            'Apple___healthy',
            'Blueberry___healthy',
            'Cherry_(including_sour)___Powdery_mildew',
            'Cherry_(including_sour)___healthy',
            'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
            'Corn_(maize)___Common_rust_',
            'Corn_(maize)___Northern_Leaf_Blight',
            'Corn_(maize)___healthy',
            'Grape___Black_rot',
            'Grape___Esca_(Black_Measles)',
            'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
            'Grape___healthy',
            'Orange___Haunglongbing_(Citrus_greening)',
            'Peach___Bacterial_spot',
            'Peach___healthy',
            'Pepper,_bell___Bacterial_spot',
            'Pepper,_bell___healthy',
            'Potato___Early_blight',
            'Potato___Late_blight',
            'Potato___healthy',
            'Raspberry___healthy',
            'Soybean___healthy',
            'Squash___Powdery_mildew',
            'Strawberry___Leaf_scorch',
            'Strawberry___healthy',
            'Tomato___Bacterial_spot',
            'Tomato___Early_blight',
            'Tomato___Late_blight',
            'Tomato___Leaf_Mold',
            'Tomato___Septoria_leaf_spot',
            'Tomato___Spider_mites Two-spotted_spider_mite',
            'Tomato___Target_Spot',
            'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
            'Tomato___Tomato_mosaic_virus',
            'Tomato___healthy'
        ]
        
        # Get the predicted class and confidence
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index]) * 100
        predicted_disease = disease_classes[predicted_class_index]
        
        # Clean up the disease name for display
        clean_disease_name = predicted_disease.replace('___', ' - ').replace('_', ' ').title()
        
        return {
            'success': True,
            'disease_type': clean_disease_name,
            'confidence': round(confidence, 2),
            'description': f"AI detected: {clean_disease_name} with {round(confidence, 2)}% confidence"
        }
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to process the image. Please try again with a different image.'
        }
```

### 3.3 Remove or comment out the mock functions

Comment out or remove these functions:
- `get_mock_disease_prediction()`

## Step 4: Model Configuration

### 4.1 Determine your model's input size
Check your model's expected input shape:

```python
# Add this temporary code to see your model's input shape
model = tf.keras.models.load_model('path/to/your/model.h5')
print("Model input shape:", model.input_shape)
```

### 4.2 Update disease classes
Replace the `disease_classes` list with the actual classes your model was trained on.

### 4.3 Preprocessing adjustments
Adjust the image preprocessing based on how your model was trained:
- Input size (224x224, 256x256, etc.)
- Normalization method (divide by 255, standardization, etc.)
- Color channels (RGB, BGR, etc.)

## Step 5: Test the Integration

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to `/disease-detection/`

3. Upload a test image and verify the results

## Step 6: Error Handling

Monitor the console for any errors during model loading or prediction. Common issues:

- **Model not found**: Check the file path
- **Input shape mismatch**: Verify image preprocessing
- **Memory issues**: Large models may require more RAM
- **TensorFlow version**: Ensure compatibility between training and deployment environments

## Step 7: Performance Optimization

For production deployment:

1. **Model caching**: The model is loaded once and cached globally
2. **Image optimization**: Resize images before processing
3. **Async processing**: Consider using Celery for heavy model operations
4. **GPU support**: Enable GPU if available for faster inference

## Example Model Integration

Here's a complete example of how your `process_plant_image` function might look:

```python
def process_plant_image(image_file):
    """Process uploaded plant image using the trained model"""
    
    try:
        # Load model
        model = load_disease_model()
        if model is None:
            return get_mock_disease_prediction(image_file.name)  # Fallback to mock
        
        # Preprocess image
        image = Image.open(image_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image = image.resize((224, 224))  # Adjust to your model's input size
        img_array = np.array(image) / 255.0  # Normalize
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict
        predictions = model.predict(img_array)
        class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][class_index]) * 100
        
        # Your disease classes here
        disease_name = YOUR_DISEASE_CLASSES[class_index]
        
        return {
            'success': True,
            'disease_type': disease_name,
            'confidence': round(confidence, 2),
            'description': f"Detected: {disease_name}"
        }
        
    except Exception as e:
        print(f"Model prediction error: {str(e)}")
        # Fallback to mock prediction
        return get_mock_disease_prediction(image_file.name)
```

## Troubleshooting

### Common Issues:

1. **ImportError: No module named 'tensorflow'**
   ```bash
   pip install tensorflow
   ```

2. **Model file not found**
   - Check file path
   - Ensure model file is in the correct directory

3. **Invalid input shape**
   - Verify image preprocessing matches training data
   - Check model.input_shape

4. **Low accuracy**
   - Ensure preprocessing matches training preprocessing
   - Verify disease classes order
   - Check image quality and lighting

### Debug Mode:

Add debug prints to monitor the prediction process:

```python
print(f"Image shape after preprocessing: {img_array.shape}")
print(f"Prediction probabilities: {predictions[0]}")
print(f"Predicted class index: {class_index}")
print(f"Confidence: {confidence}%")
```

## Next Steps

1. Test with various plant images
2. Monitor accuracy and adjust preprocessing if needed
3. Implement model versioning for updates
4. Add logging for production monitoring
5. Consider A/B testing with different models

## Support

If you encounter issues:
1. Check Django logs for error messages
2. Verify TensorFlow/Keras version compatibility
3. Test model loading separately in a Python script
4. Ensure sufficient system memory for model loading

---

**Note**: The current implementation includes a fallback to mock predictions if the model fails to load, ensuring the system remains functional during development and testing.
