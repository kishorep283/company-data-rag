import tempfile
from pathlib import Path

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from langchain_community.document_loaders import PyMuPDFLoader


def load_pdf(file_path: str | Path):
    """Load a PDF into LangChain documents, one document per page."""
    return PyMuPDFLoader(str(file_path)).load()


class PDFUploadView(APIView):
    """Receive a PDF from the dashboard and load it into LangChain documents."""

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            return Response(
                {"detail": "Upload a PDF using the 'file' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file.name.lower().endswith(".pdf"):
            return Response(
                {"detail": "Only PDF files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
                temporary_path = Path(temporary_file.name)
                for file_chunk in uploaded_file.chunks():
                    temporary_file.write(file_chunk)

            documents = load_pdf(temporary_path)
        except Exception:
            return Response(
                {"detail": "The uploaded file could not be loaded as a PDF."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        return Response(
            {
                "filename": uploaded_file.name,
                "document_count": len(documents),
                "documents": [
                    {
                        "page_content": document.page_content,
                        "metadata": document.metadata,
                    }
                    for document in documents
                ],
            },
            status=status.HTTP_200_OK,
        )


