from django.db import models
from django.contrib.auth.models import User

# レシピモデル
class Recipe(models.Model):
    title = models.CharField("タイトル", max_length=100)
    cooking_time = models.IntegerField("調理時間（分）", null=True, blank=True)
    message = models.TextField("投稿者からの一言", blank=True)
    image = models.ImageField("画像", upload_to='recipe_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    favorited_by = models.ManyToManyField(User, related_name='favorite_recipes', blank=True)

    def __str__(self):
        return self.title

# 材料モデル
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField("材料名", max_length=100)
    quantity = models.IntegerField(null=True, blank=True)
    unit = models.CharField("単位", max_length=20, choices=[
        ('個', '個'), ('本', '本'), ('枚', '枚'), ('匹', '匹'), ('尾', '尾'), ('合','合'),
        ('切れ', '切れ'), ('大さじ', '大さじ'), ('小さじ', '小さじ'),
        ('ml', 'ml'), ('cc', 'cc'), ('g', 'g'), ('kg', 'kg'),
        ('袋', '袋'), ('適量', '適量'), ('少々', '少々'), ('ひとつまみ', 'ひとつまみ'),
    ])

    def __str__(self):
        return f"{self.name} {self.quantity}{self.unit}"

# コメントモデル
class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField("コメント内容")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} のコメント"
