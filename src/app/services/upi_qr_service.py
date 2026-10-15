
import base64
from io import BytesIO
from urllib.parse import urlencode

import qrcode

from src.app.core.security import settings
from src.app.core.exceptions import (
    UPIConfigurationException,
    UPIQRNotAvailableException,
)
from src.app.models.donation import Donation


def generate_upi_qr(donation: Donation) -> dict:
    upi_vpa = settings.YMCA_UPI_VPA
    payee_name = settings.YMCA_UPI_PAYEE_NAME

    if not upi_vpa or not payee_name:
        raise UPIConfigurationException()

    if donation.payment_method != "UPI":
        raise UPIQRNotAvailableException(
            "UPI QR is available only for UPI donations"
        )

    if donation.payment_status != "PENDING":
        raise UPIQRNotAvailableException(
            "UPI QR is available only for pending donations"
        )

    upi_params = {
        "pa": upi_vpa,
        "pn": payee_name,
        "am": format(donation.amount, ".2f"),
        "cu": "INR",
        "tr": str(donation.id),
        "tn": f"YMCA Donation {str(donation.id)[:8]}",
    }

    upi_uri = "upi://pay?" + urlencode(upi_params)

    qr_image = qrcode.make(upi_uri)
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")

    encoded_image = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    return {
        "donation_id": str(donation.id),
        "amount": donation.amount,
        "payment_status": donation.payment_status,
        "upi_uri": upi_uri,
        "qr_code_data_url": f"data:image/png;base64,{encoded_image}",
    }
