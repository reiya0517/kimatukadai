from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from .forms import RegisterForm, RecipeForm, IngredientFormSet, StepFormSet
from .models import Recipe, Comment, Step, Ingredient, ShoppingListItem

# トップページ
def index(request):
    new_recipes = Recipe.objects.order_by('-created_at')[:5]
    ranked_recipes = Recipe.objects.annotate(
        favorite_count=Count('favorited_by')
    ).order_by('-favorite_count')[:10]
    return render(request, 'reciprs/index.html', {
        'new_recipes': new_recipes,
        'ranked_recipes': ranked_recipes,
    })

# 会員登録
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'reciprs/register.html', {'form': form})

# ログイン
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            error = "ユーザー名またはパスワードが違います"
            return render(request, 'reciprs/login.html', {'error': error})
    return render(request, 'reciprs/login.html')

# ログアウト
def logout_view(request):
    logout(request)
    return redirect('login')

# レシピ投稿
@login_required
def post_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = IngredientFormSet(request.POST, prefix='ingredients')
        step_formset = StepFormSet(request.POST, prefix='steps')

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            ingredient_formset.instance = recipe
            ingredient_formset.save()

            steps_data = []
            for step_form in step_formset.forms:
                if step_form.cleaned_data and not step_form.cleaned_data.get('DELETE', False):
                    description = step_form.cleaned_data.get('description')
                    if description:
                        steps_data.append(description)

            recipe.steps.all().delete()
            for i, description in enumerate(steps_data, start=1):
                Step.objects.create(recipe=recipe, order=i, description=description)

            return redirect('index')
    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet(prefix='ingredients')
        step_formset = StepFormSet(prefix='steps')

    return render(request, 'reciprs/post_recipe.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
    })

# レシピ編集
@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe, prefix='ingredients')
        step_formset = StepFormSet(request.POST, instance=recipe, prefix='steps')

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            ingredient_formset.save()

            steps_data = []
            for step_form in step_formset.forms:
                if step_form.cleaned_data and not step_form.cleaned_data.get('DELETE', False):
                    description = step_form.cleaned_data.get('description')
                    if description:
                        steps_data.append(description)

            recipe.steps.all().delete()
            for i, description in enumerate(steps_data, start=1):
                Step.objects.create(recipe=recipe, order=i, description=description)

            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe, prefix='ingredients')
        step_formset = StepFormSet(instance=recipe, prefix='steps')

    return render(request, 'reciprs/edit_recipe.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'recipe': recipe
    })

# レシピ削除
@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipe_detail', recipe_id=recipe.id)
    if request.method == 'POST':
        recipe.delete()
        return redirect('index')

# レシピ詳細
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'reciprs/recipe_detail.html', {'recipe': recipe})

# レシピ検索
def search_recipes(request):
    query = request.GET.get('q')
    results = Recipe.objects.none()
    ranked_recipes = Recipe.objects.none()

    if query:
        results = Recipe.objects.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        ).order_by('-created_at')

        ranked_recipes = results.annotate(num_favorites=Count('favorited_by')).order_by('-num_favorites')[:5]

    return render(request, 'reciprs/search_results.html', {
        'query': query,
        'results': results,
        'ranked_recipes': ranked_recipes,
    })

# お気に入り切り替え
@login_required
def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    if user in recipe.favorited_by.all():
        recipe.favorited_by.remove(user)
    else:
        recipe.favorited_by.add(user)
    return redirect('recipe_detail', recipe_id=recipe.id)

# コメント追加
@login_required
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(recipe=recipe, user=request.user, content=content)
    return redirect('recipe_detail', recipe_id=recipe.id)

# お気に入りレシピ表示
@login_required
def favorites_view(request):
    favorite_recipes = Recipe.objects.filter(favorited_by=request.user)
    favorites_new = favorite_recipes.order_by('-created_at')
    favorites_ranked = favorite_recipes.annotate(favorite_count=Count('favorited_by')).order_by('-favorite_count')
    return render(request, 'reciprs/favorites.html', {
        'favorites_new': favorites_new,
        'favorites_ranked': favorites_ranked,
    })

# 買い物リスト追加
@login_required
def add_to_shopping_list(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)

    defaults = {'unit': ingredient.unit}
    if ingredient.quantity is not None:
        defaults['quantity'] = ingredient.quantity

    ShoppingListItem.objects.get_or_create(
        user=request.user,
        ingredient=ingredient,
        defaults=defaults
    )
    return redirect('recipe_detail', recipe_id=ingredient.recipe.id)


# 買い物リスト表示
@login_required
def shopping_list(request):
    items = ShoppingListItem.objects.filter(user=request.user)
    return render(request, 'reciprs/shopping_list.html', {'items': items})

# 買い物リスト削除
@login_required
def delete_shopping_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
    if request.method == 'POST':
        item.delete()
    return redirect('shopping_list')

# 自分のレシピ一覧
@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'reciprs/my_recipes.html', {'recipes': recipes})
