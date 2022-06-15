from pkgutil import walk_packages
EXTENSIONS = [package.name for package in walk_packages(__path__, f'{__package__}.')]
