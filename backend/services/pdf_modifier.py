from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


class PDFModifier:

    def modify(
            self,
            file_path: str,
            modifications: list[dict],
            output_path: str,
    ):
        reader = PdfReader(file_path)
        writer = PdfWriter()

        pages_to_remove = set()
        overlays = {}

        for modification in modifications:
            action = modification.get("action")

            if action == "remove_page":
                page = modification.get("page")

                if page:
                    pages_to_remove.add(page)

            elif action == "add_text":
                page = modification.get("page")
                text = modification.get("text", "")

                if page:
                    overlays.setdefault(
                        page,
                        [],
                    ).append(text)

        for index, page in enumerate(
                reader.pages,
                start=1,
        ):
            if index in pages_to_remove:
                continue

            if index in overlays:
                packet = BytesIO()

                overlay = canvas.Canvas(
                    packet,
                    pagesize=A4,
                )

                y_position = 750

                for text in overlays[index]:
                    overlay.drawString(
                        50,
                        y_position,
                        text,
                    )

                    y_position -= 20

                overlay.save()

                packet.seek(0)

                overlay_pdf = PdfReader(
                    packet
                )

                page.merge_page(
                    overlay_pdf.pages[0]
                )

            writer.add_page(page)

        writer.write(output_path)