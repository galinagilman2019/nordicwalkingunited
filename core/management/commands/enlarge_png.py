import os
from PIL import Image
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Enlarge a PNG image by a fixed scale factor (1.195)"

    SCALE_FACTOR = 1.195  # Scale factor

    def add_arguments(self, parser):
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the input PNG image"
        )
        parser.add_argument(
            "output_path",
            type=str,
            help="Path to save the enlarged PNG image"
        )

    def handle(self, *args, **options):
        input_path = options["input_path"]
        output_path = options["output_path"]

        if not os.path.exists(input_path):
            self.stderr.write(self.style.ERROR(f"Input file does not exist: {input_path}"))
            return

        # Open image
        img = Image.open(input_path)

        # Calculate new size
        new_width = int(img.width * self.SCALE_FACTOR)
        new_height = int(img.height * self.SCALE_FACTOR)

        # Resize image with high-quality resampling
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save the result
        resized_img.save(output_path)
        self.stdout.write(self.style.SUCCESS(f"Image saved as {output_path} with size {new_width}x{new_height}"))
