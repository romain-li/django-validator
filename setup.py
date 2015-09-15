from setuptools import setup

setup(
    name="django_validator",
    version="0.1.1",
    packages=[
        "django_validator",
    ],
    install_requires=[
        "django>=1.4.18",
        "djangorestframework>=2.3.13",
    ],
)
