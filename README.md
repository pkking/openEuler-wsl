# openeuler WSL support
通过微软的[launcher](https://github.com/microsoft/WSL-DistroLauncher)启动的openeuler发行版

## build status
[![Build WSL](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml/badge.svg?branch=main)](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml)
## usage
1. 可以通过action里的artifacts下载，超过30天github会自动清理旧的artifacts，可以通过re-run重新生成
1. 当前支持sideload 方式加载openeuler，需要先加载DistroLauncher-Appx_xxx_Test目录下的证书，[参考](https://stackoverflow.com/questions/23812471/installing-appx-without-trusted-certificate)
1. 双击Appx_1.0.0.0_arm64.appxbundle 安装openeuler，即可使用

## prerequisite
相应的github actioin中需要上传证书 https://github.com/microsoft/github-actions-for-desktop-apps#workflows
## roadmap
- 支持其他launcher（[wsldl](https://github.com/yuk7/wsldl)，[wsl-distrod](https://github.com/nullpo-head/wsl-distrod)）
- 和openeuler 发布流程集成，持续发布LTS 版本的wsl rootfs和上架windows商店

## contribution
You're wellcome

## LICENSE
MIT
