from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from langchain_core.documents import Document


class PDFUploadViewTests(APITestCase):
	@patch("embedding.views.load_pdf")
	def test_upload_loads_pdf_and_returns_documents(self, load_pdf):
		load_pdf.return_value = [
			Document(page_content="Company policy", metadata={"page": 0}),
		]
		uploaded_file = SimpleUploadedFile(
			"policy.pdf", BytesIO(b"pdf content").read(), content_type="application/pdf"
		)

		response = self.client.post(
			"/api/documents/upload/", {"file": uploaded_file}, format="multipart"
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["document_count"], 1)
		self.assertEqual(response.data["documents"][0]["page_content"], "Company policy")
		load_pdf.assert_called_once()

	def test_upload_requires_a_file(self):
		response = self.client.post("/api/documents/upload/", {}, format="multipart")

		self.assertEqual(response.status_code, 400)
