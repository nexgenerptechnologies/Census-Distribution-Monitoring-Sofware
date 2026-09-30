app_name = "census_distribution_monitoring_software"
app_title = "Census Distribution Monitoring Software"
app_publisher = "NexGen ERP Technologies"
app_description = "Census Distribution Monitoring Software for Frappe Framework v15 and v16"
app_email = "info@nexgenerptechnologies.com"
app_license = "mit"
required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/census_distribution_monitoring_software/css/census_app.css"
# app_include_js = "/assets/census_distribution_monitoring_software/js/census_app.js"

# include js, css files in header of web template
web_include_css = "/assets/census_distribution_monitoring_software/css/portal.css"
web_include_js = "/assets/census_distribution_monitoring_software/js/portal.js"

# Website Route Rules
website_route_rules = [
    {"from_route": "/portal", "to_route": "tracking"},
    {"from_route": "/distribution", "to_route": "tracking"},
]

# Fixtures to export and import on install
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["Census Portal User", "Census Manager"]]]},
    {"dt": "Census State"},
    {"dt": "Census Item"},
]

after_install = "census_distribution_monitoring_software.setup_data.after_install"
after_migrate = "census_distribution_monitoring_software.setup_data.after_migrate"

# DocType Events
# doc_events = {
#     "Census Dispatch": {
#         "on_submit": "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_dispatch.census_dispatch.on_submit",
#         "on_cancel": "census_distribution_monitoring_software.census_distribution_monitoring_software.doctype.census_dispatch.census_dispatch.on_cancel",
#     }
# }
