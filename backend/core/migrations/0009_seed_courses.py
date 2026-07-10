from django.db import migrations


COURSES = [
    "Software Engineering",
    "UI/UX Design",
    "Data Analytics",
    "CyberSecurity",
]


def seed_courses(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    for name in COURSES:
        Course.objects.get_or_create(name=name)


def unseed_courses(apps, schema_editor):
    Course = apps.get_model("core", "Course")
    Course.objects.filter(name__in=COURSES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_weeklytestattempt"),
    ]

    operations = [
        migrations.RunPython(seed_courses, reverse_code=unseed_courses),
    ]
