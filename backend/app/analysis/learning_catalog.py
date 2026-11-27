"""SkillLens V2 learning catalog.

Deterministic, curated mapping from canonical skills (see
skill_taxonomy.py) to recognized certifications and courses. This is the
data source for certification/course recommendations in both JD-compare
and resume-only modes.

The catalog is static and versioned: recommendations cite
LEARNING_CATALOG_VERSION so results are reproducible and auditable.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.analysis.skill_taxonomy import Taxonomy
from backend.app.domain.recommendations import LearningResourceRef


LEARNING_CATALOG_VERSION = "learning-catalog-v1"


@dataclass(frozen=True)
class LearningResource:
    """One curated certification or course entry."""

    kind: str  # "certification" or "course"
    title: str
    provider: str
    level: str  # "entry", "intermediate", or "advanced"
    url: str
    skills: tuple[str, ...] = ()

    def to_ref(self, related_skill: str) -> LearningResourceRef:
        return LearningResourceRef(
            kind=self.kind,
            title=self.title,
            provider=self.provider,
            level=self.level,
            url=self.url,
            related_skill=related_skill,
        )


_CATALOG: tuple[LearningResource, ...] = (
    # Cloud
    LearningResource("certification", "AWS Certified Cloud Practitioner", "Amazon Web Services", "entry", "https://aws.amazon.com/certification/certified-cloud-practitioner/", ("aws",)),
    LearningResource("certification", "AWS Certified Solutions Architect - Associate", "Amazon Web Services", "intermediate", "https://aws.amazon.com/certification/certified-solutions-architect-associate/", ("aws",)),
    LearningResource("certification", "Microsoft Certified: Azure Fundamentals (AZ-900)", "Microsoft", "entry", "https://learn.microsoft.com/credentials/certifications/azure-fundamentals/", ("azure",)),
    LearningResource("certification", "Microsoft Certified: Azure Administrator Associate (AZ-104)", "Microsoft", "intermediate", "https://learn.microsoft.com/credentials/certifications/azure-administrator/", ("azure",)),
    LearningResource("certification", "Google Cloud Digital Leader", "Google Cloud", "entry", "https://cloud.google.com/learn/certification/cloud-digital-leader", ("gcp",)),
    LearningResource("certification", "Google Cloud Associate Cloud Engineer", "Google Cloud", "intermediate", "https://cloud.google.com/learn/certification/cloud-engineer", ("gcp",)),
    # DevOps
    LearningResource("certification", "Docker Certified Associate", "Docker", "intermediate", "https://training.mirantis.com/dca-certification/", ("docker",)),
    LearningResource("course", "Docker Fundamentals", "Docker", "entry", "https://www.docker.com/courses/", ("docker",)),
    LearningResource("certification", "Certified Kubernetes Administrator (CKA)", "CNCF", "advanced", "https://www.cncf.io/training/certification/cka/", ("kubernetes",)),
    LearningResource("certification", "HashiCorp Certified: Terraform Associate", "HashiCorp", "intermediate", "https://developer.hashicorp.com/certifications/infrastructure-automation", ("terraform",)),
    LearningResource("certification", "CompTIA Linux+", "CompTIA", "entry", "https://www.comptia.org/certifications/linux", ("linux",)),
    # Programming
    LearningResource("certification", "PCEP - Certified Entry-Level Python Programmer", "Python Institute", "entry", "https://pythoninstitute.org/pcep", ("python",)),
    LearningResource("certification", "PCAP - Certified Associate Python Programmer", "Python Institute", "intermediate", "https://pythoninstitute.org/pcap", ("python",)),
    LearningResource("certification", "Oracle Certified Professional: Java SE 17 Developer", "Oracle", "intermediate", "https://education.oracle.com/java-se-17-developer/pexam_1z0-829", ("java",)),
    LearningResource("certification", "Microsoft Certified: Power BI Data Analyst Associate (PL-300)", "Microsoft", "intermediate", "https://learn.microsoft.com/credentials/certifications/data-analyst-associate/", ("power bi",)),
    LearningResource("certification", "Tableau Desktop Specialist", "Tableau", "entry", "https://www.tableau.com/learn/certification/desktop-specialist", ("tableau",)),
    LearningResource("certification", "Microsoft Office Specialist: Excel Associate", "Microsoft", "entry", "https://learn.microsoft.com/office-certifications/", ("excel",)),
    # Data & ML
    LearningResource("certification", "Google Data Analytics Professional Certificate", "Google (Coursera)", "entry", "https://www.coursera.org/professional-certificates/google-data-analytics", ("data analysis",)),
    LearningResource("certification", "IBM Data Science Professional Certificate", "IBM (Coursera)", "entry", "https://www.coursera.org/professional-certificates/ibm-data-science", ("data science",)),
    LearningResource("certification", "Machine Learning Specialization", "DeepLearning.AI (Coursera)", "intermediate", "https://www.coursera.org/specializations/machine-learning-introduction", ("machine learning",)),
    LearningResource("certification", "Deep Learning Specialization", "DeepLearning.AI (Coursera)", "intermediate", "https://www.coursera.org/specializations/deep-learning", ("deep learning",)),
    LearningResource("certification", "TensorFlow Developer Certificate", "Google", "advanced", "https://www.tensorflow.org/certificate", ("tensorflow",)),
    LearningResource("course", "Generative AI with Large Language Models", "DeepLearning.AI (Coursera)", "intermediate", "https://www.coursera.org/learn/generative-ai-with-llms", ("llm",)),
    LearningResource("course", "Prompt Engineering for ChatGPT", "Vanderbilt (Coursera)", "entry", "https://www.coursera.org/learn/prompt-engineering", ("prompt engineering",)),
    LearningResource("certification", "Databricks Certified Data Engineer Associate", "Databricks", "intermediate", "https://www.databricks.com/learn/certification/data-engineer-associate", ("spark", "databricks")),
    LearningResource("certification", "Confluent Certified Developer for Apache Kafka", "Confluent", "intermediate", "https://www.confluent.io/certification/", ("kafka",)),
    LearningResource("certification", "SnowPro Core Certification", "Snowflake", "intermediate", "https://learn.snowflake.com/", ("snowflake",)),
    LearningResource("course", "SQL for Data Science", "UC Davis (Coursera)", "entry", "https://www.coursera.org/learn/sql-for-data-science", ("sql",)),
    # Business
    LearningResource("certification", "Professional Scrum Master I (PSM I)", "Scrum.org", "entry", "https://www.scrum.org/professional-scrum-certifications", ("agile",)),
    LearningResource("certification", "Project Management Professional (PMP)", "PMI", "advanced", "https://www.pmi.org/certifications/project-management-pmp", ("project management",)),
    LearningResource("certification", "Google Project Management Professional Certificate", "Google (Coursera)", "entry", "https://www.coursera.org/professional-certificates/google-project-management", ("project management",)),
    LearningResource("certification", "Salesforce Certified Administrator", "Salesforce", "entry", "https://trailhead.salesforce.com/credentials/administratoroverview", ("salesforce",)),
    LearningResource("certification", "Financial Modeling & Valuation Analyst (FMVA)", "Corporate Finance Institute", "intermediate", "https://corporatefinanceinstitute.com/certifications/", ("financial analysis",)),
    # Security
    LearningResource("certification", "CompTIA Security+", "CompTIA", "entry", "https://www.comptia.org/certifications/security", ("cybersecurity",)),
)


class LearningCatalog:
    """Deterministic lookup from skills to curated learning resources."""

    VERSION = LEARNING_CATALOG_VERSION

    def __init__(self) -> None:
        self._by_skill: dict[str, tuple[LearningResource, ...]] = {}
        for resource in _CATALOG:
            for skill in resource.skills:
                self._by_skill[skill] = self._by_skill.get(skill, ()) + (resource,)

    def resources_for_skill(self, target: str) -> tuple[LearningResource, ...]:
        """
        Resolve any raw or normalized skill name to catalog resources.

        Accepts canonical names, aliases and raw extracted text; unknown
        skills return an empty tuple, never an error.
        """
        canonical = Taxonomy.resolve(target.strip().lower())
        if canonical is None:
            return ()
        return self._by_skill.get(canonical, ())


LearningCatalogInstance = LearningCatalog()
