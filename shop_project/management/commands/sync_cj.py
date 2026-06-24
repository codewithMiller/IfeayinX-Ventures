from django.core.management.base import BaseCommand
from shop_project.cj_api import get_token, fetch_clothing
from shop_project.models import Product, ProductVariant, VariantImage, Category


def parse_price(price_val):
    if not price_val:
        return 0
    price_str = str(price_val).split('--')[0].strip()
    try:
        return float(price_str)
    except ValueError:
        return 0


class Command(BaseCommand):
    help = "Sync Ankara clothing/fabric from CJDropshipping"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of relevant products to import"
        )
        parser.add_argument(
            "--max-pages",
            type=int,
            default=1,
            help="Number of pages to fetch per keyword"
        )

    def handle(self, *args, **options):
        max_products = options.get("limit")
        max_pages = options.get("max_pages", 1)

        token = get_token()
        if not token:
            self.stdout.write(self.style.ERROR("Auth failed. Check your CJ_API_KEY."))
            return

        category, _ = Category.objects.get_or_create(name="Ankara")

        products = fetch_clothing(
            token,
            max_pages=max_pages,
            max_products=max_products
        )

        if not products:
            self.stdout.write(self.style.WARNING("No products returned from CJ."))
            return

        added_count = 0
        updated_count = 0
        existing_count = 0
        skipped_missing = 0

        for item in products:
            pid = item.get("pid")
            name = item.get("productNameEn", "Unnamed")
            price = parse_price(item.get("sellPrice", 0))
            image = item.get("productImage", "")

            if not pid or not image:
                skipped_missing += 1
                self.stdout.write(f"Skipped missing pid/image: {name}")
                continue

            product, created = Product.objects.get_or_create(
                cj_pid=pid,
                defaults={
                    "name": name,
                    "category": category,
                    "is_cj_product": True,
                }
            )

            if created:
                variant = ProductVariant.objects.create(
                    product=product,
                    price=price,
                    stock=99,
                    available=True
                )
                VariantImage.objects.create(
                    variant=variant,
                    image_url=image
                )
                added_count += 1
                self.stdout.write(self.style.SUCCESS(f"Added: {name}"))
            else:
                changed = False

                if product.name != name:
                    product.name = name
                    changed = True

                if product.category_id != category.id:
                    product.category = category
                    changed = True

                if not product.is_cj_product:
                    product.is_cj_product = True
                    changed = True

                if changed:
                    product.save()

                variant = product.variants.first()
                if variant:
                    if variant.price != price:
                        variant.price = price
                        variant.save()
                        updated_count += 1
                else:
                    variant = ProductVariant.objects.create(
                        product=product,
                        price=price,
                        stock=99,
                        available=True
                    )
                    VariantImage.objects.create(
                        variant=variant,
                        image_url=image
                    )
                    updated_count += 1

                existing_count += 1
                self.stdout.write(f"Exists/checked: {name}")

        self.stdout.write(self.style.SUCCESS(
            f"Sync complete. Added={added_count}, Existing={existing_count}, "
            f"Updated={updated_count}, SkippedMissing={skipped_missing}"
        ))
