from pypdf import PdfReader


class PDFParser:

    def extract(self, file_path: str):
        reader = PdfReader(file_path)

        pages = []

        for index, page in enumerate(
                reader.pages,
                start=1,
        ):
            pages.append({
                "index": index,
                "text": page.extract_text() or "",
            })

        return pages