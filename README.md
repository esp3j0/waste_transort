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

3. 安装后端依赖
   ```cmd
   # 安装python所需依赖
   cd backend
   pip install -r requirements.txt
   ```

## quick start

### 前端

运行以下命令，编译前端文件，然后使用微信小程序打开前端front目录。
```cmd
cd front
yarn dev:app
```
### 后端

windows中执行以下命令。
```cmd
cd backend
./start.bat
```

## pr流程

### 更新代码到自己的分支

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

### 提交代码到main分支

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

4. 合并PR

# 需求文档

## 页面原型

## 电子联单说明

用户填写并提交订单 ，然后订单中的地址会关联到小区，又因为物业会管理一堆小区，所以可以找到与该物业相关的订单，然后每个物业拥有一个物业主管理员，和一些非主管理员，这些管理员可以看到与该物业相关的订单，但是非主管理员只能看到与自身相关的小区的订单，管理员需要做的就是对订单进行离场确认，此时会将该管理员的信息和确认时间更新到订单中， 之后就是运输端按照规范运输... 处置端完成回收确认...

## 订单说明
首先用户下单时候会根据填写的信息生成大概的费用并支付，之后订单会进入调度算法，调度算法（暂未实现，暂时随机选取一家物业公司和一家处置回收公司）会将订单派送给调度管理员，并指定订单需要到达的处置回收站，调度管理员可以派单给司机，订单状态变成已派单，这时司机可以看到相应订单，接下来司机调用订单更新，将订单状态改为车辆出发前往建筑垃圾位置。车辆到达指定地点后，司机调用订单更新，将订单状态改为已到达清运位置，同时需要司机对垃圾进行现场拍照，当车辆装好后，司机调用订单更新，将订单状态改为车辆出发前往处置回收站，同时要求司机对清理后的现场进行拍照，当司机到达处置回收站后，订单状态改为车辆已到达置回收站。处置回收站员（过磅员）主要是对车辆进行称重管理，称重完成，生成最终账单，多了就退款，代表整个任务完成。

## 后端角色
每个账号注册后都会对应一个app/models/user.py中的一个User模型，User模型中的role有5中类型，类型如下：
```
class UserRole(StrEnum):
   """用户角色枚举"""
   CUSTOMER = "customer"  # 用户下单端用户
   PROPERTY = "property"  # 物业管理端用户
   TRANSPORT = "transport"  # 运输管理端用户
   RECYCLING = "recycling"  # 处置回收端用户
   ADMIN = "admin"  # 系统管理员
```
首先通过User.role来区分不同端的用户。因为物业管理端有多家物业管理公司，运输管理端有多家运输管理公司，处置回收端有多家处置回收公司，所以物业管理端用户与物业管理公司是多对多的关系，其余两端同理。多对多关系需要一张表来记录，物业管理端用户与物业管理公司使用PropertyManager表来管理，为了区分公司内人员角色，使用了PropertyManager.is_primary和PropertyManager.role来进行管理。当PropertyManager.is_primary==True时候，该用户代表该物业公司的最高管理员，当PropertyManager.is_primary==False的时候，使用PropertyManager.role来区分该公司的不同普通角色，物业管理人员只有主管理员和普通管理员，所以并没有使用这个字段来做权限管理。但是运输管理端需要使用这个字段来区分调度员和司机。
### 用户下单端
任何用户均可以在线注册和下单，权限一致，该端只有手机小程序。

#### 普通用户-小程序端

1. 地址管理
   - [ ] 地址信息增删改
   - [ ] 选择默认

2. 下单清运
   - [ ] 地址选择，自动选择默认地址
      - [ ] 地图选点
      - [ ] 小区自动匹配(无法匹配则显示无小区)/手动选择
   - [ ] 清运表格
   - [ ] 费用清算
   - [ ] 在线支付

3. 装修报备
   - [ ] 地址选择，自动选择默认地址
      - [ ] 地图选点
      - [ ] 小区自动匹配(无法匹配则显示无小区)/手动选择
   - [ ] 报备表格

### 物业管理端
每个物业分配一个该物业的最高管理员，可以增删改查当前物业的普通管理员信息，普通管理员可以
#### 物业管理端最高管理员(User.role==UserRole.PROPERTY&&PropertyManager.is_primary==True)-电脑端 -> 区分不同物业公司

1. 对其所管理的小区增删改查

2. 对其所管理的人员增删改查

3. 当前物业的装修报备情况

#### 物业管理端管理员(User.role==UserRole.PROPERTY&&PropertyManager.is_primary==False)-小程序端

1. 当前物业的装修报备情况

2. 查看对当前物业的运输清单，确认司机离开

### 运输管理端
每个运输公司分配一个该公司的最高管理员，多个该运输公司的的调度员，多个该运输公司的的司机。
#### 运输管理端最高管理员(User.role==UserRole.TRANSPORT&&TransportManager.is_primary==True) -> 区分不同运输公司
1. 对其所管理的司机增删改查
2. 对其管理的车辆增删改查
3. 对所在的运输公司的信息进行修改

#### 运输管理端调度员(User.role==UserRole.TRANSPORT&&TransportManager.is_primary==False&&TransportManager.role==TransportRole.DISPATCHER)
1. 接收订单，该订单会被关联到运输管理端调度员所在的运输公司，订单变为已派单状态
2. 取消订单，该订单会重新进入调度算法
2. 将订单分配自家的司机，修改司机状态信息为忙碌

#### 运输管理端司机(User.role==UserRole.TRANSPORT&&TransportManager.is_primary==False&&TransportManager.role==TransportRole.DRIVER)

1. 查看被分配到的订单
2. 订单更新-前往建筑垃圾位置
3. 订单更新-到达建筑垃圾位置，同时上传现场垃圾照片
4. 订单更新-前往处置回收站，同时上传已清理完的垃圾现场
5. 订单更新-已到达置回收站，修改司机状态信息为可用

### 处置回收端

...

## 模型
=======
4. 合并PR，