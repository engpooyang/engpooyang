"""ElevenLabs custom tool: Provide transfer destination for call routing."""

from src.models.schemas import TransferCallRequest, TransferCallResponse


def handle_transfer_call(request: TransferCallRequest) -> TransferCallResponse:
    """Return the transfer details for ElevenLabs to execute the Transfer-to-Number system tool.

    The actual transfer is performed by ElevenLabs' built-in Transfer-to-Number
    capability. This tool validates and confirms the transfer destination.
    """
    if not request.destination_number:
        return TransferCallResponse(
            success=False,
            message="No destination number provided.",
        )

    return TransferCallResponse(
        success=True,
        message=f"Transferring to {request.destination_number}. {request.caller_message}",
    )
