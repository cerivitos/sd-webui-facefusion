# coding=utf-8
import os
import tempfile
from typing import Union, List

from PIL import Image

from facefusion.core import run


def get_images_from_list(imgs: Union[List, None]):
	result = []
	tmp_paths = []
	if imgs is None:
		return result, tmp_paths
	for x in imgs:
		try:
			path = os.path.abspath(x.name)
		except:
			import base64, io
			if 'base64,' in x:  # check if the base64 string has a data URL scheme
				base64_data = x.split('base64,')[-1]
			else:
				base64_data = x
			img_bytes = base64.b64decode(base64_data)
			source_img = Image.open(io.BytesIO(img_bytes))
			source_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
			source_img.save(source_path)
			path = source_path
			tmp_paths.append(source_path)
		result.append(path)
	return result, tmp_paths


def swap_face(
	source_img: Image.Image,
	target_img: Image.Image,
	provider: str,
	detector_score: float,
	mask_blur: float,
	skip_nsfw: bool = True,
	source_imgs: Union[List, None] = None
) -> Image.Image:
	if isinstance(source_img, str):  # source_img is a base64 string
		import base64, io
		if 'base64,' in source_img:  # check if the base64 string has a data URL scheme
			base64_data = source_img.split('base64,')[-1]
			img_bytes = base64.b64decode(base64_data)
		else:
			# if no data URL scheme, just decode
			img_bytes = base64.b64decode(source_img)
		source_img = Image.open(io.BytesIO(img_bytes))
	source_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
	source_img.save(source_path)
	target_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
	target_img.save(target_path)
	output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name

	# call FaceFusion
	source_path_list, tmp_paths = get_images_from_list(source_imgs)
	paths = [source_path, *source_path_list]
	result = run(
		source_path=paths, target_path=target_path, output_path=output_path,
		provider=provider, detector_score=detector_score, mask_blur=mask_blur, skip_nsfw=skip_nsfw
	)
	if result:
		result_image = Image.open(result)
	else:
		result_image = target_img

	# clear temp files
	tmp_paths.append(source_path)
	tmp_paths.append(target_path)
	tmp_paths.append(output_path)
	for tmp in tmp_paths:
		os.remove(tmp)
	return result_image
