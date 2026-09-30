from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f.read().splitlines() if line.strip() and not line.startswith("#")]

version = "0.0.1"

setup(
    name="census_distribution_monitoring_software",
    version=version,
    description="Census Distribution Monitoring Software for Frappe Framework",
    author="NexGen ERP Technologies",
    author_email="info@nexgenerptechnologies.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
