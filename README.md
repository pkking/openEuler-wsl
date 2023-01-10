# openeuler WSL support
通过微软的[launcher](https://github.com/microsoft/WSL-DistroLauncher)启动的openeuler发行版

## build status
[![Build WSL](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml/badge.svg?branch=main)](https://github.com/pkking/openEuler-wsl/actions/workflows/wsl.yaml)
## install
1. 可以通过action里的artifacts下载，超过30天github会自动清理旧的artifacts，可以通过re-run重新生成
1. 当前支持sideload 方式加载openeuler应用：
    1. 将`sideload-xxx.zip`解压后，进入`DistroLaucher-xxx_Test`目录
    1. 加载目录下的证书`xxx.cer`文件，[参考](https://stackoverflow.com/questions/23812471/installing-appx-without-trusted-certificate)，简单来说：
        1. 双击`xxx.cer`
        1. 选择`local machine`
        1. 选择`trusted people`
    1. 双击`DistroLauncher-Appx_xxx_<arm64/x64>.appxbundle` 安装openeuler WSL应用


## roadmap
- [ ] 支持其他launcher（[wsldl](https://github.com/yuk7/wsldl)，[wsl-distrod](https://github.com/nullpo-head/wsl-distrod)）
- [ ] 和openeuler 发布流程集成，持续发布LTS 版本的wsl rootfs，旁加载应用
- [ ] 在openEuler的基础设施中构建APP和rootfs，`github action`用户开发者自定义
- [x] 20.03 LTS SP3上架windows商店
- [x] 22.03 LTS 上架windows商店
- [ ] 22.09 上架windows商店
- [ ] systemd 正常工作并开启namespace
 
## contribution
You're wellcome

## LICENSE
MIT

# how to customize my own WSL
1. fork本仓库
2. 根据需要，修改本仓库代码（例如要增删包，可以修改`docker/Dockerfile`）
3. 根据[该文档](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-self-signed-certificate)生成一个自签发的证书，后缀为pfx
4. 修改`DistroLauncher-Appx/MyDistro.appxmanifest`中的`Publisher=`字段，将其改为与上面的证书CN字段一致
5. 修改`DistroLauncher-Appx/DistroLauncher-Appx.vcxproj`中的`<PackageCertificateThumbprint>`字段，将其改为上面证书的指纹和证书`CN`字段，获取`CN`/`PackageCertificateThumbprint`的方法如下：
```powershell
PS C:\> Get-PfxCertificate -FilePath .\DistroLauncher-Appx_TemporaryKey.pfx

Thumbprint                                Subject
----------                                -------
asdfsadfadfs9asdfasdfsadfE1FC8AC90C26DE1  CN=xxxadsfasdfsadf
```
## 没有微软开发者账号和azure AD
6. 进入仓库`setting->secrets->actions->new secrets`，创建以下secrets
- SIGN_CERT：内容为证书的base64编码，base64编码生成方式为：
```powershell
$fileContentBytes = get-content 'YOURFILEPATH.pfx' -Encoding Byte
[System.Convert]::ToBase64String($fileContentBytes)
```
## 有微软开发者账号
6. fork本仓库
7. 进入仓库`setting->secrets->actions->new secrets`，创建以下secrets
- AZURE_AD_APP_KEY
- AZURE_AD_CLIENT_ID
- AZURE_AD_TENANT_ID
- SIGN_CERT

AZURE这几个变量，请参考[这里](https://github.com/marketplace/actions/windows-store-publish#prerequisites)的步骤生成
SIGN_CERT请参考上面的步骤

修改后，通过点击`actioin`中的`run workflow`就能生成对应的WSL软件包（如果没有开发者账号或不期望发布到应用商店，`Should we upload the appxbundle to the store`这个参数请输入`no`，否则输入`yes`），对应任务的summary页面中，可以下载所有生成的`artifacts`，其中`rootfs-xxx`是用于制作WSL的文件系统，`siteload-xxx`是可以直接通过双击安装的app软件包，`storeupload-`则是用于上传到微软商店的app软件包

**注意**：本仓库的脚本只能更新已有应用的提交，因此新创建的应用需要人工进行第一次提交，可以参考[如何人工提交](https://learn.microsoft.com/zh-cn/windows/apps/publish/publish-your-app/create-app-submission?pivots=store-installer-msix)
