# core/management/commands/resize_to_a3.py

from django.core.management.base import BaseCommand
from PIL import Image
import os

A3_WIDTH, A3_HEIGHT = 3508, 4961  # A3 at 300 DPI

class Command(BaseCommand):
    help = "Resize PNG image to A3. Optionally fill the page with --fill."

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Path to the input PNG file')
        parser.add_argument('output_file', type=str, help='Path to save the resized PNG file')
        parser.add_argument('--fill', action='store_true', help='Fill the A3 canvas')

    def handle(self, *args, **options):
        input_file = options['input_file']
        output_file = options['output_file']
        fill = options['fill']

        if not os.path.exists(input_file):
            self.stderr.write(f"Input file does not exist: {input_file}")
            return

        with Image.open(input_file) as img:
            img = img.convert("RGBA")

            scale_w = A3_WIDTH / img.width
            scale_h = A3_HEIGHT / img.height

            if fill:
                scale = max(scale_w, scale_h)  # cover entire A3
            else:
                scale = min(scale_w, scale_h)  # fit inside A3

            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            if fill:
                # Center on A3 white canvas
                background = Image.new("RGBA", (A3_WIDTH, A3_HEIGHT), (255, 255, 255, 255))
                offset = ((A3_WIDTH - new_w) // 2, (A3_HEIGHT - new_h) // 2)
                background.paste(img, offset, img)
                img = background

            img.save(output_file, "PNG", dpi=(300, 300))
            self.stdout.write(f"Image saved as {output_file} with A3 size")

