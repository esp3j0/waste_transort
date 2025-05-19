# 开发指南

## 依赖

1. 安装开发环境
   - 安装 Python 3.11
   - 安装 Node.js

2. 安装前端依赖
   ```cmd
   # 全局安装 yarn 包管理器
   npm install -g yarn
   
   # 进入前端目录并安装项目依赖
   cd front
   yarn install
   ```

## 运行

```cmd
cd front
yarn dev:app
```

## 更新代码到自己的分支

1. 切换到自己的develop分支
```bash
git chceckout -b xxx_dev
```
2. 拉取最新代码
```bash
git fetch
```
3. 将main分支合并到自己的develop分支
```bash
git merge origin/main
```

## 提交代码到main分支

1. 切换到自己的develop分支
```bash
git chceckout -b xxx_dev
```
2. 提交代码
```bash
git add .
git commit -m "xxx"
git push origin xxx_dev
```
3. 打开github 提交PR
4. 合并PR，