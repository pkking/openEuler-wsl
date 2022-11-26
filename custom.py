# coding=utf-8
import argparse
import sys
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher/DistributionInfo.h
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher-Appx/MyDistro.appxmanifest
#          sed -i 's/22.03/${{ matrix.release }}/g' DistroLauncher-Appx/DistroLauncher-Appx.vcxproj
def init_parser():
    parser = argparse.ArgumentParser(
        prog = 'customer.py',
        description= 'custom some metadata for openEuler WSL project',
    )

    parser.add_argument('-r', '--release')
    parser.add_argument('-p', '--place_holder', default='place_holder')
    return parser

custom_arrary = [
    {
        'file': 'DistroLauncher/DistributionInfo.h',
        'origin': 'place_holder',
        'replace': 'release',
    },
    {
        'file': 'DistroLauncher-Appx/MyDistro.appxmanifest',
        'origin': 'place_holder',
        'replace': 'release',
    },
    {
        'file': 'DistroLauncher-Appx/DistroLauncher-Appx.vcxproj',
        'origin': 'place_holder',
        'replace': 'release',
    }
]
if __name__ == '__main__':
    parser = init_parser()
    args = parser.parse_args()
    print(args.__dict__['release'])
    if not args.release or not args.place_holder: 
        parser.print_help()
        sys.exit(1)

    for d in custom_arrary:
        with open(d['file'], 'r+', encoding='utf-8') as f:
            output = f.read().replace(args.__dict__[d['origin']], args.__dict__[d['replace']])
            f.seek(0)
            f.write(output)
