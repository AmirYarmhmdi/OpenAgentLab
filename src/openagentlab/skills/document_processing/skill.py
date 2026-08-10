from openagentlab.skills.base import BaseSkill, SkillMetadata
from openagentlab.skills.document_processing.tools.csv_reader import CSVReaderTool
from openagentlab.skills.document_processing.tools.docx_reader import DOCXReaderTool
from openagentlab.skills.document_processing.tools.excel_sheet_reader import (
    ExcelSheetReaderTool,
)
from openagentlab.skills.document_processing.tools.excel_workbook_reader import (
    ExcelWorkbookReaderTool,
)
from openagentlab.skills.document_processing.tools.json_reader import JSONReaderTool
from openagentlab.skills.document_processing.tools.pdf_reader import PDFReaderTool
from openagentlab.skills.document_processing.tools.text_reader import TextReaderTool


class DocumentProcessingSkill(BaseSkill):
    def __init__(self) -> None:
        super().__init__(
            metadata=SkillMetadata(
                name="document_processing",
                description="Deterministic processing for supported document files.",
                version="0.1.0",
            ),
            instructions=(
                "Responsible for deterministic processing of supported document "
                "and file formats. Reader tools are selected and coordinated by "
                "the orchestrator rather than parsed directly by the LLM."
            ),
            capabilities=(
                "document.read.pdf",
                "document.read.excel",
                "document.read.excel.workbook",
                "document.read.excel.sheet",
                "document.read.csv",
                "document.read.text",
                "document.read.json",
                "document.read.docx",
            ),
            tools=(
                PDFReaderTool(),
                ExcelWorkbookReaderTool(),
                ExcelSheetReaderTool(),
                CSVReaderTool(),
                TextReaderTool(),
                JSONReaderTool(),
                DOCXReaderTool(),
            ),
            dependencies=(),
        )
