from django.contrib import admin
from .models import VoiceCommand
from django import forms

class VoiceCommandForm(forms.ModelForm):
	text = forms.CharField(
		widget=forms.TextInput(attrs={
			'placeholder': 'e.g. lock doors',
		}),
		help_text="Main command phrase. Example: lock doors"
	)
	synonyms = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={
			'placeholder': 'e.g. lock, secure, close',
			'rows': 3,
		}),
		help_text="Comma-separated synonyms. Example: lock, secure, close"
	)

	def clean_synonyms(self):
		data = self.cleaned_data['synonyms']
		# Remove spaces around commas, ensure proper format
		cleaned = ','.join([s.strip() for s in data.split(',') if s.strip()])
		return cleaned

	class Meta:
		model = VoiceCommand
		fields = '__all__'

@admin.register(VoiceCommand)
class VoiceCommandAdmin(admin.ModelAdmin):
	form = VoiceCommandForm
	list_display = ("text", "enabled", "created_at", "updated_at")
	search_fields = ("text", "synonyms")
	list_filter = ("enabled",)

# Register your models here.
