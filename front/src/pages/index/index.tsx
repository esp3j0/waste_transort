import { View, Text, Button } from '@tarojs/components'
import { useLoad } from '@tarojs/taro'
import Taro from '@tarojs/taro'
import './index.scss'

export default function Index () {
  useLoad(() => {
    console.log('Page loaded.')
  })

  const handleWxLogin = async () => {
    try {
      // 1. 调用微信登录接口获取code
      const loginRes = await Taro.login()
      if (!loginRes.code) {
        Taro.showToast({
          title: '登录失败',
          icon: 'error'
        })
        return
      }

      // 2. 调用后端登录接口
      const res = await Taro.request({
        url: 'http://localhost:8000/api/v1/auth/wx-login',
        method: 'POST',
        data: {
          code: loginRes.code
        }
      })

      if (res.statusCode === 200 && res.data.access_token) {
        // 保存token
        Taro.setStorageSync('token', res.data.access_token)
        Taro.showToast({
          title: '登录成功',
          icon: 'success'
        })
      } else {
        Taro.showToast({
          title: '登录失败',
          icon: 'error'
        })
      }
    } catch (error) {
      console.error('登录错误:', error)
      Taro.showToast({
        title: '登录出错',
        icon: 'error'
      })
    }
  }

  return (
    <View className='index'>
      <Text>Hello world!</Text>
      <Button onClick={handleWxLogin}>微信登录</Button>
    </View>
  )
}
