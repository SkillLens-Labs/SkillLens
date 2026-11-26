"""SkillLens V2 shared skill taxonomy.

Single source of truth for skill detection and normalization. The
resume-side extractor (skill_extractor.py), the resume-side normalizer
(skill_normalizer.py) and the JD-side extractor (jd_skill_extractor.py)
all derive their vocabularies from this module, so a skill that can be
detected in one side is always detectable and normalized identically on
the other side.

This module is intentionally dependency-free and deterministic. Category
information is advisory metadata for downstream modules (career
intelligence, recommendation catalog) and never affects matching.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillDefinition:
    """One canonical skill with its aliases and advisory category."""

    canonical: str
    category: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    # Short or English-word aliases ("go", "r") only match with this exact
    # casing plus word boundaries, to avoid false positives.
    case_sensitive_aliases: tuple[str, ...] = field(default_factory=tuple)


LANG = "programming_language"
WEB = "web_framework"
DATA = "data_and_ml"
CLOUD = "cloud_and_devops"
DB = "database"
TOOL = "tool"
BIZ = "business"
SOFT = "soft_skill"
DOMAIN = "domain_knowledge"

_SKILL_DATA: tuple[SkillDefinition, ...] = (
    # Programming languages
    SkillDefinition("python", LANG, ("python3", "python 3", "py")),
    SkillDefinition("java", LANG, ("java 8", "java 11", "java 17", "core java")),
    SkillDefinition("javascript", LANG, ("js", "es6", "ecmascript", "vanilla javascript")),
    SkillDefinition("typescript", LANG, ("ts",)),
    SkillDefinition("golang", LANG, (), ("Go",)),
    SkillDefinition("rust", LANG),
    SkillDefinition("c++", LANG, ("cpp",)),
    SkillDefinition("c#", LANG, ("c sharp", "csharp", "cs")),
    SkillDefinition("c", LANG, (), ("C",)),
    SkillDefinition("sql", LANG, ("ansi sql",)),
    SkillDefinition("nosql", DB),
    SkillDefinition("r", DATA, (), ("R",)),
    SkillDefinition("scala", DATA),
    SkillDefinition("kotlin", LANG),
    SkillDefinition("swift", LANG),
    SkillDefinition("php", LANG),
    SkillDefinition("ruby", LANG),
    SkillDefinition("matlab", LANG),
    SkillDefinition("bash", TOOL, ("shell scripting", "shell", "zsh")),
    SkillDefinition("powershell", TOOL),
    SkillDefinition("vba", TOOL, ("excel vba",)),
    SkillDefinition("dart", LANG, ("flutter",)),
    # Web frameworks / libraries
    SkillDefinition("html", WEB, ("html5",)),
    SkillDefinition("css", WEB, ("css3",)),
    SkillDefinition("sass", WEB, ("scss",)),
    SkillDefinition("react", WEB, ("reactjs", "react.js", "react js", "react 18")),
    SkillDefinition("next.js", WEB, ("nextjs", "next js")),
    SkillDefinition("angular", WEB, ("angularjs", "angular 2+")),
    SkillDefinition("vue.js", WEB, ("vue", "vuejs")),
    SkillDefinition("node.js", WEB, ("node", "nodejs")),
    SkillDefinition("express", WEB, ("expressjs", "express.js")),
    SkillDefinition("nestjs", WEB, ("nest.js", "nest js")),
    SkillDefinition("fastapi", WEB, ("fast api",)),
    SkillDefinition("django", WEB),
    SkillDefinition("flask", WEB),
    SkillDefinition("spring boot", WEB, ("springboot", "spring-boot")),
    SkillDefinition("spring", WEB),
    SkillDefinition("dotnet", WEB, (".net", "asp.net", "dotnet core", "asp.net core")),
    SkillDefinition("laravel", WEB),
    SkillDefinition("rest api", WEB, ("rest", "restful api", "restful apis", "rest apis")),
    SkillDefinition("graphql", WEB),
    SkillDefinition("grpc", WEB),
    SkillDefinition("microservices", WEB, ("microservice architecture", "micro services")),
    SkillDefinition("api design", WEB, ("api development", "api integration")),
    SkillDefinition("tailwind css", WEB, ("tailwind",)),
    # Data & ML
    SkillDefinition("machine learning", DATA, ("ml", "machine-learning", "ml modeling")),
    SkillDefinition("deep learning", DATA, ("deep-learning",)),
    SkillDefinition("natural language processing", DATA, (
        "nlp", "natural-language-processing", "text mining",
    )),
    SkillDefinition("computer vision", DATA, ("cv", "image processing", "opencv")),
    SkillDefinition("reinforcement learning", DATA, ("rl",)),
    SkillDefinition("llm", DATA, (
        "llms", "large language model", "large language models",
        "generative ai", "gen ai", "genai",
    )),
    SkillDefinition("hugging face", DATA, ("huggingface", "transformers",
                                           "transformer models")),
    SkillDefinition("langchain", DATA, ("langgraph", "llamaindex")),
    SkillDefinition("prompt engineering", DATA, ("prompt design",)),
    SkillDefinition("artificial intelligence", DATA, ("ai ml",), ("AI",)),
    SkillDefinition("pandas", DATA),
    SkillDefinition("numpy", DATA),
    SkillDefinition("scikit-learn", DATA, ("sklearn", "scikit learn")),
    SkillDefinition("tensorflow", DATA),
    SkillDefinition("pytorch", DATA),
    SkillDefinition("keras", DATA),
    SkillDefinition("xgboost", DATA, ("lightgbm", "catboost")),
    SkillDefinition("spark", DATA, ("apache spark", "pyspark")),
    SkillDefinition("hadoop", DATA),
    SkillDefinition("kafka", DATA, ("apache kafka",)),
    SkillDefinition("airflow", DATA, ("apache airflow",)),
    SkillDefinition("snowflake", DB),
    SkillDefinition("databricks", DATA),
    SkillDefinition("etl", DATA, ("etl pipelines", "elt", "data pipelines",
                                  "data pipeline")),
    SkillDefinition("data analysis", DATA, ("data analytics", "exploratory data analysis", "eda")),
    SkillDefinition("data science", DATA),
    SkillDefinition("data engineering", DATA),
    SkillDefinition("data visualization", DATA, ("dashboards", "dashboarding")),
    SkillDefinition("statistics", DATA, ("statistical analysis", "hypothesis testing")),
    SkillDefinition("ab testing", DATA, ("a/b testing", "experimentation")),
    SkillDefinition("time series analysis", DATA, ("forecasting",)),
    # Databases
    SkillDefinition("postgresql", DB, ("postgres", "postgres sql")),
    SkillDefinition("mysql", DB, ("mariadb",)),
    SkillDefinition("sqlite", DB),
    SkillDefinition("sql server", DB, ("mssql", "microsoft sql server", "t-sql")),
    SkillDefinition("oracle", DB),
    SkillDefinition("mongodb", DB, ("mongo",)),
    SkillDefinition("redis", DB),
    SkillDefinition("elasticsearch", DB, ("elastic search", "opensearch")),
    SkillDefinition("dynamodb", DB),
    SkillDefinition("cassandra", DB),
    SkillDefinition("database design", DB, ("schema design", "data modeling",
                                            "query optimization")),
    # Cloud & DevOps
    SkillDefinition("aws", CLOUD, ("amazon web services", "ec2", "s3", "lambda")),
    SkillDefinition("azure", CLOUD, ("microsoft azure", "azure devops")),
    SkillDefinition("gcp", CLOUD, ("google cloud", "google cloud platform")),
    SkillDefinition("docker", CLOUD, ("containerization", "containers")),
    SkillDefinition("kubernetes", CLOUD, ("k8s",)),
    SkillDefinition("terraform", CLOUD, ("infrastructure as code", "iac")),
    SkillDefinition("ci/cd", CLOUD, ("ci cd", "cicd", "continuous integration",
                               "continuous deployment", "github actions",
                               "jenkins", "gitlab ci")),
    SkillDefinition("linux", CLOUD, ("unix", "ubuntu")),
    SkillDefinition("git", TOOL, ("version control",)),
    SkillDefinition("github", TOOL, ("gitlab", "bitbucket")),
    SkillDefinition("monitoring", CLOUD, ("observability", "grafana",
                                          "prometheus", "datadog")),
    SkillDefinition("serverless", CLOUD, ("aws lambda",)),
    # Tools & product
    SkillDefinition("jira", TOOL, ("atlassian", "confluence")),
    SkillDefinition("figma", TOOL),
    SkillDefinition("power bi", DATA, ("powerbi",)),
    SkillDefinition("tableau", TOOL),
    SkillDefinition("excel", TOOL, ("microsoft excel", "ms excel", "advanced excel",
                                    "pivot tables", "vlookup")),
    SkillDefinition("salesforce", TOOL, ("crm",)),
    SkillDefinition("sap", TOOL),
    SkillDefinition("postman", TOOL, ("swagger", "openapi")),
    # Business & marketing
    SkillDefinition("agile", BIZ, ("scrum", "sprint planning", "kanban")),
    SkillDefinition("product management", BIZ, ("roadmapping", "product strategy")),
    SkillDefinition("project management", BIZ, ("pmp", "program management")),
    SkillDefinition("stakeholder management", BIZ, ("stakeholder communication",
                                                    "cross-functional collaboration")),
    SkillDefinition("business analysis", BIZ, ("requirements gathering", "gap analysis")),
    SkillDefinition("seo", BIZ, ("search engine optimization",)),
    SkillDefinition("digital marketing", BIZ, ("google analytics", "content marketing",
                                               "email marketing", "social media marketing")),
    SkillDefinition("financial analysis", BIZ, ("financial modeling", "budgeting",
                                                "forecasting models")),
    SkillDefinition("customer service", BIZ, ("client relations", "customer success")),
    # Soft skills
    SkillDefinition("communication", SOFT, ("communication skills", "verbal communication",
                                            "written communication", "presentation skills",
                                            "public speaking")),
    SkillDefinition("leadership", SOFT, ("team leadership", "mentoring", "people management")),
    SkillDefinition("teamwork", SOFT, ("collaboration", "team collaboration")),
    SkillDefinition("problem solving", SOFT, ("analytical thinking", "critical thinking",
                                              "analytical skills")),
    SkillDefinition("time management", SOFT, ("prioritization", "organizational skills")),
    SkillDefinition("adaptability", SOFT, ("flexible", "fast learner", "quick learner")),
    # CS fundamentals & analysis tooling
    SkillDefinition("data structures", DOMAIN, ("dsa",)),
    SkillDefinition("algorithms", DOMAIN, ("algorithm design",)),
    SkillDefinition("system design", DOMAIN, ("distributed systems design",)),
    SkillDefinition("object oriented programming", DOMAIN,
                    ("oop", "object-oriented programming")),
    SkillDefinition("matplotlib", DATA),
    SkillDefinition("jupyter", TOOL, ("jupyter notebook", "jupyter notebooks")),
    SkillDefinition("shap", DATA, ("explainability", "model interpretability",
                                   "interpretability")),
    # Domains
    SkillDefinition("fintech", DOMAIN, ("trading systems", "payments")),
    SkillDefinition("healthcare", DOMAIN, ("hipaa", "clinical data")),
    SkillDefinition("e-commerce", DOMAIN, ("ecommerce", "retail technology")),
    SkillDefinition("cybersecurity", DOMAIN, ("information security", "infosec",
                                              "penetration testing", "owasp")),
)


class SkillTaxonomy:
    """Deterministic lookup tables built once from the skill definitions."""

    def __init__(self) -> None:
        self.definitions: dict[str, SkillDefinition] = {}
        self.alias_to_canonical: dict[str, str] = {}
        self.case_sensitive_alias_to_canonical: dict[str, str] = {}
        self.category_by_canonical: dict[str, str] = {}

        for definition in _SKILL_DATA:
            canonical = definition.canonical
            if canonical in self.definitions:
                raise ValueError(f"Duplicate canonical skill: {canonical}")
            self.definitions[canonical] = definition
            self.category_by_canonical[canonical] = definition.category

            for alias in definition.aliases:
                self._register_alias(alias, canonical, self.alias_to_canonical)
            for alias in definition.case_sensitive_aliases:
                # Case-sensitive aliases keep their original casing: they are
                # matched against the raw text, not the lowercased text.
                self._register_alias(
                    alias, canonical, self.case_sensitive_alias_to_canonical,
                    case_sensitive=True,
                )

    @staticmethod
    def _register_alias(
        alias: str,
        canonical: str,
        target: dict[str, str],
        case_sensitive: bool = False,
    ) -> None:
        key = alias.strip() if case_sensitive else alias.strip().lower()
        existing = target.get(key)
        if existing is not None and existing != canonical:
            raise ValueError(
                f"Alias '{key}' maps to both '{existing}' and '{canonical}'"
            )
        target[key] = canonical

    @property
    def canonical_names(self) -> tuple[str, ...]:
        return tuple(self.definitions)

    @property
    def aliases(self) -> dict[str, str]:
        return dict(self.alias_to_canonical)

    def lookup(self, normalized_text: str) -> str | None:
        """Resolve one normalized alias or canonical name."""
        if normalized_text in self.definitions:
            return normalized_text
        return self.alias_to_canonical.get(normalized_text)

    def lookup_case_sensitive(self, text: str) -> str | None:
        """Resolve one case-sensitive alias (e.g. 'Go', 'R', 'C', 'AI')."""
        key = text.strip()
        canonical = self.case_sensitive_alias_to_canonical.get(key)
        if canonical is not None:
            return canonical
        return self.lookup(key.lower())

    def resolve(self, raw_text: str) -> str | None:
        """Resolve raw extracted text to its canonical skill name."""
        normalized = raw_text.strip().lower()
        canonical = self.lookup(normalized)
        if canonical is not None:
            return canonical
        return self.case_sensitive_alias_to_canonical.get(raw_text.strip())


Taxonomy = SkillTaxonomy()
