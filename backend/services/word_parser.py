from docx import Document


class WordParser:

    def extract(self, file_path: str):
        document = Document(file_path)

        sections = []

        for index, paragraph in enumerate(
                document.paragraphs,
                start=1,
        ):
            text = paragraph.text.strip()

            if not text:
                continue

            sections.append({
                "index": index,
                "style": paragraph.style.name,
                "text": text,
            })

        return sections