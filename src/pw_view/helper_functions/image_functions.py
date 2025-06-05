
import io
import base64

from PIL import Image, ImageDraw

def get_image_bytes(pillow_image: Image.Image):
    img_byte_arr = io.BytesIO()
    pillow_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def image_to_base64(img: Image.Image):
    img_bytes = get_image_bytes(img)
    encoded = base64.b64encode(img_bytes.read()).decode('utf-8')
    return encoded

def recolor(img: Image, target_color: str, new_color: str) -> Image:
	
	data = img.getdata()
	new_data = []
	
	for pixel in data:
		if pixel[:3] == target_color:
			new_data.append(new_color + (pixel[3],))  # Preserve alpha
		else:
			new_data.append(pixel)
	img.putdata(new_data)

	return img