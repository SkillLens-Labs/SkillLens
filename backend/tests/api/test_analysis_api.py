from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["app"] == "SkillLens"
    assert data["version"] == "0.1.0"


def test_resume_analysis_endpoint_contract() -> None:
    response = client.post(
        "/api/v1/analyses/resume",
        files={
            "resume": (
                "resume.pdf",
                b"placeholder resume content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 501

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_IMPLEMENTED"
    assert "message" in data
    assert "request_id" in data


def test_resume_jd_analysis_endpoint_contract() -> None:
    response = client.post(
        "/api/v1/analyses/resume-jd",
        files={
            "resume": (
                "resume.pdf",
                b"placeholder resume content",
                "application/pdf",
            ),
            "job_description": (
                "job.txt",
                b"placeholder job description",
                "text/plain",
            ),
        },
    )

    assert response.status_code == 501

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_IMPLEMENTED"
    assert "message" in data
    assert "request_id" in data


def test_get_analysis_endpoint_contract() -> None:
    response = client.get("/api/v1/analyses/test-analysis-id")

    assert response.status_code == 501

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_IMPLEMENTED"
    assert "message" in data
    assert "request_id" in data


def test_delete_analysis_endpoint_contract() -> None:
    response = client.delete("/api/v1/analyses/test-analysis-id")

    assert response.status_code == 501

    data = response.json()

    assert data["code"] == "ANALYSIS_NOT_IMPLEMENTED"
    assert "message" in data
    assert "request_id" in data
