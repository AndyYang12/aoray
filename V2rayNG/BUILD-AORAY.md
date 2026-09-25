# aoray NG —— 体积压缩记录 / 两个版本怎么选

基座：v2rayNG 1.8.12 + Xray 引擎 1.8.11（`armeabi-v7a`，minSdk 19 / Android 4.4+）
纯 Java 手搓那条路线已按你的要求放弃。

## 一句话结论

**"装机后 ≤9MB" 物理不可能。** 引擎那颗 `libgojni.so` 单独就是
27,169,852 字节（解压后），压缩进 APK 也要 9.88MB —— 那是 Xray/Go 内核本体，
不是可以"删一删"的东西。所以做不到 9MB 的唯一出路就是你否掉的纯 Java；
既然要真引擎，目标改成「往死里小 + 尽量搬去 SD 卡」。

## 已做的删减（零行为风险）

| 项 | 手法 | 收益（APK 内，压缩后） |
|---|---|---|
| 引擎 aar 里 4 个 ABI → 只留 armeabi-v7a | 重打 aar | 输入 45MB → 9.5MB（APK 不变，构建更快） |
| `geoip.dat` 10.22MB → 0.14MB；`geosite.dat` 1.65 → 0.15MB | 按 protobuf 逐条过滤，只留内置模板真用到的 `cn` / `private` / `category-ads`；文件尾部非 protobuf 字节原样保留 | **-2.55MB**（2.62MB+0.51MB → 37KB+39KB） |
| 语言资源留 en + zh-rCN + zh-rTW | `resConfigs`（顺带剔掉 AndroidX 自带的 ar/fa/ru/vi 翻译） | `resources.arsc` 1.27MB → 0.72MB，**-0.55MB** |
| 删 `montserrat_thin.ttf`（抽屉标题的自定义字体） | 字体只是装饰，删除并去掉 `android:fontFamily` 引用 | **-0.14MB** |
| 上游那版已删的扫码（quickie + barcode native） | 上一轮做的 | -2.83MB |
| `zipAlignEnabled true` | 对齐利于 mmap，不增体积 | — |
| 允许整体装到 SD 卡 | `android:installLocation="preferExternal"` | **装机后内部存储可降到 ~2MB**（见下） |

安全版合计：**19.9MB → 16.4MB**。

## 额外一档：R8 代码压缩（12.7MB，需你在真机点一遍）

再开 `minifyEnabled true` + `shrinkResources true`（上游是关着的），dex 5.43MB → 1.74MB，
总 APK **12.7MB**。我为 Gson 反射面加了 keep 规则（`-keep class com.v2ray.ang.dto.**`
及 gson TypeAdapter/TypeToken/SerializedName 全套）。已验证 dex 里
`dto/ServerConfig`、`service/V2RayVpnService`、`libv2ray/Libv2ray` 都在。

但我不吹没验过的东西：**R8 只在构建层验证，我手上没有 4.4 真机可跑。**
这类 app 用 Gson 直接反射解析配置对象，是 R8 最容易咬到的地方。
所以两个都给你：

- `aoray-ng-1.1-armeabi-v7a.apk` 16.4MB —— 保守版，上游构建方式（不混淆），行为可预期。
- `aoray-ng-r8-armeabi-v7a.apk` 12.7MB —— 最小版，多省 3.7MB。
  用之前必测三点（30 秒）：①粘贴订阅→能解析出节点列表；②点连接→通知栏出现钥匙图标、
  状态变"已连接"；③设置里的"分流/路由"选「绕过大陆」后能正常上谷歌/境外。
  任一失败就退回保守版（R8 出问题的典型表现就是"订阅解析出 0 个节点"或"配置全空"）。

## 「除 7MB 外都放 SD 卡」怎么落实

Android 4.4 时代机制是 `asec` 容器：应用装到外部存储时，**APK 本体和解压出的 lib 都进 SD**，
手机内部只剩下 `files/` 缓存（约 2MB）。所以：

1. APK 已声明 `preferExternal`，正常 ROM 安装时会直接给你 SD 选项；
2. 若装在内部存储，`设置 → 应用 → aoray → 移到 SD 卡` 按钮现在应该出现了（`auto` 才会出现，之前没这属性）；
3. 结果预期：手机内部占用从 ~45MB 降到 ~2MB，SD 卡上那 ~45MB 躲不掉；
4. 老实说风险：4.4 时代不少 OEM ROM 的 SD 容器是 `noexec`，那时 dlopen 会失败 ——
   表现为「能装但一点连接就崩/服务起不来」。真遇到就退回内部存储；
   这条我只能给你判断方向，因为手上没这台设备。
