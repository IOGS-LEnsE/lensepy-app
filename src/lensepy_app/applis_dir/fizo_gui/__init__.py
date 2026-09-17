import argparse

def init_app(application):
    application = application
    xml_data = application.manager.xml_app
    print(f'XML = {xml_data}')

    # Check options
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "app_name",
        type=str,
        help="Name of the application"
    )

    parser.add_argument(
        "--old",
        action="store_true",
        help="Image mode only (no camera)"
    )
    args = parser.parse_args()

    # Check options
    suffix = "_old" if args.old else ""

    application.config_name = f"{application.appli_root}/config/appli{suffix}.xml"
