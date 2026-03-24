import argparse

def init_app(application):
    parser = argparse.ArgumentParser()
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

    # Check options
    suffix = "_image" if args.image else ""
    application.config_name = f"{application.appli_root}/config/appli{suffix}.xml"
