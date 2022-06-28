from rest_framework import serializers
from django.core.files.uploadedfile import SimpleUploadedFile

import base64
import uuid
import tempfile


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        data = data.strip('data:image/')
        index = data.find(';')
        content_type = data[:index]
        data = data[index + 8:]
        image_data = base64.b64decode(data)
        filename = uuid.uuid4().hex
        with tempfile.TemporaryFile() as image:
            image.write(image_data)
            image.seek(0)
            file = SimpleUploadedFile(
                name=f'{filename}.{content_type}',
                content=image.read(),
                content_type=f'image/{content_type}'
            )
        return super().to_internal_value(file)



