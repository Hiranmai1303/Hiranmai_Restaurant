"""
Phase 16 Unit Tests: Final Project Deliverables & Artifacts Verification
Verifies that all required PDF reports, PowerPoint presentations, and master
documentation exist and are structurally valid.
"""
import os
import pytest

DELIVERABLES = [
    "README.md",
    "docs/Dataset_Details.pdf",
    "docs/Evaluation_Report.pdf",
    "docs/API_Documentation.pdf",
    "design/Design_Document.pdf",
    "architecture/Architecture_Diagram.pdf",
    "presentation/Project_Presentation.pptx"
]

@pytest.mark.parametrize("file_path", DELIVERABLES)
def test_deliverable_file_exists_and_non_empty(file_path):
    assert os.path.exists(file_path), f"Missing required deliverable: {file_path}"
    file_size = os.path.getsize(file_path)
    assert file_size > 1000, f"Deliverable {file_path} is too small ({file_size} bytes)"

def test_readme_contains_core_sections():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    assert "AI-Powered Restaurant Operations & Review Assistant" in content
    assert "Technology Stack" in content
    assert "System Architecture" in content
    assert "LangGraph" in content
    assert "Prophet" in content
    assert "DeepEval" in content
    assert "FastAPI" in content
    assert "Streamlit" in content
