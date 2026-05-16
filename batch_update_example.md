# 批量更新个性化配置接口使用示例

## 接口信息

- **URL**: `POST /api/batch-update-settings`
- **Content-Type**: `application/json`

## 请求示例

### 示例1: 更新单个字段
```javascript
// 更新背景
uni.request({
  url: 'http://192.168.0.118:8000/api/batch-update-settings',
  method: 'POST',
  data: {
    userSn: '用户的userSn',
    settings: {
      background: 'spring'
    }
  },
  success: (res) => {
    console.log('更新成功', res)
  }
})
```

### 示例2: 同时更新多个字段
```javascript
// 同时更新背景、木槌皮肤和木鱼皮肤
uni.request({
  url: 'http://192.168.0.118:8000/api/batch-update-settings',
  method: 'POST',
  data: {
    userSn: '用户的userSn',
    settings: {
      background: 'summer',
      hammerSkin: 'golden',
      fishSkin: 'jade'
    }
  },
  success: (res) => {
    console.log('更新成功', res)
  }
})
```

### 示例3: 更新所有皮肤相关配置
```javascript
// 批量更新所有皮肤配置
uni.request({
  url: 'http://192.168.0.118:8000/api/batch-update-settings',
  method: 'POST',
  data: {
    userSn: '用户的userSn',
    settings: {
      background: 'winter',
      hammerSkin: 'silver',
      fishSkin: 'gold',
      knockSound: 'wood'
    }
  },
  success: (res) => {
    console.log('更新成功', res)
  }
})
```

## 支持的字段列表

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| fishSkin | string | 木鱼皮肤 | "default", "jade", "gold" |
| hammerSkin | string | 木槌皮肤 | "default", "golden", "silver" |
| knockSound | string | 敲击音效 | "default", "wood", "stone" |
| background | string | 背景图 | "default", "spring", "summer", "autumn", "winter" |
| volume | int | 音量(0-100) | 80 |
| isVibrate | int | 是否震动(0/1) | 1 |
| autoFreq | int | 自动敲击频率(毫秒) | 1000 |
| autoDuration | int | 自动敲击时长(秒),0=永久 | 0 |
| knockText | string | 敲击弹出文字 | "功德+1" |
| isShowBase | int | 是否显示木鱼底座(0/1) | 1 |
| baseSkin | string | 木鱼底座皮肤 | "default" |

## 响应示例

```json
{
  "code": 200,
  "msg": "成功更新 3 个配置项",
  "data": {
    "updatedFields": ["background", "hammerSkin", "fishSkin"],
    "settings": {
      "fishSkin": "jade",
      "hammerSkin": "golden",
      "knockSound": "default",
      "background": "summer",
      "volume": 80,
      "isVibrate": 1,
      "autoFreq": 1000,
      "autoDuration": 0,
      "knockText": "功德+1",
      "isShowBase": 1,
      "baseSkin": "default"
    }
  }
}
```
