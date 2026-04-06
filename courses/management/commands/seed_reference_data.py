from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models import APIPlan, Course, StudyLevel, StudySubLevel


REFERENCE_COURSES = [
    # Core
    {"domain": "mathematiques", "name": "Mathématiques", "description": "Algèbre, analyse, géométrie, probabilités."},
    {"domain": "francais", "name": "Français / Langue", "description": "Grammaire, orthographe, rédaction, littérature."},
    {"domain": "langues", "name": "Langues", "description": "Langues vivantes et étrangères."},
    {"domain": "anglais", "name": "Anglais", "description": "Cours d’anglais."},
    {"domain": "espagnol", "name": "Espagnol", "description": "Cours d’espagnol."},
    {"domain": "allemand", "name": "Allemand", "description": "Cours d’allemand."},
    {"domain": "histoire", "name": "Histoire", "description": "Histoire ancienne, moderne et contemporaine."},
    {"domain": "geographie", "name": "Géographie", "description": "Géographie physique et humaine."},
    {"domain": "philosophie", "name": "Philosophie", "description": "Notions, auteurs, dissertations, explications de texte."},
    {"domain": "economie", "name": "Économie", "description": "Micro, macro, développement, économie appliquée."},
    {"domain": "education_civique", "name": "Éducation civique / Instruction civique", "description": "Citoyenneté, institutions, droits et devoirs."},
    # Sciences
    {"domain": "physique", "name": "Physique", "description": "Mécanique, électricité, optique, thermodynamique."},
    {"domain": "chimie", "name": "Chimie", "description": "Chimie générale, organique, inorganique."},
    {"domain": "svt", "name": "SVT", "description": "Sciences de la vie et de la Terre."},
    {"domain": "sciences_de_la_terre", "name": "Sciences de la Terre", "description": "Géologie, tectonique, climat, ressources."},
    {"domain": "biologie", "name": "Biologie", "description": "Biologie cellulaire, génétique, physiologie."},
    {"domain": "informatique", "name": "Informatique", "description": "Programmation, algorithmique, systèmes."},
    {"domain": "technologie", "name": "Technologie", "description": "Technologie, conception, systèmes techniques."},
    {"domain": "sciences_numeriques", "name": "Sciences numériques", "description": "Réseaux, données, cybersécurité, numérique."},
    # Arts & sports
    {"domain": "eps", "name": "Éducation physique et sportive", "description": "EPS, sport, entraînement, santé."},
    {"domain": "arts_plastiques", "name": "Arts plastiques", "description": "Dessin, peinture, arts visuels."},
    {"domain": "musique", "name": "Musique", "description": "Éducation musicale, théorie, pratique."},
    {"domain": "theatre", "name": "Théâtre", "description": "Expression, mise en scène, analyse."},
    # Sciences humaines & sociales
    {"domain": "sociologie", "name": "Sociologie", "description": "Sociologie générale et appliquée."},
    {"domain": "psychologie", "name": "Psychologie", "description": "Psychologie cognitive, sociale, clinique."},
    {"domain": "droit", "name": "Droit", "description": "Droit public, privé, procédures, méthodologie."},
    {"domain": "sciences_politiques", "name": "Sciences politiques", "description": "Institutions, relations internationales, politiques publiques."},
    {"domain": "hggsp", "name": "HGGSP", "description": "Histoire-Géographie, Géopolitique, Sciences politiques."},
    # Business
    {"domain": "management", "name": "Management", "description": "Organisation, stratégie, leadership."},
    {"domain": "marketing", "name": "Marketing", "description": "Études de marché, marketing digital, marque."},
    {"domain": "comptabilite", "name": "Comptabilité", "description": "Comptabilité générale, analytique, finance."},
    {"domain": "finance", "name": "Finance", "description": "Finance d’entreprise, marchés, gestion."},
    # STEM extras
    {"domain": "statistiques", "name": "Statistiques", "description": "Statistiques descriptives et inférentielles."},
    {"domain": "probabilites", "name": "Probabilités", "description": "Probabilités et lois usuelles."},
    {"domain": "electronique", "name": "Électronique", "description": "Électronique analogique et numérique."},
    {"domain": "mecanique", "name": "Mécanique", "description": "Mécanique des solides, dynamique."},
    {"domain": "genie_civil", "name": "Génie civil", "description": "Structures, matériaux, construction."},
    # Other
    {"domain": "litterature", "name": "Littérature", "description": "Littérature française et mondiale."},
    {"domain": "communication", "name": "Communication", "description": "Communication écrite/orale, médias."},
    {"domain": "methodologie", "name": "Méthodologie", "description": "Méthodes de travail, dissertation, résumé."},
]


REFERENCE_STUDY_LEVELS = [
    {
        "key": "primaire",
        "name": "Primaire",
        "sublevels": ["CP", "CE1", "CE2", "CM1", "CM2"],
    },
    {
        "key": "college_lycee",
        "name": "Collège/Lycée",
        "sublevels": ["6ème", "5ème", "4ème", "3ème"],
    },
    {
        "key": "secondaire",
        "name": "Secondaire",
        "sublevels": ["Seconde", "Première", "Terminale"],
    },
    {
        "key": "universite",
        "name": "Université",
        "sublevels": ["Licence 1", "Licence 2", "Licence 3", "Master", "Doctorat"],
    },
]

REFERENCE_API_PLANS = [
    {
        "code": "free",
        "name": "Freemium",
        "description": "Accès gratuit avec quotas limités.",
        "billing_period": APIPlan.BILLING_MONTHLY,
        "price_cents": 0,
        "daily_requests_limit": 500,
        "daily_download_limit": 50,
        "max_page_size": 100,
    },
    {
        "code": "starter",
        "name": "Starter",
        "description": "Pour projets personnels et petites équipes.",
        "billing_period": APIPlan.BILLING_MONTHLY,
        "price_cents": 990,
        "daily_requests_limit": 5000,
        "daily_download_limit": 500,
        "max_page_size": 500,
    },
    {
        "code": "starter_yearly",
        "name": "Starter (Annuel)",
        "description": "Starter en facturation annuelle (meilleur prix).",
        "billing_period": APIPlan.BILLING_YEARLY,
        "price_cents": 9900,
        "daily_requests_limit": 5000,
        "daily_download_limit": 500,
        "max_page_size": 500,
    },
    {
        "code": "pro",
        "name": "Pro",
        "description": "Pour usage intensif, recherche et intégrations.",
        "billing_period": APIPlan.BILLING_MONTHLY,
        "price_cents": 4990,
        "daily_requests_limit": 50000,
        "daily_download_limit": 5000,
        "max_page_size": 1000,
    },
    {
        "code": "pro_yearly",
        "name": "Pro (Annuel)",
        "description": "Pro en facturation annuelle (meilleur prix).",
        "billing_period": APIPlan.BILLING_YEARLY,
        "price_cents": 49900,
        "daily_requests_limit": 50000,
        "daily_download_limit": 5000,
        "max_page_size": 1000,
    },
]


def _slug_key(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ç", "c")
        .replace("’", "")
        .replace("'", "")
        .replace("/", "_")
    )


class Command(BaseCommand):
    help = "Seed reference data (courses + study levels + API plans) idempotently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-update",
            action="store_true",
            help="Update name/description/order when an entry already exists.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force_update = options["force_update"]

        created_courses = 0
        updated_courses = 0
        for item in REFERENCE_COURSES:
            course, created = Course.objects.get_or_create(
                domain=item["domain"],
                defaults={"name": item["name"], "description": item.get("description", "")},
            )
            if created:
                created_courses += 1
                continue

            if force_update:
                updates = {}
                if course.name != item["name"]:
                    updates["name"] = item["name"]
                if (course.description or "") != (item.get("description", "") or ""):
                    updates["description"] = item.get("description", "")
                if updates:
                    Course.objects.filter(pk=course.pk).update(**updates)
                    updated_courses += 1

        created_levels = 0
        created_sublevels = 0
        for order, level_item in enumerate(REFERENCE_STUDY_LEVELS):
            level, created = StudyLevel.objects.get_or_create(
                key=level_item["key"],
                defaults={"name": level_item["name"], "order": order},
            )
            if created:
                created_levels += 1
            elif force_update:
                updates = {}
                if level.name != level_item["name"]:
                    updates["name"] = level_item["name"]
                if level.order != order:
                    updates["order"] = order
                if updates:
                    StudyLevel.objects.filter(pk=level.pk).update(**updates)
                    level.refresh_from_db()

            for sub_order, sub_name in enumerate(level_item["sublevels"]):
                sub_key = _slug_key(sub_name)
                _, sub_created = StudySubLevel.objects.get_or_create(
                    level=level,
                    key=sub_key,
                    defaults={"name": sub_name, "order": sub_order},
                )
                if sub_created:
                    created_sublevels += 1
                elif force_update:
                    StudySubLevel.objects.filter(level=level, key=sub_key).update(
                        name=sub_name, order=sub_order
                    )

        created_plans = 0
        updated_plans = 0
        for plan_order, plan_item in enumerate(REFERENCE_API_PLANS):
            plan, created = APIPlan.objects.get_or_create(
                code=plan_item["code"],
                defaults={
                    "name": plan_item["name"],
                    "description": plan_item["description"],
                    "billing_period": plan_item["billing_period"],
                    "price_cents": plan_item["price_cents"],
                    "daily_requests_limit": plan_item["daily_requests_limit"],
                    "daily_download_limit": plan_item["daily_download_limit"],
                    "max_page_size": plan_item["max_page_size"],
                    "is_active": True,
                },
            )
            if created:
                created_plans += 1
                continue

            if force_update:
                updates = {}
                for k in [
                    "name",
                    "description",
                    "billing_period",
                    "price_cents",
                    "daily_requests_limit",
                    "daily_download_limit",
                    "max_page_size",
                ]:
                    if getattr(plan, k) != plan_item[k]:
                        updates[k] = plan_item[k]
                if updates:
                    APIPlan.objects.filter(pk=plan.pk).update(**updates)
                    updated_plans += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed terminé: courses +{created_courses} (maj {updated_courses}), "
                f"levels +{created_levels}, sublevels +{created_sublevels}, "
                f"plans +{created_plans} (maj {updated_plans})."
            )
        )
