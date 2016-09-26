import imghdr
import io
import os

from knowledge_repo.utils.dependencies import check_dependencies
from knowledge_repo._version import __optional_dependencies__

ALLOWED_IMAGE_TYPES = ('png', 'jpeg', 'gif')


def get_file_extension(filepath):
    return os.path.splitext(filepath)[1]


def is_allowed_image_format(img_file):
    """ Checks if a given file is an image"""
    return imghdr.what(img_file) in ALLOWED_IMAGE_TYPES


def is_pdf(filename):
    return get_file_extension(filename) == '.pdf'


def pdf_page_to_png(src_pdf, pagenum=0, resolution=154):
    """
    Returns specified PDF page as wand.image.Image png.
    :param PyPDF2.PdfFileReader src_pdf: PDF from which to take pages.
    :param int pagenum: Page number to take.
    :param int resolution: Resolution for resulting png in DPI.
    """

    check_dependencies(__optional_dependencies__['pdf'])
    # Import libraries within this function so as to avoid import-time dependence
    import PyPDF2
    from wand.image import Image  # TODO: When we start using this again, document which system-level libraries are required.

    dst_pdf = PyPDF2.PdfFileWriter()
    dst_pdf.addPage(src_pdf.getPage(pagenum))

    pdf_bytes = io.BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=resolution)
    img.convert("png")

    return img
