import frappe
from census_distribution_monitoring_software.setup_data import load_default_data

def execute():
    load_default_data()
