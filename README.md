# openeuler WSL support
通过微软的[launcher](https://github.com/microsoft/WSL-DistroLauncher)启动的openeuler发行版

## build status
[![Build WSL](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml/badge.svg?branch=main)](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml)
## usage
1. 可以通过action里的artifacts下载，超过30天github会自动清理旧的artifacts，可以通过re-run重新生成
1. 当前支持sideload 方式加载openeuler，需要先加载DistroLauncher-Appx_xxx_Test目录下的证书，[参考](https://stackoverflow.com/questions/23812471/installing-appx-without-trusted-certificate)
1. 双击Appx_xxx_arm64/x64.appxbundle 安装openeuler，即可使用

## prerequisite
相应的github actioin中需要上传证书 https://github.com/microsoft/github-actions-for-desktop-apps#workflows
## roadmap
- 支持其他launcher（[wsldl](https://github.com/yuk7/wsldl)，[wsl-distrod](https://github.com/nullpo-head/wsl-distrod)）
- 和openeuler 发布流程集成，持续发布LTS 版本的wsl rootfs和上架windows商店

## contribution
You're wellcome

## LICENSE
MIT

# how to customize my own WSL
1. fork本仓库
1. 根据需要，修改本仓库代码（例如要增删包，可以修改`docker/Dockerfile`）
1. 根据[该文档](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-self-signed-certificate)生成一个自签发的证书，后缀为pfx
1. 修改`DistroLauncher-Appx/MyDistro.appxmanifest`中的`Publisher=`字段，将其改为与上面的证书CN字段一致
1. 修改`DistroLauncher-Appx/DistroLauncher-Appx.vcxproj`中的`<PackageCertificateThumbprint>`字段，将其改为上面证书的指纹
## 没有微软开发者账号和azure AD
1. 进入仓库`setting->secrets->actions->new secrets`，创建以下secrets
- SIGN_CERT：证书的base64编码，生成方式为：
```powershell
$fileContentBytes = get-content 'YOURFILEPATH.pfx' -Encoding Byte
[System.Convert]::ToBase64String($fileContentBytes)
```
## 有微软开发者账号
1. fork本仓库
1. 进入仓库`setting->secrets->actions->new secrets`，创建以下secrets
- AZURE_AD_APP_KEY
- AZURE_AD_CLIENT_ID
- AZURE_AD_TENANT_ID
- SIGN_CERT

AZURE这几个变量，请参考[这里](https://github.com/marketplace/actions/windows-store-publish#prerequisites)的步骤生成
1. 修改后，通过github actioin就能生成对应的WSL软件包，其中rootfs是用于制作WSL的文件系统，siteload-xxx是可以直接通过双击安装的appxbundle格式的app软件包，storeupload则是用于上传到微软商店的app软件包
