CREATE DATABASE IF NOT EXISTS muyu_db
CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE muyu_db;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '内部自增主键，仅后端使用',
    user_sn VARCHAR(32) NOT NULL UNIQUE COMMENT '用户对外唯一编码（U+15位字母数字）',
    openid VARCHAR(100) UNIQUE NULL COMMENT '微信openid（微信登录/捆绑用，未捆绑则为空）',
    nickname VARCHAR(50) NULL COMMENT '用户昵称',
    avatar VARCHAR(255) NULL COMMENT '用户头像地址（本地用static目录，上线用OSS）',
    phone VARCHAR(20) UNIQUE NULL COMMENT '手机号（手机号登录用，未注册则为空）',
    merit_count BIGINT DEFAULT 0 COMMENT '累计功德数（核心字段）',
    province VARCHAR(50) NULL COMMENT '所在省份（用于省份排行榜）',
    status TINYINT DEFAULT 1 COMMENT '账号状态：1正常，0禁用',
    last_active_at DATETIME NULL DEFAULT NULL COMMENT '最后活跃时间，用于登录态校验与续期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    KEY idx_merit_count (merit_count),
    KEY idx_province (province)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户基础表';

CREATE TABLE IF NOT EXISTS user_settings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '配置主键',
    user_id BIGINT NOT NULL UNIQUE COMMENT '关联users表的id（一对一）',
    fish_skin VARCHAR(50) DEFAULT 'default' COMMENT '木鱼皮肤标识',
    hammer_skin VARCHAR(50) DEFAULT 'default' COMMENT '木槌皮肤标识',
    knock_sound VARCHAR(50) DEFAULT 'default' COMMENT '敲击音效标识',
    background VARCHAR(50) DEFAULT 'default' COMMENT '背景图标识',
    volume INT DEFAULT 80 COMMENT '音量（0-100）',
    is_vibrate TINYINT DEFAULT 1 COMMENT '是否震动：1开启，0关闭',
    auto_freq INT DEFAULT 1000 COMMENT '自动敲击频率（毫秒）',
    auto_duration INT DEFAULT 0 COMMENT '自动敲击时长（秒）：0=永久',
    knock_text VARCHAR(100) DEFAULT '阿弥陀佛' COMMENT '敲击弹出文字',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户个性化配置表';

CREATE TABLE IF NOT EXISTS user_levels (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '等级主键',
    level INT UNIQUE NOT NULL COMMENT '等级数字（1~6，可扩展）',
    level_name VARCHAR(50) NOT NULL COMMENT '等级称号',
    min_merit BIGINT NOT NULL COMMENT '等级最低功德门槛',
    max_merit BIGINT NOT NULL COMMENT '等级最高功德上限',
    color VARCHAR(50) DEFAULT '#ffffff' COMMENT '等级文字颜色',
    status TINYINT DEFAULT 1 COMMENT '状态：1启用，0禁用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户等级配置表';

INSERT IGNORE INTO user_levels (level, level_name, min_merit, max_merit, color, status) VALUES
(1, '初心者', 0, 999, '#9E9E9E', 1),
(2, '静心者', 1000, 4999, '#4FC3F7', 1),
(3, '禅修者', 5000, 19999, '#66BB6A', 1),
(4, '功德者', 20000, 99999, '#FFCA28', 1),
(5, '禅尊者', 100000, 499999, '#FF7043', 1),
(6, '圆满者', 500000, 9999999, '#AB47BC', 1);