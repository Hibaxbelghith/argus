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


class DetectionEditForm(forms.ModelForm):
    """Form for editing detection metadata"""
    
    class Meta:
        model = DetectionResult
        fields = ['title', 'description', 'tags', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Front Entrance Security Check'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add notes, observations, or context about this detection...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., security, entrance, daytime, suspicious'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Building A - Main Entrance'
            }),
        }
        labels = {
            'title': 'Title',
            'description': 'Description / Notes',
            'tags': 'Tags',
            'location': 'Location'
        }
        help_texts = {
            'tags': 'Separate tags with commas (e.g., security, entrance, night)',
        }
