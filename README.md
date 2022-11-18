# openeuler WSL support
通过微软的[launcher](https://github.com/microsoft/WSL-DistroLauncher)启动的openeuler发行版
## usage
1. 当前支持sideload 方式加载openeuler，需要先加载DistroLauncher-Appx_xxx_Test目录下的证书，[参考](https://stackoverflow.com/questions/23812471/installing-appx-without-trusted-certificate)
1. 双击Appx_1.0.0.0_arm64.appxbundle 安装openeuler，即可使用

## roadmap
- 支持其他launcher（[wsldl](https://github.com/yuk7/wsldl)，[wsl-distrod](https://github.com/nullpo-head/wsl-distrod)）
- 和openeuler 发布流程集成，持续发布LTS 版本的wsl rootfs和上架windows商店

## contribution
You're wellcome

## LICENSE
MIT