from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, RecipeForm,IngredientFormSet
from .models import Recipe, Comment
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required


# トップページ
def index(request):
    new_recipes = Recipe.objects.order_by('-created_at')[:5]
    ranked_recipes = Recipe.objects.annotate(
        favorite_count=Count('favorited_by')
    ).order_by('-favorite_count')[:5]

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
            return redirect('login')  # 登録後ログイン画面へ
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
            return redirect('index')  # ログイン成功でトップへ
        else:
            error = "ユーザー名またはパスワードが違います"
            return render(request, 'reciprs/login.html', {'error': error})
    return render(request, 'reciprs/login.html')


# ログアウト
def logout_view(request):
    logout(request)
    return redirect('login')


# レシピ投稿
@login_required  # ← ログインしていないと投稿できないようにします
def post_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = IngredientFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # フォームから Recipe オブジェクトを作る（まだ保存しない）
            recipe = form.save(commit=False)
            # 現在ログイン中のユーザーを投稿者(author)に設定
            recipe.author = request.user
            recipe.save()  # データベースに保存

            # 材料のフォームセットを処理
            ingredients = formset.save(commit=False)
            for ingredient in ingredients:
                ingredient.recipe = recipe  # 紐付ける
                ingredient.save()

            return redirect('index')
    else:
        form = RecipeForm()
        formset = IngredientFormSet()

    return render(request, 'reciprs/post_recipe.html', {
        'form': form,
        'ingredient_formset': formset
    })



# レシピ詳細
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, 'reciprs/recipe_detail.html', {'recipe': recipe})


# レシピ検索
def search_recipes(request):
    query = request.GET.get('q')  # 検索キーワード取得
    results = []
    if query:
        results = Recipe.objects.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        )
        ranked_recipes = Recipe.objects.annotate(num_favorites=Count('favorited_by')).order_by('-num_favorites')[:5]
    return render(request, 'reciprs/search_results.html', {'query': query, 'results': results,  'ranked_recipes': ranked_recipes})


# お気に入り切り替え
def toggle_favorite(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect('login')

    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    if user in recipe.favorited_by.all():
        recipe.favorited_by.remove(user)
    else:
        recipe.favorited_by.add(user)
    return redirect('recipe_detail', recipe_id=recipe.id)


# コメント追加
def add_comment(request, recipe_id):
    if not request.user.is_authenticated:
        return redirect('login')

    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(recipe=recipe, user=request.user, content=content)
    return redirect('recipe_detail', recipe_id=recipe.id)


# お気に入りレシピ表示
def favorites_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    favorite_recipes = Recipe.objects.filter(favorited_by=request.user)
    return render(request, 'reciprs/favorites.html', {'recipes': favorite_recipes})


# 買い物リスト表示（仮）
def shopping_list_view(request):
    return render(request, 'reciprs/shopping_list.html')
