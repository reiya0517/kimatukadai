from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient,Step

# ユーザー登録フォーム
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
            'password1': 'パスワード',
            'password2': 'パスワード（確認）',
        }

# レシピ投稿フォーム
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'cooking_time', 'message', 'image']
        labels = {
            'title': 'タイトル',
            'cooking_time': '調理時間（分）',
            'message': '投稿者からの一言',
            'image': '画像',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

# 材料入力フォーム
class IngredientForm(forms.ModelForm):
    quantity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'min': 0,
            'step': 1,
            'class': 'form-control',
        }),
        label='量',
    )

    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'unit']
        labels = {
            'name': '材料名',
            'unit': '単位',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '材料名：'}),
            'unit': forms.Select(),

        }


# 材料フォームセット（1レシピに対して複数の材料を入力可能）
IngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    form=IngredientForm,
    extra=3,
    can_delete=True
)


# 作り方フォーム
class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['description']
        labels = {'description': '作り方'}
        widgets = {'description': forms.Textarea(attrs={'rows': 2, 'placeholder': '例：野菜を切る'})}

StepFormSet = inlineformset_factory(
    Recipe,
    Step,
    form=StepForm,
    extra=3,
    can_delete=True
)

