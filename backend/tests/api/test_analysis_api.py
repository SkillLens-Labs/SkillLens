import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.analysis.resume_language_quality import ResumeLanguageQualityAnalyzer
from backend.app.main import app


client = TestClient(app)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
PDF_FIXTURE = FIXTURES_DIR / "phase3_sample_resume.pdf"
DOCX_FIXTURE = FIXTURES_DIR / "phase3_sample_resume.docx"
JD_FIXTURE = FIXTURES_DIR / "phase5_sample_job_description.docx"


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "SkillLens"
    assert data["version"] == "0.1.0"


def test_resume_analysis_endpoint_returns_canonical_result() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert "data" in body

    data = body["data"]

    assert data["analysis_id"]
    assert data["schema_version"] == "1.0.0"
    assert data["analysis_mode"] == "resume_only"
    assert data["status"] == "completed"
    assert data["input"]["resume_document_id"]
    assert data["resume_profile"] is not None
    assert data["resume_quality"] is not None
    assert data["ats_intelligence"] is not None
    assert data["job_profile"] is None
    assert data["skill_analysis"] is not None
    assert data["skill_analysis"]["extracted_skills"] == []
    assert data["skill_analysis"]["matched_skills"] == []
    assert isinstance(data["skill_analysis"]["gaps"], list)

    assert data["scoring"] is None
    assert data["xai"] is None
    assert data["career_intelligence"] is not None
    assert data["career_intelligence"]["taxonomy_version"] == "career-taxonomy-v1"
    assert data["career_intelligence"]["engine_version"] == "phase7-career-intelligence-v1"
    assert data["recommendations"] == []

    assert data["language_quality"] is not None
    assert 0.0 <= data["language_quality"]["overall_score"] <= 100.0
    assert data["language_quality"]["authorship_heuristic"] is not None
    assert data["language_quality"]["authorship_heuristic"]["disclaimer"] == (
        "This is a heuristic writing-style estimate, not proof of AI authorship."
    )
    assert (
        data["metadata"]["engine_versions"]["language_quality"]
        == ResumeLanguageQualityAnalyzer.ENGINE_VERSION
    )


def test_resume_analysis_endpoint_supports_docx() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["analysis_mode"] == "resume_only"
    assert data["status"] == "completed"
    assert data["resume_profile"] is not None
    assert data["resume_quality"] is not None
    assert data["ats_intelligence"] is not None


def test_resume_analysis_accepts_options_and_client_metadata() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "options": (
                    '{"include_career_intelligence": true,'
                    '"include_recommendations": true,'
                    '"include_xai": true}'
                ),
                "client_metadata": (
                    '{"source": "api-test",'
                    '"session_id": "test-session",'
                    '"extra": {"test": true}}'
                ),
            },
        )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["metadata"]["extra"]["source"] == "api-test"
    assert data["metadata"]["extra"]["session_id"] == "test-session"


def test_resume_analysis_rejects_invalid_options_json() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "options": "{invalid-json",
            },
        )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == "INVALID_ANALYSIS_OPTIONS"
    assert data["field"] == "options"
    assert data["request_id"]


def test_resume_analysis_rejects_invalid_client_metadata_json() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "client_metadata": "{invalid-json",
            },
        )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == "INVALID_CLIENT_METADATA"
    assert data["field"] == "client_metadata"
    assert data["request_id"]


def test_resume_analysis_rejects_unsupported_document_type() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        files={
            "resume": (
                "resume.txt",
                b"plain text resume",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == "UNSUPPORTED_DOCUMENT_TYPE"
    assert data["request_id"]


def test_resume_analysis_rejects_empty_document() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        files={
            "resume": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == "EMPTY_DOCUMENT"
    assert data["request_id"]


def test_resume_analysis_rejects_content_mismatch() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        files={
            "resume": (
                "resume.pdf",
                b"not a pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["code"] == "DOCUMENT_CONTENT_MISMATCH"
    assert data["request_id"]


def test_get_analysis_endpoint_returns_existing_analysis() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        create_response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert create_response.status_code == 200

    analysis_id = create_response.json()["data"]["analysis_id"]

    response = client.get(
        f"/api/v1/analyses/{analysis_id}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["data"]["analysis_id"] == analysis_id
    assert body["data"]["analysis_mode"] == "resume_only"
    assert body["data"]["status"] == "completed"


def test_get_analysis_endpoint_returns_not_found() -> None:
    response = client.get(
        "/api/v1/analyses/nonexistent-analysis-id",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_FOUND"
    assert data["field"] == "analysis_id"
    assert data["request_id"]


def test_delete_analysis_endpoint_deletes_existing_analysis() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        create_response = client.post(
            "/api/v1/analyses/resume",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert create_response.status_code == 200

    analysis_id = create_response.json()["data"]["analysis_id"]

    response = client.delete(
        f"/api/v1/analyses/{analysis_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["analysis_id"] == analysis_id
    assert data["deleted"] is True
    assert data["message"]


def test_delete_analysis_endpoint_returns_not_found() -> None:
    response = client.delete(
        "/api/v1/analyses/nonexistent-analysis-id",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_FOUND"
    assert data["field"] == "analysis_id"
    assert data["request_id"]


def test_resume_jd_analysis_endpoint_returns_matching_result() -> None:
    with DOCX_FIXTURE.open("rb") as resume, JD_FIXTURE.open("rb") as job_description:
        response = client.post(
            "/api/v1/analyses/resume-jd",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
                "job_description": (
                    "phase5_sample_job_description.docx",
                    job_description,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            },
        )

    assert response.status_code == 200

    body = response.json()
    assert "data" in body

    data = body["data"]
    assert data["analysis_id"]
    assert data["schema_version"] == "1.0.0"
    assert data["analysis_mode"] == "resume_jd"
    assert data["status"] == "completed"

    assert data["input"]["resume_document_id"]
    assert data["input"]["job_description_document_id"]

    assert data["resume_profile"] is not None
    assert data["job_profile"] is not None

    assert data["language_quality"] is not None
    assert 0.0 <= data["language_quality"]["overall_score"] <= 100.0
    assert data["language_quality"]["confidence"] is not None
    assert data["language_quality"]["authorship_heuristic"] is not None
    assert (
        data["language_quality"]["authorship_heuristic"]["disclaimer"]
        == "This is a heuristic writing-style estimate, not proof of AI authorship."
    )
    assert (
        data["metadata"]["engine_versions"]["language_quality"]
        == ResumeLanguageQualityAnalyzer.ENGINE_VERSION
    )

    assert data["matching"] is not None
    assert data["matching"]["skill_matches"]
    assert data["matching"]["requirement_alignments"]

    assert data["skill_analysis"] is not None
    assert data["skill_analysis"]["extracted_skills"]

    print("\nSKILL MATCHES:")
    print(json.dumps(data["matching"]["skill_matches"], indent=2, default=str))

    print("\nREQUIREMENT ALIGNMENTS:")
    print(json.dumps(data["matching"]["requirement_alignments"], indent=2, default=str))

    print("\nSKILL ANALYSIS:")
    print(json.dumps(data["skill_analysis"], indent=2, default=str))

    assert data["skill_analysis"]["partial_matches"]
    assert "Strong Python and SQL skills." in data["skill_analysis"]["partial_matches"]
    assert isinstance(data["skill_analysis"]["gaps"], list)

    assert data["scoring"] is not None
    assert 0.0 <= data["scoring"]["overall_score"] <= 100.0
    assert data["scoring"]["dimension_scores"]
    assert data["scoring"]["contributions"]

    assert data["xai"] is not None
    assert data["xai"]["overall_explanation"]
    assert data["xai"]["score_explanation"]

def test_resume_analysis_accepts_resume_text() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        data={
            "resume_text": (
                "John Doe\n"
                "Python developer with FastAPI, SQL, Docker, and AWS experience."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["analysis_mode"] == "resume_only"
    assert data["status"] == "completed"


def test_resume_jd_accepts_resume_file_and_jd_text() -> None:
    with DOCX_FIXTURE.open("rb") as resume:
        response = client.post(
            "/api/v1/analyses/resume-jd",
            files={
                "resume": (
                    "phase3_sample_resume.docx",
                    resume,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "job_description_text": (
                    "We are looking for a Python developer with FastAPI, "
                    "SQL, Docker, and AWS experience."
                )
            },
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["analysis_mode"] == "resume_jd"
    assert data["status"] == "completed"


def test_resume_jd_accepts_resume_text_and_jd_file() -> None:
    with JD_FIXTURE.open("rb") as job_description:
        response = client.post(
            "/api/v1/analyses/resume-jd",
            files={
                "job_description": (
                    "phase5_sample_job_description.docx",
                    job_description,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={
                "resume_text": (
                    "John Doe\n"
                    "Python developer with FastAPI, SQL, Docker, and AWS experience."
                )
            },
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["analysis_mode"] == "resume_jd"
    assert data["status"] == "completed"


def test_resume_jd_accepts_resume_text_and_jd_text() -> None:
    response = client.post(
        "/api/v1/analyses/resume-jd",
        data={
            "resume_text": (
                "John Doe\n"
                "Python developer with FastAPI, SQL, Docker, and AWS experience."
            ),
            "job_description_text": (
                "We are looking for a Python developer with FastAPI, "
                "SQL, Docker, and AWS experience."
            ),
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["analysis_mode"] == "resume_jd"
    assert data["status"] == "completed"


def test_resume_jd_text_extracts_skills_and_matches_resume() -> None:
    response = client.post(
        "/api/v1/analyses/resume-jd",
        data={
            "resume_text": (
                "John Doe\n"
                "Python developer with FastAPI, SQL, Docker, and AWS experience."
            ),
            "job_description_text": (
                "We are looking for a Python developer with FastAPI, "
                "SQL, Docker, and AWS experience."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["status"] == "completed"
    assert data["matching"]["metadata"]["job_skill_count"] == 5


def test_resume_analysis_rejects_missing_resume_input() -> None:
    response = client.post("/api/v1/analyses/resume")

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_DOCUMENT_INPUT"


def test_resume_analysis_rejects_file_and_text_together() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        files={
            "resume": (
                "resume.txt",
                b"resume content",
                "text/plain",
            )
        },
        data={"resume_text": "duplicate resume content"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_DOCUMENT_INPUT"


def test_resume_jd_rejects_missing_job_description_input() -> None:
    response = client.post(
        "/api/v1/analyses/resume-jd",
        data={"resume_text": "Python developer with FastAPI experience."},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "INVALID_DOCUMENT_INPUT"

def test_job_description_text_preserves_header_metadata() -> None:
    from backend.app.api.routes.analyses import _job_description_text_as_docx
    from backend.app.analysis.jd_structure import JDSectionType, JDStructureInterpreter
    from backend.app.infrastructure.parsers.document_processor import DocumentProcessor

    jd_text = (
        "Data Engineer\n"
        "Company: NovaTech Solutions\n"
        "Location: Remote — India\n"
        "Employment Type: Full-time\n"
        "Experience: 0–2 years\n"
        "\n"
        "Required Qualifications\n"
        "Strong Python programming skills.\n"
    )

    filename, content, content_type = _job_description_text_as_docx(
        jd_text,
        "test_jd",
    )

    document = DocumentProcessor().process(
        filename=filename,
        content=content,
        content_type=content_type,
        document_id="test-jd-header",
    )

    structured = JDStructureInterpreter().interpret(document)

    header = structured.sections_of(JDSectionType.HEADER)[0]

    assert [block.text for block in header.blocks] == [
        "Company: NovaTech Solutions",
        "Location: Remote — India",
        "Employment Type: Full-time",
        "Experience: 0–2 years",
    ]