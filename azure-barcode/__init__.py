# requirements.txt
#
# azure-functions==1.3.1
# Pillow==7.2.0
# python-barcode==0.13.1

import logging
from io import BytesIO
import base64, json

from barcode.codex import Code128, Code39, Gs1_128, PZN
from barcode.ean import EAN13, EAN14, EAN8, JAN
from barcode.isxn import ISBN10, ISBN13, ISSN
from barcode.itf import ITF
from barcode.upc import UPCA
from barcode.writer import ImageWriter

import azure.functions as func


BARCODES = {
    "ean8": EAN8, "ean13": EAN13, "ean": EAN13, "gtin": EAN14, "ean14": EAN14,
    "jan": JAN, "upc": UPCA, "upca": UPCA,
    "isbn": ISBN13, "isbn13": ISBN13, "gs1": ISBN13,
    "isbn10": ISBN10, "issn": ISSN,
    "code39": Code39, "code128": Code128,
    "pzn": PZN, "itf": ITF, "gs1_128": Gs1_128,
}

def main(req: func.HttpRequest) -> func.HttpResponse:

    code = req.params.get('code','').strip().lower()
    value = req.params.get('value','').strip()
    output = req.params.get('output','').strip().lower()

    barcode_object = BARCODES.get(code)
    if not barcode_object:
        return func.HttpResponse(f"Input barcode type and value, available barcode types: {', '.join(list(BARCODES.keys()))}" , status_code=500)

    try:
        fd = BytesIO()
        barcode_object(value, writer=ImageWriter()).write(fd)
        fd.seek(0)
        arr = fd.read(-1)
        if output=="base64":
            s = base64.encodebytes(arr).decode().replace('\n', '')
            return func.HttpResponse(json.dumps({"code":s}), status_code=200, mimetype="application/json")
        else:
            return func.HttpResponse(arr, status_code=200, mimetype="image/jpg")
    except Exception as exc:
        return func.HttpResponse(f"Error: {str(exc)}" , status_code=500)



