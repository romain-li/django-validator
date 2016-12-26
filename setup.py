from setuptools import setup
import django_validator

setup(
    name="django_validator",
    keywords="validator",
    author="romain_li",
    author_email="romain_li@163.com",
    url="https://github.com/romain-li/django-validator",
    description="Django validator with decorators.",
    version=django_validator.VERSION,
    packages=[
        "django_validator",
    ],
    license="MIT",
    install_requires=[
        "django>=1.4.18",
        "djangorestframework>=2.3.13",
    ],
)
