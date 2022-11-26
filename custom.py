# coding=utf-8
import argparse
import sys
import shutil
import os.path
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher/DistributionInfo.h
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher-Appx/MyDistro.appxmanifest
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher-Appx/DistroLauncher-Appx.vcxproj
def init_parser():
    parser = argparse.ArgumentParser(
        prog = 'customer.py',
        description= 'custom some metadata for openEuler WSL project',
    )

    parser.add_argument('-r', '--release')
    return parser

custom_arrary = [
    {
        'file': 'DistroLauncher/DistributionInfo.h',
    },
    {
        'file': 'DistroLauncher-Appx/MyDistro.appxmanifest',
    },
    {
        'file': 'DistroLauncher-Appx/DistroLauncher-Appx.vcxproj',
    }
]
if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()
    print(args.__dict__['release'])
    if not args.release: 
        parser.print_help()
        sys.exit(1)

    for c in custom_arrary:
        src = os.path.join('meta', args.release)
        shutil.copy2(os.path.join(src, c['file']), c['file'])