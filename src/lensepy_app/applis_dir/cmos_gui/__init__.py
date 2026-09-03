import argparse

def init_app(application):
    application = application
    xml_data = application.manager.xml_app
    print(f'XML = {xml_data}')

    # Check options
    parse_version_choices = ["1A", "2A", "3A"]
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "app_name",
        type=str,
        help="Name of the application"
    )

    parser.add_argument(
        "--VI",
        action="store_true",
        help="Machine Vision version"
    )
    args = parser.parse_args()

    # Check options
    suffix = "vi" if args.VI else ""

    if suffix != "":
        application.config_name = f"{application.appli_root}/config/appli_{suffix}.xml"
    else:
        application.config_name = f"{application.appli_root}/config/appli.xml"

    print(application.config_name)