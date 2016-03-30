from setuptools import setup

setup(
    name="django_validator",
    keywords="validator",
    author="romain_li",
    author_email="romain_li@163.com",
    url="https://github.com/romain-li/django-validator",
    version="0.2.1",
    packages=[
        "django_validator",
    ],
    license="MIT",
    install_requires=[
        "django>=1.4.18",
        "djangorestframework>=2.3.13",
    ],
)
