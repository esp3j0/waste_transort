# 开发指南

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