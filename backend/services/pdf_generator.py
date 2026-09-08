from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
)


class PDFGenerator:

    def generate(
            self,
            title: str,
            sections: list[dict],
            output_path: str,
    ):
        document = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=0.7 * inch,
            leftMargin=0.7 * inch,
            topMargin=0.7 * inch,
            bottomMargin=0.7 * inch,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocumentTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=22,
            spaceAfter=24,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=15,
            spaceBefore=14,
            spaceAfter=8,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=15,
            spaceAfter=8,
        )

        story = []

        # Title
        story.append(
            Paragraph(
                title,
                title_style,
            )
        )

        for section in sections:
            heading = section.get(
                "heading",
                "",
            )

            content = section.get(
                "content",
                "",
            )

            bullets = section.get(
                "bullets",
                [],
            )

            if heading:
                story.append(
                    Paragraph(
                        heading,
                        heading_style,
                    )
                )

            if content:
                story.append(
                    Paragraph(
                        content,
                        body_style,
                    )
                )

            if bullets:
                bullet_items = []

                for bullet in bullets:
                    bullet_items.append(
                        ListItem(
                            Paragraph(
                                str(bullet),
                                body_style,
                            )
                        )
                    )

                story.append(
                    ListFlowable(
                        bullet_items,
                        bulletType="bullet",
                        leftIndent=20,
                    )
                )

                story.append(
                    Spacer(1, 8)
                )

        document.build(story)