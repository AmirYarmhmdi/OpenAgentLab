import pytest

from openagentlab.skills import SkillMetadata, SkillRegistry
from openagentlab.skills.document_processing import DocumentProcessingSkill
from openagentlab.skills.registry import DuplicateSkillError


def test_skill_metadata_can_be_created() -> None:
    metadata = SkillMetadata(
        name="example",
        description="An example skill.",
        version="0.1.0",
    )

    assert metadata.name == "example"
    assert metadata.description == "An example skill."
    assert metadata.version == "0.1.0"


def test_document_processing_skill_has_metadata_and_instructions() -> None:
    skill = DocumentProcessingSkill()

    assert skill.metadata.name == "document_processing"
    assert skill.metadata.description == (
        "Deterministic processing for supported document files."
    )
    assert skill.metadata.version == "0.1.0"
    assert "deterministic processing" in skill.instructions


def test_document_processing_skill_declares_planned_capabilities() -> None:
    skill = DocumentProcessingSkill()

    assert skill.capabilities == (
        "document.read.pdf",
        "document.read.excel",
        "document.read.excel.workbook",
        "document.read.excel.sheet",
        "document.read.csv",
    )


def test_document_processing_skill_exposes_pdf_as_executable_capability() -> None:
    skill = DocumentProcessingSkill()

    assert skill.executable_capabilities == (
        "document.read.pdf",
        "document.read.excel.workbook",
        "document.read.excel.sheet",
        "document.read.csv",
    )
    assert skill.get_tool("pdf_reader") is not None


def test_document_processing_skill_keeps_high_level_excel_non_executable() -> None:
    skill = DocumentProcessingSkill()

    assert "document.read.excel" in skill.capabilities
    assert "document.read.excel.workbook" in skill.executable_capabilities
    assert "document.read.excel.sheet" in skill.executable_capabilities
    assert "document.read.csv" in skill.capabilities
    assert "document.read.excel" not in skill.executable_capabilities
    assert "document.read.csv" in skill.executable_capabilities


def test_skill_registry_registers_and_retrieves_skill() -> None:
    registry = SkillRegistry()
    skill = DocumentProcessingSkill()

    registry.register(skill)

    assert registry.get("document_processing") is skill


def test_skill_registry_rejects_duplicate_skill_names() -> None:
    registry = SkillRegistry()
    registry.register(DocumentProcessingSkill())

    with pytest.raises(DuplicateSkillError, match="document_processing"):
        registry.register(DocumentProcessingSkill())


def test_skill_registry_lists_registered_skills() -> None:
    registry = SkillRegistry()
    skill = DocumentProcessingSkill()
    registry.register(skill)

    assert registry.list_skills() == (skill,)


def test_skill_registry_finds_skills_by_declared_capability() -> None:
    registry = SkillRegistry()
    skill = DocumentProcessingSkill()
    registry.register(skill)

    assert registry.find_by_capability("document.read.pdf") == (skill,)
    assert registry.find_by_capability("document.write.pdf") == ()
