from django import forms


class SalesUploadForm(forms.Form):
    file = forms.FileField(label="Sales XLSX file")

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Only .xlsx files are supported.")
        if f.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File must be 10 MB or smaller.")
        return f
