import argparse

def init_app(application):
    application = application
    xml_data = application.manager.xml_app
    print(f'XML = {xml_data}')

    # Check options
    parse_version_choices = ["1A", "2A", "3A"]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        type=str,
        choices=parse_version_choices,
        default="NO",
        help=f"Version to use (choices: {parse_version_choices})"
    )

    parser.add_argument(
        "app_name",
        type=str,
        help="Name of the application"
    )

    parser.add_argument(
        "--image",
        action="store_true",
        help="Image mode only (no camera)"
    )
    args = parser.parse_args()

    print("Version choisie :", args.version)
    # Check options
    version = "1A" if args.version == "NO" else args.version
    suffix = "_image" if args.image else ""

    application.config_name = f"{application.appli_root}/config/appli_{version}{suffix}.xml"
