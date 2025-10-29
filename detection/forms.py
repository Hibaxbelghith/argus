from django import forms
from .models import DetectionResult


class ImageUploadForm(forms.ModelForm):
    """Form for uploading images for object detection"""
    
    class Meta:
        model = DetectionResult
        fields = ['original_image']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'imageUpload'
            })
        }
        labels = {
            'original_image': 'Choose an image for object detection'
        }
    
    def clean_original_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('original_image')
        
        if image:
            # Check file size (limit to 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 10MB )")
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            ext = image.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise forms.ValidationError(
                    f"Unsupported file extension. Allowed: {', '.join(valid_extensions)}"
                )
        
        return image
