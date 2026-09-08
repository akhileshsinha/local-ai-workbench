from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import shutil
import uuid
import json
from services.document_processor import extract_document
from services.ppt_generator import PPTGenerator
from services.excel_generator import ExcelGenerator
from services.word_generator import WordGenerator
from services.pdf_generator import PDFGenerator
from services.ppt_parser import PPTParser
from services.ppt_modifier import PPTModifier
from services.excel_parser import ExcelParser
from services.excel_modifier import ExcelModifier
from services.word_parser import WordParser
from services.word_modifier import WordModifier
from services.pdf_parser import PDFParser
from services.pdf_modifier import PDFModifier

from services.rag_service import RAGService
from fastapi.responses import FileResponse

load_dotenv()


from model_manager import ModelManager
from services.job_service import LinkedInJobService

rag_service = RAGService()
ppt_generator = PPTGenerator()
excel_generator = ExcelGenerator()
word_generator = WordGenerator()
pdf_generator = PDFGenerator()
ppt_parser = PPTParser()
ppt_modifier = PPTModifier()
excel_parser = ExcelParser()
excel_modifier = ExcelModifier()
word_parser = WordParser()
word_modifier = WordModifier()
pdf_parser = PDFParser()
pdf_modifier = PDFModifier()


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

GENERATED_DIR = Path("generated_documents")
GENERATED_DIR.mkdir(exist_ok=True)

IMAGE_DIR = Path("generated_images")
IMAGE_DIR.mkdir(exist_ok=True)

app.mount(
    "/generated-images",
    StaticFiles(directory="generated_images"),
    name="generated-images",
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_manager = ModelManager()
job_service = LinkedInJobService()

@app.post("/text-to-image")
async def text_to_image(
    prompt: str = Form(...),
):
    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    file_id = str(uuid.uuid4())

    output_path = (
        IMAGE_DIR /
        f"{file_id}.png"
    )

    model_manager.switch("flux")

    model_manager.current_model.generate(
        prompt,
        str(output_path),
    )

    return {
        "status": "generated",
        "model": "flux",
        "file_id": file_id,
        "filename": f"{file_id}.png",
        "image_url": (
            f"/generated-images/{file_id}.png"
        ),
    }

@app.get("/download-document/{file_id}")
def download_document(file_id: str):
    output_dir = Path("generated_documents")

    file_types = {
        ".pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        ".xlsx": (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        ".docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        ".pdf": "application/pdf",
    }

    for extension, media_type in file_types.items():
        file_path = output_dir / f"{file_id}{extension}"

        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                filename=file_path.name,
                media_type=media_type,
            )

    raise HTTPException(
        status_code=404,
        detail="Generated document not found.",
    )
@app.post("/upload-document")
async def upload_document(
        file: UploadFile = File(...)
):
    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "error": (
                f"Unsupported file type: {extension}. "
                "Supported: PDF, DOCX, XLSX, PPTX."
            )
        }

    document_id = str(uuid.uuid4())

    stored_filename = (
        f"{document_id}{extension}"
    )

    file_path = (
            UPLOAD_DIR /
            stored_filename
    )

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    try:
        documents = extract_document(
            str(file_path)
        )

        chunks = rag_service.chunk_documents(
            documents
        )

        rag_result = rag_service.save_document(
            document_id,
            chunks,
        )

        extracted_text = "\n\n".join(
            f"{item['source']}:\n{item['text']}"
            for item in documents
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "file_type": extension,
            "status": "processed",
            "text": extracted_text,
            "chunks": rag_result["chunk_count"],
            "embedding_dimension": (
                rag_result[
                    "embedding_dimension"
                ]
            ),
        }

    except Exception as e:
        return {
            "document_id": document_id,
            "filename": file.filename,
            "file_type": extension,
            "status": "processing_failed",
            "error": str(e),
        }

class ModifyDocumentRequest(BaseModel):
    instruction: str

@app.post("/modify-pdf")
async def modify_pdf(
        file: UploadFile = File(...),
        instruction: str = Form(...),
):
    extension = Path(
        file.filename
    ).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    input_id = str(uuid.uuid4())

    input_path = (
            UPLOAD_DIR /
            f"{input_id}.pdf"
    )

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    document_data = pdf_parser.extract(
        str(input_path)
    )

    model_manager.switch("qwen")

    prompt = f"""
You are modifying an existing PDF document.

Existing PDF:

{json.dumps(
        document_data,
        indent=2,
        ensure_ascii=False,
    )}

User modification request:

{instruction}

Return ONLY valid JSON.

Format:

{{
    "modifications": [
        {{
            "action": "add_text",
            "page": 1,
            "text": "Additional text"
        }}
    ]
}}

Supported actions:

1. add_text

{{
    "action": "add_text",
    "page": 1,
    "text": "Text to add"
}}

2. remove_page

{{
    "action": "remove_page",
    "page": 3
}}

Only return the modifications required.
Do not return explanations.
"""

    response = model_manager.generate(
        prompt
    )

    try:
        modification_data = json.loads(
            response
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid PDF modification JSON.",
        )

    output_id = str(uuid.uuid4())

    output_path = (
            GENERATED_DIR /
            f"{output_id}.pdf"
    )

    pdf_modifier.modify(
        file_path=str(input_path),
        modifications=modification_data[
            "modifications"
        ],
        output_path=str(output_path),
    )

    return {
        "status": "modified",
        "file_id": output_id,
        "filename": f"modified_{file.filename}",
        "download_url": (
            f"/download-document/{output_id}"
        ),
    }

@app.post("/modify-word")
async def modify_word(
        file: UploadFile = File(...),
        instruction: str = Form(...),
):
    extension = Path(
        file.filename
    ).suffix.lower()

    if extension != ".docx":
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files are supported.",
        )

    input_id = str(uuid.uuid4())

    input_path = (
            UPLOAD_DIR /
            f"{input_id}.docx"
    )

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    document_data = word_parser.extract(
        str(input_path)
    )

    model_manager.switch("qwen")

    prompt = f"""
You are modifying an existing Word document.

Existing document:

{json.dumps(
        document_data,
        indent=2,
        ensure_ascii=False,
    )}

User modification request:

{instruction}

Return ONLY valid JSON.

Format:

{{
    "modifications": [
        {{
            "action": "replace_text",
            "old_text": "Old text",
            "new_text": "New text"
        }}
    ]
}}

Supported actions:

1. replace_text

{{
    "action": "replace_text",
    "old_text": "Old text",
    "new_text": "New text"
}}

2. update_paragraph

{{
    "action": "update_paragraph",
    "paragraph_index": 3,
    "text": "Updated paragraph"
}}

3. add_paragraph

{{
    "action": "add_paragraph",
    "text": "New paragraph"
}}

4. remove_paragraph

{{
    "action": "remove_paragraph",
    "paragraph_index": 4
}}

5. add_heading

{{
    "action": "add_heading",
    "text": "New Section",
    "level": 1
}}

Only return the modifications required.
Do not return explanations.
"""

    response = model_manager.generate(
        prompt
    )

    try:
        modification_data = json.loads(
            response
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid modification JSON.",
        )

    output_id = str(uuid.uuid4())

    output_path = (
            GENERATED_DIR /
            f"{output_id}.docx"
    )

    word_modifier.modify(
        file_path=str(input_path),
        modifications=modification_data[
            "modifications"
        ],
        output_path=str(output_path),
    )

    return {
        "status": "modified",
        "file_id": output_id,
        "filename": f"modified_{file.filename}",
        "download_url": (
            f"/download-document/{output_id}"
        ),
    }

@app.post("/modify-excel")
async def modify_excel(
        file: UploadFile = File(...),
        instruction: str = Form(...),
):
    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in [".xlsx", ".xlsm"]:
        raise HTTPException(
            status_code=400,
            detail="Only Excel files are supported.",
        )

    input_id = str(uuid.uuid4())

    input_path = (
            UPLOAD_DIR /
            f"{input_id}{extension}"
    )

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    workbook_data = excel_parser.extract(
        str(input_path)
    )

    model_manager.switch("qwen")

    prompt = f"""
You are modifying an existing Excel workbook.

Existing workbook:

{json.dumps(workbook_data, indent=2, default=str)}

User modification request:

{instruction}

Return ONLY valid JSON.

Format:

{{
    "modifications": [
        {{
            "action": "update_cell",
            "sheet": "Employees",
            "cell": "B2",
            "value": "Bangalore"
        }}
    ]
}}

Supported actions:

1. update_cell

{{
    "action": "update_cell",
    "sheet": "Sheet1",
    "cell": "A1",
    "value": "New value"
}}

2. replace_text

{{
    "action": "replace_text",
    "sheet": "Sheet1",
    "old_text": "Hyderabad",
    "new_text": "Bangalore"
}}

3. add_column

{{
    "action": "add_column",
    "sheet": "Sheet1",
    "column_index": 5,
    "header": "Status",
    "values": ["Active", "Inactive"]
}}

4. remove_column

{{
    "action": "remove_column",
    "sheet": "Sheet1",
    "column_index": 5
}}

5. add_row

{{
    "action": "add_row",
    "sheet": "Sheet1",
    "values": ["John", "Hyderabad", "Male"]
}}

6. remove_row

{{
    "action": "remove_row",
    "sheet": "Sheet1",
    "row_index": 4
}}

7. create_sheet

{{
    "action": "create_sheet",
    "name": "Summary",
    "headers": ["Department", "Count"],
    "rows": [
        ["Engineering", 10],
        ["Product", 5]
    ]
}}

Only return modifications required by the user's request.
"""

    response = model_manager.generate(
        prompt
    )

    try:
        modification_data = json.loads(
            response
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid modification JSON.",
        )

    output_id = str(uuid.uuid4())

    output_path = (
            GENERATED_DIR /
            f"{output_id}{extension}"
    )

    excel_modifier.modify(
        file_path=str(input_path),
        modifications=modification_data[
            "modifications"
        ],
        output_path=str(output_path),
    )

    return {
        "status": "modified",
        "file_id": output_id,
        "filename": f"modified_{file.filename}",
        "download_url": (
            f"/download-document/{output_id}"
        ),
    }

@app.post("/modify-ppt")
async def modify_ppt(
        file: UploadFile = File(...),
        instruction: str = Form(...),
):
    extension = Path(
        file.filename
    ).suffix.lower()

    if extension != ".pptx":
        raise HTTPException(
            status_code=400,
            detail="Only PPTX files are supported currently.",
        )

    input_id = str(uuid.uuid4())

    input_path = (
            UPLOAD_DIR /
            f"{input_id}.pptx"
    )

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    slides = ppt_parser.extract(
        str(input_path)
    )

    model_manager.switch("qwen")

    prompt = f"""
You are modifying an existing PowerPoint presentation.

Existing presentation:

{json.dumps(slides, indent=2)}

User modification request:

{instruction}

Return ONLY valid JSON.

Format:

{{
    "modifications": [
        {{
            "action": "change_title",
            "slide": 1,
            "value": "New title"
        }},
        {{
            "action": "replace_text",
            "old_text": "Old text",
            "new_text": "New text"
        }}
    ]
}}

Supported actions:
- change_title
- replace_text

Only return modifications required by the user's request.
"""

    response = model_manager.generate(
        prompt
    )

    try:
        modification_data = json.loads(
            response
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid modification JSON.",
        )

    output_id = str(uuid.uuid4())

    output_path = (
            GENERATED_DIR /
            f"{output_id}.pptx"
    )

    ppt_modifier.modify(
        file_path=str(input_path),
        modifications=modification_data[
            "modifications"
        ],
        output_path=str(output_path),
    )

    return {
        "status": "modified",
        "file_id": output_id,
        "filename": f"modified_{file.filename}",
        "download_url": (
            f"/download-document/{output_id}"
        ),
    }

class GeneratePDFRequest(BaseModel):
    prompt: str

@app.post("/generate-pdf")
def generate_pdf(
        request: GeneratePDFRequest
):
    model_manager.switch("qwen")

    prompt = f"""
Create a professional PDF document based on the user's request.

Return ONLY valid JSON.

Format:
{{
    "title": "Document title",
    "sections": [
        {{
            "heading": "Section heading",
            "content": "Section content",
            "bullets": [
                "Bullet 1",
                "Bullet 2",
                "Bullet 3"
            ]
        }}
    ]
}}

Requirements:
- Create logical sections.
- Use professional business language.
- Keep the content concise and well structured.
- Use bullets where appropriate.
- Do not use Markdown.
- Return ONLY valid JSON.

User request:
{request.prompt}
"""

    response = model_manager.generate(prompt)

    try:
        document_data = json.loads(response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid PDF JSON."
        )

    output_dir = Path("generated_documents")
    output_dir.mkdir(exist_ok=True)

    file_id = str(uuid.uuid4())

    output_path = (
            output_dir /
            f"{file_id}.pdf"
    )

    pdf_generator.generate(
        title=document_data["title"],
        sections=document_data["sections"],
        output_path=str(output_path),
    )

    return {
        "status": "generated",
        "file_id": file_id,
        "filename": f"{document_data['title']}.pdf",
        "download_url": (
            f"/download-document/{file_id}"
        ),
    }

class GenerateWordRequest(BaseModel):
    prompt: str
@app.post("/generate-word")
def generate_word(
        request: GenerateWordRequest
):
    model_manager.switch("qwen")

    prompt = f"""
Create a professional Word document based on the user's request.

Return ONLY valid JSON.

Format:
{{
    "title": "Document title",
    "sections": [
        {{
            "heading": "Section heading",
            "content": "Section content",
            "bullets": [
                "Bullet 1",
                "Bullet 2",
                "Bullet 3"
            ]
        }}
    ]
}}

Requirements:
- Create logical sections.
- Use professional language.
- Keep the content well structured.
- Use bullets where appropriate.
- Do not use Markdown.
- Return ONLY valid JSON.

User request:
{request.prompt}
"""

    response = model_manager.generate(prompt)

    try:
        document_data = json.loads(response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid Word document JSON."
        )

    output_dir = Path("generated_documents")
    output_dir.mkdir(exist_ok=True)

    file_id = str(uuid.uuid4())

    output_path = (
            output_dir /
            f"{file_id}.docx"
    )

    word_generator.generate(
        title=document_data["title"],
        sections=document_data["sections"],
        output_path=str(output_path),
    )

    return {
        "status": "generated",
        "file_id": file_id,
        "filename": f"{document_data['title']}.docx",
        "download_url": (
            f"/download-document/{file_id}"
        ),
    }


class GenerateExcelRequest(BaseModel):
    prompt: str

@app.post("/generate-excel")
def generate_excel(
        request: GenerateExcelRequest
):
    model_manager.switch("qwen")

    prompt = f"""
Create an Excel workbook based on the user's request.

Return ONLY valid JSON.

Format:
{{
    "sheets": [
        {{
            "name": "Sheet name",
            "headers": [
                "Column 1",
                "Column 2"
            ],
            "rows": [
                ["Value 1", "Value 2"],
                ["Value 3", "Value 4"]
            ]
        }}
    ]
}}

Requirements:
- Create only the sheets required by the request.
- Use meaningful sheet names.
- Include appropriate column headers.
- Generate realistic and useful data.
- Do not use Markdown.
- Return ONLY JSON.

User request:
{request.prompt}
"""

    response = model_manager.generate(prompt)

    try:
        workbook_data = json.loads(response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid Excel JSON."
        )

    output_dir = Path("generated_documents")
    output_dir.mkdir(exist_ok=True)

    file_id = str(uuid.uuid4())

    output_path = (
            output_dir /
            f"{file_id}.xlsx"
    )

    excel_generator.generate(
        sheets=workbook_data["sheets"],
        output_path=str(output_path),
    )

    return {
        "status": "generated",
        "file_id": file_id,
        "filename": "generated.xlsx",
        "download_url": (
            f"/download-document/{file_id}"
        ),
    }

class GeneratePPTRequest(BaseModel):
    prompt: str

@app.post("/generate-ppt")
def generate_ppt(request: GeneratePPTRequest):
    model_manager.switch("qwen")

    prompt = f"""
Create a professional PowerPoint presentation based on the
following user request.

Return ONLY valid JSON.

JSON format:
{{
    "title": "Presentation title",
    "slides": [
        {{
            "title": "Slide title",
            "bullets": [
                "Bullet 1",
                "Bullet 2",
                "Bullet 3"
            ]
        }}
    ]
}}

Requirements:
- Create 5 to 8 slides.
- Keep each slide concise.
- Use professional business language.
- Do not use Markdown.
- Do not add explanations outside the JSON.

User request:
{request.prompt}
"""

    response = model_manager.generate(prompt)

    try:
        presentation_data = json.loads(response)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Qwen returned invalid presentation JSON."
        )

    output_dir = Path("generated_documents")
    output_dir.mkdir(exist_ok=True)

    file_id = str(uuid.uuid4())

    output_path = (
            output_dir /
            f"{file_id}.pptx"
    )

    ppt_generator.generate(
        title=presentation_data["title"],
        slides=presentation_data["slides"],
        output_path=str(output_path),
    )

    return {
        "status": "generated",
        "file_id": file_id,
        "filename": f"{presentation_data['title']}.pptx",
        "download_url": f"/download-document/{file_id}",
    }


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "qwen"

@app.post("/generate")
def generate(request: GenerateRequest):

    model_manager.switch("qwen")
    response = model_manager.generate(
        request.prompt
    )

    return {
        "model": "qwen",
        "response": response,
    }


@app.get("/models")
def get_models():

    return model_manager.get_status()

class SwitchModelRequest(BaseModel):
    model: str


@app.post("/models/switch")
def switch_model(request: SwitchModelRequest):

    model_manager.switch(request.model)

    return {
        "model": request.model,
        "status": "loaded",
    }

@app.post("/models/unload")
def unload_model():

    model_manager.unload()

    return {
        "status": "Model unloaded"
    }

@app.post("/analyze-image")
async def analyze_image(
        prompt: str = Form(...),
        image: UploadFile = File(...),
):

    model_manager.switch("qwen-vision")

    model = model_manager.models["qwen-vision"]

    image_bytes = await image.read()

    import tempfile

    with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=True
    ) as temp:

        temp.write(image_bytes)
        temp.flush()

        response = model.generate(
            temp.name,
            prompt
        )

    return {
        "model": "Qwen3-VL-2B-Instruct",
        "response": response,
    }


class GenerateCodeRequest(BaseModel):
    prompt: str


@app.post("/generate-code")
def generate_code(request: GenerateCodeRequest):

    model_manager.switch("qwen-coder")

    result = model_manager.generate(
        request.prompt
    )

    return {
        "model": "qwen-coder",
        "response": result["explanation"],
        "code": result["code"],
    }

class GenerateProjectRequest(BaseModel):
    prompt: str
    workspace: Optional[dict] = None


class WorkspaceFile(BaseModel):
    path: str
    content: str

class Workspace(BaseModel):
    files: list[WorkspaceFile] = []


@app.post("/generate-project")
def generate_project(request: GenerateProjectRequest):

    model_manager.switch("qwen-coder")

    workspace_files = (
        request.workspace.get("files", [])
        if request.workspace
        else []
    )

    response = model_manager.generate_project(
        request.prompt,
        workspace_files,
    )

    return response


class AskDocumentRequest(BaseModel):
    document_id: str
    question: str

@app.post("/ask-document")
def ask_document(
        request: AskDocumentRequest
):
    model_manager.switch("qwen")

    results = rag_service.search(
        request.document_id,
        request.question,
        top_k=5,
    )

    if not results:
        return {
            "document_id": request.document_id,
            "question": request.question,
            "answer": (
                "I could not find the answer "
                "in the document."
            ),
            "sources": [],
        }

    context_parts = []

    for index, result in enumerate(
            results,
            start=1,
    ):
        context_parts.append(
            f"""
Source {index} ({result['source']}):
{result['text']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
Answer the user's question using only the
provided document context.

Rules:
- Do not use outside knowledge.
- If the answer is not available in the context,
  say exactly:
  "I could not find the answer in the document."
- Give a concise and accurate answer.
- When useful, mention the source such as
  Page 3, Slide 5, or a sheet name.
- Do not invent information.

Document context:
{context}

User question:
{request.question}
"""

    response = model_manager.generate(
        prompt
    )

    return {
        "document_id": request.document_id,
        "question": request.question,
        "answer": response,
        "sources": results,
    }