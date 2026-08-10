"""File guide.

- Use: Exports the Document Processing Skill.
- Usage: Import from openagentlab.skills.document_processing.__init__ to use the
  package API.
- Duties: Keeps package imports short and stable for other modules.
- Depends on: Project modules: openagentlab.skills.document_processing.skill.
"""

from openagentlab.skills.document_processing.skill import DocumentProcessingSkill

__all__ = ["DocumentProcessingSkill"]
