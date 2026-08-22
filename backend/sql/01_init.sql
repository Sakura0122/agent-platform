-- Final MySQL schema assembled from Alembic revisions through d858feccac09.
-- This is a standalone schema script; Alembic's alembic_version table is intentionally omitted.

CREATE DATABASE IF NOT EXISTS `agent_platform`
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `agent_platform`;

SET NAMES utf8mb4;

-- 用户表
CREATE TABLE IF NOT EXISTS `users`
(
    `id`              CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `username`        VARCHAR(50)  NOT NULL COMMENT '用户名',
    `email`           VARCHAR(100) NOT NULL COMMENT '邮箱',
    `hashed_password` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `is_active`       TINYINT(1)   NOT NULL COMMENT '是否启用',
    `is_superuser`    TINYINT(1)   NOT NULL COMMENT '是否为超级管理员',
    `last_login`      DATETIME     NULL COMMENT '最后登录时间',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`      DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `ix_users_email` (`email`),
    UNIQUE KEY `ix_users_username` (`username`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '用户表';

-- 权限表
CREATE TABLE IF NOT EXISTS `permissions`
(
    `id`          CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `code`        VARCHAR(100) NOT NULL COMMENT '权限编码',
    `name`        VARCHAR(100) NOT NULL COMMENT '权限名称',
    `description` VARCHAR(200) NULL COMMENT '权限描述',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`  DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_permissions_code` (`code`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '权限表';

-- 角色表
CREATE TABLE IF NOT EXISTS `roles`
(
    `id`          CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `code`        VARCHAR(100) NOT NULL COMMENT '角色编码',
    `name`        VARCHAR(100) NOT NULL COMMENT '角色名称',
    `description` VARCHAR(200) NULL COMMENT '角色描述',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`  DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_roles_code` (`code`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '角色表';

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS `role_permissions`
(
    `id`            CHAR(36) NOT NULL COMMENT '业务表主键 UUID',
    `role_id`       CHAR(36) NOT NULL COMMENT '角色 UUID',
    `permission_id` CHAR(36) NOT NULL COMMENT '权限 UUID',
    `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_role_permissions_pair` (`role_id`, `permission_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '角色权限关联表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS `user_roles`
(
    `id`         CHAR(36) NOT NULL COMMENT '业务表主键 UUID',
    `user_id`    CHAR(36) NOT NULL COMMENT '用户 UUID',
    `role_id`    CHAR(36) NOT NULL COMMENT '角色 UUID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_user_roles_pair` (`user_id`, `role_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '用户角色关联表';

-- 模型供应商表
CREATE TABLE IF NOT EXISTS `model_providers`
(
    `id`          CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `name`        VARCHAR(100) NOT NULL COMMENT '供应商名称',
    `type`        VARCHAR(50)  NOT NULL COMMENT '供应商类型: openai/anthropic/aliyun/azure/local/custom',
    `status`      VARCHAR(50)  NOT NULL COMMENT '连接状态: connected/disconnected/error',
    `endpoint`    VARCHAR(500) NOT NULL COMMENT 'API端点地址',
    `api_key`     TEXT         NULL COMMENT 'API密钥（加密存储）',
    `description` VARCHAR(500) NULL COMMENT '供应商描述',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`  DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '模型供应商表';

-- 模型表
CREATE TABLE IF NOT EXISTS `models`
(
    `id`             CHAR(36)       NOT NULL COMMENT '业务表主键 UUID',
    `name`           VARCHAR(100)   NOT NULL COMMENT '模型显示名称',
    `model_id`       VARCHAR(100)   NOT NULL COMMENT '模型标识符，如 gpt-4',
    `provider_id`    CHAR(36)       NOT NULL COMMENT '所属供应商 UUID',
    `capabilities`   VARCHAR(500)   NULL COMMENT '能力标签，逗号分隔: function_call,vision,streaming',
    `context_length` INT            NOT NULL COMMENT '上下文窗口大小',
    `status`         VARCHAR(50)    NOT NULL COMMENT '状态: available/unavailable/rate_limited',
    `input_price`    DECIMAL(10, 6) NOT NULL COMMENT '输入价格（每1K tokens）',
    `output_price`   DECIMAL(10, 6) NOT NULL COMMENT '输出价格（每1K tokens）',
    `currency`       VARCHAR(10)    NOT NULL COMMENT '货币单位',
    `is_default`     TINYINT(1)     NOT NULL COMMENT '是否为默认模型',
    `description`    TEXT           NULL COMMENT '模型描述',
    `created_at`     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`     DATETIME       NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_models_model_id` (`model_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '模型表';

-- 知识库表
CREATE TABLE IF NOT EXISTS `knowledge_bases`
(
    `id`                   CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `name`                 VARCHAR(200) NOT NULL COMMENT '知识库名称',
    `description`          VARCHAR(500) NULL COMMENT '描述',
    `status`               VARCHAR(50)  NOT NULL COMMENT '状态: ready/indexing/error/empty',
    `document_count`       INT          NOT NULL COMMENT '文档数量',
    `segment_count`        INT          NOT NULL COMMENT '分段数量',
    `embedding_model`      VARCHAR(100) NOT NULL COMMENT '向量化模型',
    `created_by`           VARCHAR(100) NULL COMMENT '创建者',
    `chunk_method`         VARCHAR(20)  NOT NULL COMMENT '分段方式: fixed/sentence/paragraph',
    `chunk_size`           INT          NOT NULL COMMENT '分段大小（tokens）',
    `chunk_overlap`        INT          NOT NULL COMMENT '重叠大小（tokens）',
    `retrieval_strategy`   VARCHAR(20)  NOT NULL COMMENT '检索策略: vector/fulltext/hybrid',
    `top_k`                INT          NOT NULL COMMENT '返回结果数',
    `similarity_threshold` FLOAT        NOT NULL COMMENT '相似度阈值',
    `created_at`           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`           DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '知识库表';

-- 提示词表
CREATE TABLE IF NOT EXISTS `prompts`
(
    `id`          CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `name`        VARCHAR(200) NOT NULL COMMENT 'Prompt 名称',
    `description` VARCHAR(500) NULL COMMENT '描述',
    `category`    VARCHAR(50)  NOT NULL COMMENT '分类',
    `tags`        JSON         NULL COMMENT '标签列表，JSON 数组',
    `content`     TEXT         NOT NULL COMMENT 'Prompt 正文内容',
    `variables`   JSON         NULL COMMENT '变量定义，JSON 数组',
    `version`     VARCHAR(50)  NOT NULL COMMENT '当前版本号',
    `status`      VARCHAR(50)  NOT NULL COMMENT '状态: draft/published',
    `created_by`  VARCHAR(100) NULL COMMENT '创建者',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`  DATETIME     NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '提示词表';

-- 知识库文档表
CREATE TABLE IF NOT EXISTS `documents`
(
    `id`                CHAR(36)      NOT NULL COMMENT '业务表主键 UUID',
    `knowledge_base_id` CHAR(36)      NOT NULL COMMENT '所属知识库 UUID',
    `file_name`         VARCHAR(500)  NOT NULL COMMENT '文件名',
    `file_type`         VARCHAR(50)   NOT NULL COMMENT '文件类型: pdf/docx/md/txt/html/csv',
    `file_size`         VARCHAR(50)   NULL COMMENT '文件大小',
    `status`            VARCHAR(50)   NOT NULL COMMENT '处理状态: pending/processing/completed/failed',
    `segment_count`     INT           NOT NULL COMMENT '分段数量',
    `word_count`        INT           NOT NULL COMMENT '字数',
    `error_message`     TEXT          NULL COMMENT '错误信息',
    `uploaded_by`       VARCHAR(100)  NULL COMMENT '上传者',
    `minio_path`        VARCHAR(1000) NULL COMMENT 'MinIO 存储路径',
    `processed_at`      DATETIME      NULL COMMENT '处理完成时间',
    `created_at`        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`        DATETIME      NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '知识库文档表';

-- 提示词版本表
CREATE TABLE IF NOT EXISTS `prompt_versions`
(
    `id`           CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `prompt_id`    CHAR(36)     NOT NULL COMMENT '所属 Prompt UUID',
    `version`      VARCHAR(50)  NOT NULL COMMENT '版本号',
    `content`      TEXT         NOT NULL COMMENT '该版本的内容快照',
    `changelog`    VARCHAR(500) NULL COMMENT '变更说明',
    `is_current`   TINYINT(1)   NOT NULL COMMENT '是否为当前版本',
    `published_by` VARCHAR(100) NULL COMMENT '发布者',
    `published_at` DATETIME     NULL COMMENT '发布时间',
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '提示词版本表';

-- 文档分段表
CREATE TABLE IF NOT EXISTS `segments`
(
    `id`                CHAR(36) NOT NULL COMMENT '业务表主键 UUID',
    `knowledge_base_id` CHAR(36) NOT NULL COMMENT '所属知识库 UUID',
    `document_id`       CHAR(36) NOT NULL COMMENT '所属文档 UUID',
    `position`          INT      NOT NULL COMMENT '在文档中的位置序号',
    `content`           TEXT     NOT NULL COMMENT '分段内容',
    `word_count`        INT      NOT NULL COMMENT '字数',
    `token_count`       INT      NOT NULL COMMENT 'Token 数',
    `hit_count`         INT      NOT NULL COMMENT '检索命中次数',
    `created_at`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '文档分段表';

-- 工具表
CREATE TABLE IF NOT EXISTS `tools`
(
    `id`                  CHAR(36)      NOT NULL COMMENT '业务表主键 UUID',
    `name`                VARCHAR(200)  NOT NULL COMMENT '工具名称',
    `description`         TEXT          NULL COMMENT '工具描述',
    `type`                VARCHAR(50)   NOT NULL COMMENT '工具类型: builtin/http_api/custom_function',
    `status`              VARCHAR(50)   NOT NULL COMMENT '状态: enabled/disabled/error',
    `config`              JSON          NULL COMMENT '工具配置（因类型而异）',
    `function_definition` JSON          NULL COMMENT 'Function Calling 定义（OpenAI 格式）',
    `call_count_7d`       INT           NOT NULL COMMENT '近7天调用次数',
    `success_rate`        DECIMAL(5, 2) NOT NULL COMMENT '成功率 %',
    `avg_latency`         INT           NOT NULL COMMENT '平均延迟 ms',
    `created_by`          VARCHAR(100)  NULL COMMENT '创建者',
    `created_at`          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`          DATETIME      NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_tools_name` (`name`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = '工具表';

-- Agent 表
CREATE TABLE IF NOT EXISTS `agents`
(
    `id`            CHAR(36)      NOT NULL COMMENT '业务表主键 UUID',
    `name`          VARCHAR(200)  NOT NULL COMMENT 'Agent 名称',
    `description`   TEXT          NULL COMMENT '描述',
    `type`          VARCHAR(50)   NOT NULL COMMENT '类型: conversation/tool/analysis/creative/workflow',
    `status`        VARCHAR(50)   NOT NULL COMMENT '状态: active/inactive/error/draft',
    `model_id`      CHAR(36)      NULL COMMENT '关联的模型 UUID',
    `config`        JSON          NULL COMMENT 'Agent 完整配置',
    `success_rate`  DECIMAL(5, 2) NOT NULL COMMENT '成功率 %',
    `call_count_7d` INT           NOT NULL COMMENT '近7天调用次数',
    `version`       VARCHAR(50)   NOT NULL COMMENT '当前版本号',
    `created_by`    VARCHAR(100)  NULL COMMENT '创建者',
    `created_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at`    DATETIME      NULL COMMENT '软删除时间，为空表示未删除',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = 'Agent 表';

-- Agent 版本表
CREATE TABLE IF NOT EXISTS `agent_versions`
(
    `id`           CHAR(36)     NOT NULL COMMENT '业务表主键 UUID',
    `agent_id`     CHAR(36)     NOT NULL COMMENT '所属 Agent UUID',
    `version`      VARCHAR(50)  NOT NULL COMMENT '版本号',
    `config`       JSON         NULL COMMENT '该版本的配置快照',
    `changelog`    VARCHAR(500) NULL COMMENT '变更说明',
    `is_current`   TINYINT(1)   NOT NULL COMMENT '是否为当前版本',
    `published_by` VARCHAR(100) NULL COMMENT '发布者',
    `published_at` DATETIME     NULL COMMENT '发布时间',
    `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci
    COMMENT = 'Agent 版本表';
