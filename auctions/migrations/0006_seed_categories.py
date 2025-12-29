from django.db import migrations

def seed_categories(apps, schema_editor):
    Category = apps.get_model('auctions', 'Category')

    categories = [
        "Clothes",
        "Instrument",
        "Electronics",
        "Antique",
        "Books",
        "Paintings",
    ]

    for category in categories:
        Category.objects.get_or_create(categoryName=category)


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bid_id_alter_category_id_alter_comment_id_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_categories),
    ]
