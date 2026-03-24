#!/usr/bin/env python3
import argparse


def main():
    parser = argparse.ArgumentParser(description='Install Argos Translate package for a language pair.')
    parser.add_argument('--from-code', default='en')
    parser.add_argument('--to-code', default='zh')
    args = parser.parse_args()

    import argostranslate.package

    packages = argostranslate.package.get_available_packages()
    match = None
    for pkg in packages:
        if pkg.from_code == args.from_code and pkg.to_code == args.to_code:
            match = pkg
            break
    if not match:
        raise SystemExit(f'No Argos model found for {args.from_code}->{args.to_code}')

    download_path = match.download()
    argostranslate.package.install_from_path(download_path)
    print(f'installed={args.from_code}->{args.to_code}')


if __name__ == '__main__':
    main()
