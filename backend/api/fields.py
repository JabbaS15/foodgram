import base64
import binascii
import imghdr
import io
import uuid

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import ImageField


class Base64FieldMixin(object):
    """drf-extra-fields.fields к сожалению не импортируется ко мне"""
    EMPTY_VALUES = (None, "", [], (), {})

    @property
    def ALLOWED_TYPES(self):
        raise NotImplementedError

    @property
    def INVALID_FILE_MESSAGE(self):
        raise NotImplementedError

    @property
    def INVALID_TYPE_MESSAGE(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        self.trust_provided_content_type = kwargs.pop(
            "trust_provided_content_type", False)
        self.represent_in_base64 = kwargs.pop("represent_in_base64", False)
        super(Base64FieldMixin, self).__init__(*args, **kwargs)

    def to_internal_value(self, base64_data):
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, str):
            file_mime_type = None

            if ";base64," in base64_data:
                header, base64_data = base64_data.split(";base64,")
                if self.trust_provided_content_type:
                    file_mime_type = header.replace("data:", "")

            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            file_name = self.get_file_name(decoded_file)
            file_extension = self.get_file_extension(file_name, decoded_file)

            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            complete_file_name = file_name + "." + file_extension
            data = SimpleUploadedFile(
                name=complete_file_name,
                content=decoded_file,
                content_type=file_mime_type
            )

            return super(Base64FieldMixin, self).to_internal_value(data)

        raise ValidationError(_(
            "Invalid type. "
            "This is not an base64 string: {}".format(type(base64_data)))
        )

    def get_file_extension(self, filename, decoded_file):
        raise NotImplementedError

    def get_file_name(self, decoded_file):
        return str(uuid.uuid4())

    def to_representation(self, file):
        if self.represent_in_base64:
            if not file:
                return ""

            try:
                with open(file.path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                raise IOError("Error encoding file")
        else:
            return super(Base64FieldMixin, self).to_representation(file)


class Base64ImageField(Base64FieldMixin, ImageField):
    """
    A django-rest-framework field for handling image-uploads.
    It uses base64 for en-/decoding the contents of the file.
    """
    ALLOWED_TYPES = (
        "jpeg",
        "jpg",
        "png",
        "gif"
    )
    INVALID_FILE_MESSAGE = _("Please upload a valid image.")
    INVALID_TYPE_MESSAGE = _("The type of the image couldn't be determined.")

    def get_file_extension(self, filename, decoded_file):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow is not installed.")
        extension = imghdr.what(filename, decoded_file)

        if extension is None:
            try:
                image = Image.open(io.BytesIO(decoded_file))
            except (OSError, IOError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            extension = image.format.lower()

        extension = "jpg" if extension == "jpeg" else extension
        return extension
